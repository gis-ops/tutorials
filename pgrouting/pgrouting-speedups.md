# pgRouting Performance Tuning Made Easy

> **Disclaimer**: This tutorial was developed on Mac OSX 10.15.6 and tested on Ubuntu 18.04 as well as Ubuntu 20.04. Windows compatibility cannot be guaranteed.

## Motivation

[pgRouting](https://pgrouting.org/), the popular routing extension for the open source RDBMS Postgres has been around for quite some time now, preceding most other open source routing engines.
And while its flexibility has often been praised, pgRouting's performance is usually not what it's been known for. In this tutorial however, we want to show you that 
the opposite is true: with the right tweaks and tricks, pgRouting can provide blazingly fast routing even on large road data sets!


## Prerequisites & Dependencies

- PostgreSQL instance with **PostGIS and pgRouting enabled**, we recommend [Kartoza](kartoza.com)'s [docker image]([Kartoza](https://github.com/kartoza/docker-postgis)) (see [this tutorial](https://gis-ops.com/postgrest-tutorial-installation-and-setup/))
- osmconvert ([installation instructions](https://wiki.openstreetmap.org/wiki/Osmconvert)): easily clip OSM files
- [osm2po](http://osm2po.de/): create pgRouting topology from raw OSM data

## Preprocessing the Data

For our example, we will be working with OpenStreetMap data for Northern California. Simply download the .osm file 


## Performance Tuning

### Baseline
In order to compare by how much we can speed up our queries, we first need a baseline route and see how long it takes pgRouting to compute it. For this,
we need a reasonably long route. Say we're in San Francisco and we want to drive all the way to Yosemite National Park. So we simply pick two coordinates
and – without any changes to our topology after importing it from the .sql file – calculate a route like this:

```sql
-- find he nearest vertex to the start longitude/latitude
WITH start AS (
  SELECT topo.source --could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    st_makepoint(-122.407546,37.784482),
  4326)
  LIMIT 1
),
-- find the nearest vertex to the destination longitude/latitude
destination AS (
  SELECT topo.source --could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    st_makepoint(-119.5847826,37.7446591),
  4326)
  LIMIT 1
)
-- use Dijsktra and join with the geometries
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

On my local machine, this query takes a staggering 22 seconds to compute. This is not surprising though, if we take a closer look at the dijkstra subquery: as the first argument, we provide the query for our edges table. Not only does this SELECT statement select the whole table with upwards of 3 million edges, it also computes the cost and the reverse cost _on the fly_ by measuring each edge's length. So the first and most obvious speed up is to set the cost to a fixed value, and boy are we lucky, because `osm2po` already did that for us! So we simply select the already existing `cost` and `reverse_cost` columns. Now our query looks as follows:

```sql
-- find he nearest vertex to the start longitude/latitude
WITH start AS (
  SELECT topo.source --could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    st_makepoint(-122.407546,37.784482),
  4326)
  LIMIT 1
),
-- find the nearest vertex to the destination longitude/latitude
destination AS (
  SELECT topo.source --could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    st_makepoint(-119.5847826,37.7446591),
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

This query takes 13 seconds on my machine, a 9 second speed up by *simply avoiding to calculate cost on the fly*. While this one is obvious, there's another change we can make to the edges sql that will make our query run significantly faster: considering that `pgr_dijkstra` looks at every single edge in the edges table, we can simply limit the amount of edges the algorithm looks at *by only selecting those edges that are actually relevant for our route*. We do this by selecting the bounding box of our start and destination points, expanding it by a fixed value (0.1 degrees in this case) and intersecting our edge geometries with the resulting rectangle, only keeping those within it. Our query now looks like this:

```sql
-- find he nearest vertex to the start longitude/latitude
WITH start AS (
  SELECT topo.source --could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    st_makepoint(-122.407546,37.784482),
  4326)
  LIMIT 1
),
-- find the nearest vertex to the destination longitude/latitude
destination AS (
  SELECT topo.source --could also be topo.target
  FROM norcal_2po_4pgr as topo
  ORDER BY topo.geom_way <-> ST_SetSRID(
    st_makepoint(-119.5847826,37.7446591),
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

This runs in about 5 seconds, another 8 seconds cut from our previous query. Now as far as the query goes, we have exhausted our repertoire, but there is still untapped potential in PostGIS indices: pgRouting does create indices on the `source`, `target` and `id` columns, but no spatial indices on the geometry column.

```sql
CREATE INDEX ON norcal_2po_4pgr USING gist(geom_way);
```

If we now run our last query again, we will notice that it has just gotten a lot faster again: on my machine, it runs **in an impressive 1.5 seconds**. And this isn't even everything PostGIS has to offer: as a last measure to tune pgRouting's performance, we can use PostGIS' [spatial clustering](https://postgis.net/workshops/postgis-intro/clusterindex.html), a method to further speed up accessing spatially correlated data. So we can additionally run the following line to cluster our edge data:

```sql
CLUSTER norcal_2po_4pgr USING norcal_2po_4pgr_geom_way_idx;
```

If we rerun our query, we'll see yet another speed up: I was able to cut it from 1.5 to 1.2 seconds. 

## Wrap up

Congratulations for completing the tutorial! You have successfully learned how to significantly speed up your pgRouting queries. While pgRouting may not be able to compete with other open source routing engines in terms of speed, this short tutorial has demonstrated that there is still plenty of leeway to make your routing queries much, much faster with only a few tweaks to the query and the way the edges are stored and retrieved using indexing and clustering techniques. In our example, the time to compute a 430 km long route was dropped from 22 seconds to 1.2 seconds, which represents an almost 2000% decrease. If you want to achieve even faster results, there are more general tips and tricks out there to tune your PostgreSQL instance, by e.g. have it use more of your machine's RAM (see [here](https://www.enterprisedb.com/postgres-tutorials/how-tune-postgresql-memory) for a short article).

Please feel free to get in touch with us at enquiry[at]gis-ops.com if you have any further questions, need support or have ideas for other tutorials on pgRouting!
