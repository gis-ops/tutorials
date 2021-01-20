# How to Guide Routing Algorithms Towards Pleasant Hiking

![Coastal Walk From Coogee to Bondi in Sydney](https://github.com/gis-ops/tutorials/raw/master/pgrouting/static/img/sydney-coastal-walk.jpg "Coastal Walk From Coogee to Bondi in Sydney")
*source: [https://www.sydneycoastwalks.com.au](https://www.sydneycoastwalks.com.au/)*

**Disclaimer**: This tutorial was developed on Mac OSX 10.15.6 and tested on Ubuntu 18.04 as well as Ubuntu 20.04.
Windows compatibility cannot be guaranteed.

"Dear routing service, please get me from A to B!". If you are sitting in a car or truck you would usually expect the fastest or shortest route and not care too much about the environment around you.
And this --in the majority of cases-- makes total sense. In logistics it's usually all about optimizing cost and time which is why common behaviour of proprietary routing engines such as [Google Maps](https://maps.google.com), [HERE Maps](https://wego.here.com/) or [TomTom](https://mydrive.tomtom.com) will tend to prefer motorways or primary roads as they are --at least in most countries-- the shortest and fastest connections between positions on the map. 
However, if you move away from motorized vehicles and think more about leisure and outdoor activities you may prefer scenic routes instead of walking alongside polluted and noisy main roads in metropolitans. 

In this small technical tutorial we want to demonstrate you how easy it is to adapt the behaviour of a shortest path algorithm consuming the topology with support of [pgRouting](https://pgrouting.org/) which sits on top of a relational database. With adapting we are referring to the ability change the equation of which route should be preferred as it is always about the least cost (it doesn't have to always be the shortest!). In a nutshell and algorithmitically speaking: if you want to prefer footways over primary roads, you can make this subset of roads "cheaper" to use - and by doing so guide the routing algorithm (we will be using Dijkstra's in this tutorial) to use them.

## Prerequisites & Dependencies

To implement and follow all steps of this tutorial it's required to set up [PostgreSQL](https://www.postgresql.org), [PostGIS](https://postgis.net) and [pgRouting](https://pgrouting.org). For this purpose we recommend to use a docker image provided by [Kartoza](https://github.com/kartoza/docker-postgis) Kartoza.
Additionally, we will require 3 additional command line tools, namely [osm2po](http://osm2po.de/), [osm2pgsql](https://osm2pgsql.org/) and [osmconvert](https://wiki.openstreetmap.org/wiki/Osmconvert) to prepare the data.

- You can use [this](https://github.com/gis-ops/tutorials/blob/postgrest-elevation-api/postgres/postgres_postgis_postgrest_installation.md) installation guide which will help you get the docker container up and running. Just make sure you specify `POSTGRES_MULTIPLE_EXTENSIONS=postgis,pgrouting` for the extensions in the arguments. Feel free to ignore the PostgREST steps as these will not be required. Also, it may be handy to add a shared volume for the files which will be produced in the course of this tutorial.

- *osmconvert* will be used to clip the OpenStreetMap file of [Australia](https://download.geofabrik.de/australia-oceania/australia.html) as we are merely interested in parts of Sydney in this tutorial (installation details can be found [here](https://wiki.openstreetmap.org/wiki/Osmconvert)).

- *osm2po* is used to create the topology from raw OpenStreetMap data which is not routable in its initial state. You can download it [here](http://osm2po.de/). To use this software, you will require `java` in your environment. If you want to skip this step, we will provide you with the processed topology SQL file later on in this tutorial.

- *osm2pgsql* will help us import the raw [OpenStreetMap](http://openstreetmap.org) data to our PostgreSQL database. We will require this data to update the cost of edges in the topology accordingly. Installation details can be found [here](https://github.com/openstreetmap/osm2pgsql#installing)

## Step 1 - Preparing the OpenStreetMap Data

First of all, please navigate to your working directory on your host machine and download the OSM data with:

```sh
wget https://download.geofabrik.de/australia-oceania/australia-latest.osm.pbf`
```

Using `osmconvert` we will use this data to clip a part of Sydney between [Coogee](https://en.wikipedia.org/wiki/Coogee,_New_South_Wales) and [Bondi](https://en.wikipedia.org/wiki/Bondi,_New_South_Wales) from it.

```sh
osmconvert australia-latest.osm.pbf -b=151.2463,-33.9274,151.2956,-33.8302 -o=sydney-coast.pbf
```

Alternatively, feel free to download the output of this step [here](https://github.com/gis-ops/tutorials/raw/master/pgrouting/static/data/sydney-coast.pbf).

## Step 2 - Preparing the Topology with osm2po & Importing OSM Data

As mentioned above, we will use *osm2po* to generate the topology from the OSM data we generated in the previous step. It is important to understand that OSM data is not routable in its pure form. The geniality of this software is that it isn't only a light-weight routing engine, it also processes the OSM data and outputs a SQL-file which can directly be imported to your *PostgreSQL* database and be used with *pgRouting*. For this tutorial our task is to make sure we output a topology including all highways in the area of interest as we will want to post-process these in the database.

![OpenStreetMap not Routable](https://github.com/gis-ops/tutorials/raw/master/pgrouting/static/img/osm2po-topology.png "OpenStreetMap data in its pure form is not routable")
*source: [osm2po.de](http://osm2po.de)*

Change your directory where the osm2po jar file is located. By default osm2po will not include OpenStreetMap highways with pedestrian or cycleway tags which is why we have to make some small changes to the `osm2po.config` file:

1. We want to process OSM data for these profiles, so change line 189 to `.default.wtr.finalMask = car,foot,bike`
2. Comment in **line 221** `.default.wtr.tag.highway.service` to **line 230** `.default.wtr.tag.railway.rail`

Afterwards run the following command:

```sh
java -Xmx512m -jar osm2po-core-[5.3.2]-signed.jar cmd=c prefix=syd your/path/to/sydney-coast.pbf
```

The prefix `syd` will produce a new folder in the directory you are currently in which will hold the generated files osm2po will output.


```sh
root@5d93dd759514:~/osm2po/syd# ls -la
total 3540
drwxr-xr-x 2 root root    4096 Jan 18 12:05 .
drwxr-xr-x 6 root root    4096 Jan 18 12:05 ..
-rw-r--r-- 1 root root    6461 Jan 18 12:05 jw_orphans.2po
-rw-r--r-- 1 root root  400334 Jan 18 12:05 jw_S040E150.2po
-rw-r--r-- 1 root root       1 Jan 18 12:05 jw_shared.2po
-rw-r--r-- 1 root root  111367 Jan 18 12:05 sv_all.2po
-rw-r--r-- 1 root root  533689 Jan 18 12:05 sw_all.2po
-rw-r--r-- 1 root root 2050861 Jan 18 12:05 syd_2po_4pgr.sql
-rw-r--r-- 1 root root    6848 Jan 18 12:05 syd_2po.log
-rw-r--r-- 1 root root     113 Jan 18 12:05 tm_info.2po
-rw-r--r-- 1 root root  214418 Jan 18 12:05 tn_S040E150.2po
-rw-r--r-- 1 root root    4681 Jan 18 12:05 tr_raw.2po
-rw-r--r-- 1 root root  259173 Jan 18 12:05 tw_raw.2po
```

The file we are interested in is `syd_2po_4pgr.sql` which consists of a set of columns including the source `osm_id`, `source` and `target`. Download the osm2po output [here](https://github.com/gis-ops/tutorials/raw/master/pgrouting/static/data/syd_2po_4pgr.sql) if you want to skip this step.

Last but not least we want to import the raw OSM-data to be able to join the topology with it's origin feature using the `osm_id` to determine what kind of [highway type](https://wiki.openstreetmap.org/wiki/Key:highway) (e.g. primary road, secondary road, footpath, cycleway..) we are dealing with.
 
The following command will generate a set of tables holding the OSM data (lines `planet_osm_line`, polygons `planet_osm_polygon` & points `planet_osm_point`) and all of their corresponding tags.

```sh
osm2pgsql --create --database [DB_NAME] --username [USER_NAME] --host [IP] --port [PORT] --password sydney-coast.pbf
```

## Step 3 - Guiding the Algorithm by Decreasing Edge Costs

Objective of this tutorial is to guide Dijkstra's algorithm along the coast of Sydney. The way we will be approaching this will bring in quite an imbalance into the network consisting of broken up roads (edges). However, for the purpose of this tutorial this will give you a basic understanding. Later, if and when you are tailoring your own topology, you can think about more sophisticated approaches to adapt the costs in a more delicate fashion, for instance using gravity-based ideas, where points of interest (points or even polygons) may attract the routing algorithm "their way". 

The choice being Sydney's coastal walk is quite convenient. There exist many roads you could walk on which are more or less parallel to the coastal footpaths, obviously getting you faster to the destination. The reason is straightforward: the distance is shorter (shortest path algorithms - who would have thought?). If you take a quick glimpse at what common routing services usually compute, such as [Google Maps](https://maps.google.com/), you will understand what we mean and why you may want to do some customizing.

![Google Maps from Coogee to Bondi](https://github.com/gis-ops/tutorials/raw/master/pgrouting/static/img/google-coogee-bondi.png "Google Maps from Coogee to Bondi")
*source: [maps.google.com](https://maps.google.com/)*

If you wanted to have full control over how the algorithm determines the least cost connection, you will have to start thinking about how to update the individual costs of the edges in your topology. The precious thing about OpenStreetMap is that the data is fairly structured and streets will feature a specific class. While a highway may be tagged as a "primary road", a path forbidden for motorized vehicles may be tagged was "footway". With this distinction we can start doing some fun things to the data.

In the most simple use case the cost of an edge could simply be the length of it. If we executed the following query using our topology generated by **osm2po** in our database and feeding it to **pgRouting**...

```sql
-- find he nearest vertex to the start longitude/latitude
WITH start AS ( 
  SELECT topo.source --could also be topo.target
  FROM syd_2po_4pgr as topo 
  ORDER BY topo.geom_way <-> ST_SetSRID(
    ST_GeomFromText('POINT (151.261360 -33.915983)'), 
  4326) 
  LIMIT 1
), 
-- find the nearest vertex to the destination longitude/latitude
destination AS (
  SELECT topo.source --could also be topo.target
  FROM syd_2po_4pgr as topo 
  ORDER BY topo.geom_way <-> ST_SetSRID(
    ST_GeomFromText('POINT (151.28241 -33.890510)'), 
  4326) 
  LIMIT 1
)
-- use Dijsktra and join with the geometries
SELECT ST_AsText(ST_Union(geom_way)) 
FROM pgr_dijkstra('
    SELECT id,
         source,
         target,
         ST_Length(ST_Transform(geom_way, 3857)) AS cost
        FROM syd_2po_4pgr',
    array(SELECT source FROM start),
    array(SELECT source FROM destination), 
    directed := false) AS di
JOIN   syd_2po_4pgr AS pt
  ON   di.edge = pt.id;
```

...your result should look like the following (which is very similar to what we got using Google Maps up top):

![pgRouting from Coogee to Bondi using the ST_Length](https://github.com/gis-ops/tutorials/raw/master/pgrouting/static/img/google-coogee-bondi.png "pgRouting from Coogee to Bondi using the ST_Length")

Well, it's the shortest path and we aren't satisfied with this result as we want to see the coast non-stop. This is where we will exploit the nature of the algorithm and guide it onto footpaths as much as we can (and guess what: the coastal tracks are). If you remember we imported the OpenStreetMap data at the beginning which we will now join to the topology allowing us to decrease the cost of the edges in question. To this end, we will add an auxiliary column `cost_updated` to our topology table (which will be consumed by pgRouting later on). Subsequently we will populate this column using a very straightforward logic. If the source osm_id of the record (edge) is tagged `footway, pedestrian, living_street, cycleway, track` or `steps` (in `planet_osm_line` or `planet_osm_polygon`), we will divide the length of the edge by 1000, otherwise the cost remains the metric length. The division ultimately makes the cost very cheap, i.e. the algorithm will be guided onto this subset of edges.  

```sql
-- Add aux cost column
ALTER TABLE syd_2po_4pgr ADD COLUMN "cost_updated" float;

-- The edge may either be in planet_osm_line
UPDATE syd_2po_4pgr as t
SET cost_updated = 
CASE WHEN
	(l.highway IN ('footway', 'pedestrian', 'living_street', 'cycleway', 'track', 'steps'))
THEN 
	ST_Length(ST_Transform(geom_way, 3857))/1000 
ELSE 
	ST_Length(ST_Transform(geom_way, 3857))
END
FROM planet_osm_line AS l
WHERE t.osm_id = l.osm_id;

-- Or in planet_osm_polygon
UPDATE syd_2po_4pgr as t
SET cost_updated = 
CASE WHEN
	(l.highway IN ('footway', 'pedestrian', 'living_street', 'cycleway', 'track', 'steps'))
THEN 
	ST_Length(ST_Transform(geom_way, 3857))/1000 
ELSE 
	ST_Length(ST_Transform(geom_way, 3857))
END
FROM planet_osm_polygon AS l
WHERE t.osm_id = l.osm_id;
```

Executing the query once again from above and instead of using `ST_Length(ST_Transform(geom_way, 3857)) AS cost` but `cost_updated AS cost`, your route will look something like this - enjoy the walk!

![pgRouting from Coogee to Bondi Guiding Dijkstra along the Coast](https://github.com/gis-ops/tutorials/raw/master/pgrouting/static/img/pgr_adapted_least_cost_path.png "pgRouting from Coogee to Bondi Guiding the Algorithm along the Coast")


### Wrap-up

Congratulations for completing this tutorial. By now you will have learnt how you can influence Dijkstra's routing algorithm by tinkering with edge costs. With this being a bold and simple tutorial we hope that you get the idea and understand the vast possibilities of different open source tools and frameworks in the global ecosystem of OpenStreetMap and routing. 

Please feel free to get in touch with us at **enquiry[at]gis-ops.com** if you have any further questions, need support or have ideas for other tutorials on pgRouting!
