# How to Influence Routing Algorithms for Pleasant Hiking

![Coastal Walk From Coogee to Bondi in Sydney](https://user-images.githubusercontent.com/10322094/71978844-96e0a800-321c-11ea-8df7-f6d8851248a0.png "Coastal Walk From Coogee to Bondi in Sydney")

**Disclaimer**: This tutorial was developed on Mac OSX 10.15.6 and tested on Ubuntu 18.04.
Windows compatibility cannot be guaranteed.

"Dear routing service, please get me from A to B!". In this situation, if you are sitting in a car or truck, you would usually expect the fastest or shortest route and not care too much about the environment.
And this makes total sense. In logistics it's usually all about optimizing cost and time which is why common behaviour of proprietary routing engines such as Google Maps, HERE Maps or TomTom will tend to prefer motorways or primary roads as they are --at least in most countries-- the shortest and fastest connections between points. 
However, if you move away from motorized vehicles and think more about leisure and outdoor activities you may prefer scenic routes instead of walking alongside polluted and noisy main roads in cities. In this small technical tutorial we want to demonstrate you how easy it is to adapt the behaviour of a shortest path algorithm consuming the topology with support of [pgRouting](https://pgrouting.org/) which sits on top of relational databases. With adapting we are referring to the ability change the equation of which route should be preferred as it is always about the cost. In a nutshell: if you want to prefer footways over primary roads, you cn make them "cheaper" and by doing so guide the routing algorithm to use them.

## Prerequisites

To implement and follow all steps of this tutorial it's required to set up [PostgreSQL](https://www.postgresql.org/), [PostGIS](https://postgis.net/) and [pgRouting](https://pgrouting.org/) and for that purpose we recommend to use a docker image provided by [Kartoza](https://github.com/kartoza/docker-postgis) Kartoza.
Additionally, we will require 3 additional command line tools, namely [osm2po](http://osm2po.de/), [osm2pgsql](https://osm2pgsql.org/) and [osmconvert](https://wiki.openstreetmap.org/wiki/Osmconvert).

- You can use [this](https://github.com/gis-ops/tutorials/blob/postgrest-elevation-api/postgres/postgres_postgis_postgrest_installation.md) installation guide which will help you get the docker container up and running. Just make sure you specify `POSTGRES_MULTIPLE_EXTENSIONS=postgis,pgrouting` for the extensions in the arguments. Feel free to ignore the PostgREST steps within as these will not be required. Also, it may be handy to add a shared volume for the files which will be produced in the course of this tutorial.

- osmconvert will be used to clip the [Australia](https://download.geofabrik.de/australia-oceania/australia.html) OpenStreetMap file as we are merely interested in parts of Sydney in this tutorial (installation details can be found [here](https://wiki.openstreetmap.org/wiki/Osmconvert)).

- *osm2po* is used to create the topology from raw OpenStreetMap data which is not routable in its initial state, you can download it [here](http://osm2po.de/). You will require `java` to run this program. If you want to skip this step, we will provide you with the processed topology file later on in this tutorial.

- *osm2pgsql* will help us import the raw [OpenStreetMap](http://openstreetmap.org) data to our PostgreSQL database. We will require this data to update the cost of edges in the topology accordingly. Installation details can be found [here](https://github.com/openstreetmap/osm2pgsql#installing)



## Step 1 - Preparing the OSM data

Please navigate to your working directory on your host and fetch the OSM data with:

```sh
wget https://download.geofabrik.de/australia-oceania/australia-latest.osm.pbf`
```

Using `osmconvert` we will use this data to clip a part of Sydney between [Coogee](https://en.wikipedia.org/wiki/Coogee,_New_South_Wales) and [Bondi](https://en.wikipedia.org/wiki/Bondi,_New_South_Wales) from it (feel free to download the output of this step [here](path_to_download):

```sh
osmconvert australia-latest.osm.pbf -b=151.2463,-33.9274,151.2956,-33.8302 -o=sydney-coast.pbf
```


## Step 2 - Preparing the Topology with osm2po & Importing OSM data


As mentioned above, we will use *osm2po* to generate the topology from the OSM data we just generated. It is important to understand that OSM data is not routable in its pure form. The geniality of this software is that it isn't only a light-weight routing engine, it also processes the OSM data and outputs a SQL-file which can directly be imported to *PostgreSQL* and be used with *pgRouting*. For this tutorial our task is to make sure we output a topology including all highways in the area of interest as we will want to post-process these in the database directly.

![](path_to_image)
*source: [osm2po.de](http://osm2po.de)*

Change your directory where the osm2po jar file is located. By default osm2po will not include OpenStreetMap highways with pedestrian or cycleway tags which is why we have to make some small changes to the `osm2po.config` file:

1. We want to process OSM data for these profiles, so change line 189 to `.default.wtr.finalMask = car,foot,bike`
2. Comment in line 221 `.default.wtr.tag.highway.service` to line 230 `.default.wtr.tag.railway.rail`

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

The file we are interested in is `syd_2po_4pgr.sql` which consists of a set of columns including the source `osm_id`, `source` and `target`. Download the osm2po output [here](link_to_data) if you want to skip this step.

Last but not least we want to import the raw OSM-data to be able to join the topology with it's source using the `osm_id` to determine what kind of [highway type](https://wiki.openstreetmap.org/wiki/Key:highway) (e.g. primary road, secondary road, footpath, cycleway..) we are dealing with.
 
The following command will generate a set of tables holding the OSM data (lines `planet_osm_line`, polygons `planet_osm_polygon` & points `planet_osm_point`) and all of their corresponding tags.

```sh
osm2pgsql --create --database [DB_NAME] --username [USER_NAME] --host [IP] --port [PORT] --password sydney-coast.pbf
```


## Step 3 - Updating the Edge Weights





## Step 4 - Find Routes!



### Wrap-up

Congratulations for completing this tutorial. By now you will have learnt how to set up and use the PostgREST web API to return height values from a digital elevation model.

Please feel free to get in touch with us at **enquiry[at]gis-ops.com** if you have any further questions, need support or have ideas for other tutorials on PostgREST!
