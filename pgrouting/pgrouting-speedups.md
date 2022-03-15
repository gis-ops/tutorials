# pgRouting Performance Tuning Made Easy
<img width="750" alt="pgrouting" src="https://user-images.githubusercontent.com/10322094/158249250-52f0d7fe-3482-402b-80aa-42af10e42688.png">

> **Disclaimer**: This tutorial was developed on Mac OSX 10.15.6 and tested on Ubuntu 18.04 as well as Ubuntu 20.04. Windows compatibility cannot be guaranteed.

## Motivation

[pgRouting](https://pgrouting.org/), the popular routing extension for the open source RDBMS PostgreSQL has been around for quite some time now, preceding most other open source routing engines. And while its flexibility has often been praised, pgRouting's performance is usually not what it's been known for. In this tutorial however, we want to show you that the opposite is true: with the right tweaks and tricks, pgRouting can provide blazingly fast routing even on large road data sets.


## Prerequisites & Dependencies

- PostgreSQL with **PostGIS and pgRouting enabled**, we can happily recommend [Kartoza](kartoza.com)'s [docker image]([Kartoza](https://github.com/kartoza/docker-postgis)) (see [this tutorial](https://gis-ops.com/postgrest-tutorial-installation-and-setup/))
- [osm2po](http://osm2po.de/): create pgRouting topology from raw OSM data

## Preprocessing the Data

For our example, we will be working with OpenStreetMap data for Northern California which will produce approximately 3M edges in total. Simply download the OSM file from [Geofabrik](https://www.geofabrik.de) by running the following command:

```sh
wget https://download.geofabrik.de/north-america/us/california/norcal-latest.osm.pbf
```

As mentioned above, we will use *osm2po* to generate the topology from the OSM data we generated in the previous step. It is important to understand that OSM data is not routable in its raw form. The geniality of this software is that it isn't only a light-weight routing engine, it also processes the OSM data and outputs a SQL file which can directly be imported to your PostgreSQL database and be used with **pgRouting**. For this tutorial our task is to make sure we output a topology including all highways in the area of interest as we will want to post-process these in the database.

Change your directory to where the osm2po jar file resides. By default osm2po will not include OpenStreetMap highways with pedestrian or cycleway tags which is why we have to make some small changes to the `osm2po.config` file:

1. We want to process OSM data for these profiles, hence change **line 190** to `wtr.finalMask = car,foot,bike`
2. Uncomment **lines 221** `.default.wtr.tag.highway.service` **to line 230** `.default.wtr.tag.railway.rail`

Additionally, we want to make sure the topology is produced which can be directly consumed by pgRouting - you will have to uncomment line 341 (`postp.0.class = de.cm.osm2po.plugins.postp.PgRoutingWriter`) if you are running version 5.1 or greater.

Afterwards run the following command:

```sh
java -Xmx1024m -jar osm2po-core-[5.5.2]-signed.jar cmd=c prefix=norcql your/path/to/norcal-latest.osm.pbf  # replace [5.5.2] with your osm2po version
```

The prefix `norcal` will produce a new folder in the directory you are currently in which will hold the generated files osm2po will output.
```sh
ls -l
total 2546048
-rw-r--r-- 1 chris chris   38798974 14. Mär 09:14 jw_N030W120.2po
-rw-r--r-- 1 chris chris  214118403 14. Mär 09:14 jw_N030W130.2po
-rw-r--r-- 1 chris chris      53721 14. Mär 09:14 jw_N040W120.2po
-rw-r--r-- 1 chris chris   58138934 14. Mär 09:14 jw_N040W130.2po
-rw-r--r-- 1 chris chris          1 14. Mär 09:14 jw_orphans.2po
-rw-r--r-- 1 chris chris     995562 14. Mär 09:14 jw_shared.2po
-rw-r--r-- 1 chris chris 1321783837 14. Mär 09:14 norcal_2po_4pgr.sql
-rw-r--r-- 1 chris chris      27553 14. Mär 09:14 norcal_2po.log
-rw-r--r-- 1 chris chris   54070678 14. Mär 09:14 sv_all.2po
-rw-r--r-- 1 chris chris  377289006 14. Mär 09:14 sw_all.2po
-rw-r--r-- 1 chris chris        248 14. Mär 09:14 tm_info.2po
-rw-r--r-- 1 chris chris   65383763 14. Mär 09:14 tn_N030W120.2po
-rw-r--r-- 1 chris chris  193399352 14. Mär 09:14 tn_N030W130.2po
-rw-r--r-- 1 chris chris   16483649 14. Mär 09:14 tn_N040W120.2po
-rw-r--r-- 1 chris chris   83424705 14. Mär 09:14 tn_N040W130.2po
-rw-r--r-- 1 chris chris     697558 14. Mär 09:13 tr_raw.2po
-rw-r--r-- 1 chris chris  182430743 14. Mär 09:13 tw_raw.2po

```

The file we are interested in is `norcal_2po_4pgr.sql`, which consists of a set of columns including the source `osm_id`, `source` and `target`. Import this data with `psql`.

```sh
psql -h [IP] -U [USER_NAME] -d [DB_NAME] -q -f norcal_2po_4pgr.sql
```

And that's all we need for the most basic setup to get started with pgRouting. Now, we can start writing our SQL queries.

## Performance Tuning

### Baseline Route
In order to compare by how much we can speed up our queries, we first need a reasonably long baseline route and see how long it takes pgRouting to compute it. Let's assume we are in San Francisco and we want to drive all the way to Yosemite National Park which is a ~430km/265mi drive. Let's choose 2 coordinates and hard code them into our query:

```sql
-- find the nearest vertex to the start longitude/latitude in San Francisco
WITH start AS (
  SELECT topo.source -- could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    ST_MakePoint(-122.407546,37.784482),
  4326)
  LIMIT 1
),
-- find the nearest vertex to the destination longitude/latitude in Yosemite National Park
destination AS (
  SELECT topo.source --could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    ST_MakePoint(-119.5847826,37.7446591),
  4326)
  LIMIT 1
)
-- use pgRoutings's Dijsktra and afterwards join with the geometries
SELECT ST_Union(geom_way) as geom
FROM pgr_dijkstra('
    SELECT id,
         source,
         target,
         ST_Length(ST_Transform(geom_way, 3857)) AS cost,
         ST_Length(ST_Transform(geom_way, 3857)) AS reverse_cost
        FROM norcal_2po_4pgr',
    array(SELECT source FROM start),
    array(SELECT source FROM destination),
    directed := true) AS di
JOIN   norcal_2po_4pgr AS pt
  ON   di.edge = pt.id;
```

On my local machine with 4 cores each clocked at 2.2ghz (Intel® Core™ i5) and 16 GB of memory, this route takes a staggering something between 30 and 40 seconds to compute. This is not surprising though, if we take a closer look at what's happening in the query: we determine the nearest vertice ids by means of spatial queries, run the dijkstra algorithm with these two ids in the preceding CTE query, and join the resulting path sequence back to the edge table to obtain the final geometry. And as if that wasn't plenty of computing to handle, take a closer look at the first argument of `pgr_dijkstra` where we provide the query for our edges table. Not only does this SELECT statement select the whole table with upwards of 3 million edges, it also computes the cost and the reverse cost _on the fly_ by measuring each edge's metric length. All these costly steps give us plenty of opportunity to start speeding things up.

### Speed Up 1: Precompute Costs 

The first and most obvious speed up is to precompute the cost value. We are lucky here as `osm2po` already did that for us. Instead of computing it on the fly we simply select the already existing `cost` and `reverse_cost` columns. Now our query looks as follows:

```sql
-- find the nearest vertex to the start longitude/latitude in San Francisco
WITH start AS (
  SELECT topo.source -- could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    ST_MakePoint(-122.407546,37.784482),
  4326)
  LIMIT 1
),
-- find the nearest vertex to the destination longitude/latitude in Yosemite National Park
destination AS (
  SELECT topo.source --could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    ST_MakePoint(-119.5847826,37.7446591),
  4326)
  LIMIT 1
)
-- use Dijsktra and join with the geometries
SELECT ST_Union(geom_way) as geom
FROM pgr_dijkstra('
    SELECT id,
         source,
         target,
        cost,
        reverse_cost
        FROM norcal_2po_4pgr',
    array(SELECT source FROM start),
    array(SELECT source FROM destination),
    directed := true) AS di
JOIN   norcal_2po_4pgr AS pt
  ON   di.edge = pt.id;
```

This query takes approximately 12 seconds on my machine, a more than double speed up by *simply avoiding to calculate cost on the fly*.

### Speed Up 2: Limit Edges Table with Bounding Box  

There's another change we can make to the edges sql that will make our query run significantly faster: considering that `pgr_dijkstra` looks at every single edge in the edges table, we can simply limit the amount of edges the algorithm looks at *by only selecting those edges that are actually relevant for our route*. We do this by selecting the bounding box of our start and destination points, expanding it by a fixed value (0.1 degrees in this case) and intersecting our edge geometries with the resulting rectangle, only keeping those within it. Our query now looks like this:

```sql
-- find the nearest vertex to the start longitude/latitude in San Francisco
WITH start AS (
  SELECT topo.source -- could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    ST_MakePoint(-122.407546,37.784482),
  4326)
  LIMIT 1
),
-- find the nearest vertex to the destination longitude/latitude in Yosemite National Park
destination AS (
  SELECT topo.source --could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    ST_MakePoint(-119.5847826,37.7446591),
  4326)
  LIMIT 1
)
-- use Dijsktra and join with the geometries
SELECT ST_Union(geom_way) as geom
FROM pgr_dijkstra('
    SELECT id,
         source,
         target,
        cost,
        reverse_cost
        FROM norcal_2po_4pgr as e,
    (SELECT ST_Expand(ST_Extent(geom_way),0.1) as box FROM norcal_2po_4pgr as b
        WHERE b.source = '|| (SELECT source FROM start) ||'
        OR b.source = ' || (SELECT source FROM destination) || ') as box WHERE e.geom_way && box.box'
    ,
    array(SELECT source FROM start),
    array(SELECT source FROM destination),
    directed := true) AS di
JOIN   norcal_2po_4pgr AS pt
  ON   di.edge = pt.id;
```

This runs in about 5 seconds, another 7 seconds cut from our previous query!

### Speed Ups 3 & 4: Spatial Indices and Clusters

Now as far as the query goes, we have exhausted our repertoire, but there is still untapped potential in PostGIS indices: PostgreSQL does create indices on the `source`, `target` and `id` columns when importing the dump, but no spatial indices on the geometry column. We can create one ourselves by running the following line:

```sql
CREATE INDEX ON norcal_2po_4pgr USING gist(geom_way);
```

If we now run our last query again, we will notice that it has just gotten a lot faster again: on my machine, it runs **in an impressive 1.5 seconds**. And this isn't even everything PostGIS has to offer: as a last measure to tune pgRouting's performance, we can use PostGIS' [spatial clustering](https://postgis.net/workshops/postgis-intro/clusterindex.html), a method to further speed up accessing spatially correlated data. So we can additionally run the following line to cluster our edge data:

```sql
CLUSTER norcal_2po_4pgr USING norcal_2po_4pgr_geom_way_idx;
```

If we rerun our query, we'll see yet another speed up: I was able to cut it from 1.5 to 1.2 seconds. Note that the last two speedups will only make our query faster because we use spatial functions to determine the nearest start and end vertices, and to only select the relevant edges in the Dijkstra traversal. If you only run a pure Dijkstra without any additional table expressions, neither a spatial index nor a clustered spatial index will give you any benefit. 

## Wrap up

Congratulations for completing the tutorial! You have successfully learned how to significantly speed up your pgRouting queries. While pgRouting may not be able to compete with other open source routing engines in terms of speed, this short tutorial has demonstrated that there is still plenty of leeway to make your routing queries much, much faster with only a few tweaks to the query and the way the edges are stored and retrieved using indexing and clustering techniques. In our example, the time to compute a 430 km long route was dropped from 22 seconds to 1.2 seconds, which represents an almost 2000% decrease. If you want to achieve even faster results, there are more general tips and tricks out there to tune your PostgreSQL instance, by e.g. have it use more of your machine's RAM (see [here](https://www.enterprisedb.com/postgres-tutorials/how-tune-postgresql-memory) for a short article).

Please feel free to get in touch with us at enquiry[at]gis-ops.com if you have any further questions, need support or have ideas for further tutorials on pgRouting and other topics!
