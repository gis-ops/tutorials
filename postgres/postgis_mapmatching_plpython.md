# Quick and Easy Mapmatching in PostGIS 

<p align="center">
    <img width="500" src="https://raw.githubusercontent.com/gis-ops/tutorials/cb_postgis_mapmatching/postgres/img/gps_track_overview.png"/>
</p>

> **Disclaimer**: This tutorial was developed on Mac OSX 10.15.6 and tested on Ubuntu 18.04 as well as Ubuntu 20.04. Windows compatibility cannot be guaranteed.

## Motivation

Mapmatching \[_relating a set of recorded serial location points to edges of a graph network_\] is one of those problems in geoinformatics that you would initially think of as being easy to solve: how hard can it be, after all, to snap some points to a road network and create a coherent route along that network from the point series? You start by importing your `.gpx` files into your favorite spatially enabled RDBMS, dabble with `ST_Line_Locate_Point()`, `ST_Snap()`, `ST_Azimuth()` for a while before coming to the sobering conclusion that it's just not that simple. And it really comes down to just one single problem: GPS signals are messy, and they are messy in [so many ways](https://www.aboutcivil.org/sources-of-errors-in-gps.html): issues can arise from the satellites' orbits, the signals being reflected by objects, as well as errors caused by the receiver.

So what's the good news? Many people before you have tackled this problem, both in industry as well as in academia, and so there are readily packaged open source solutions at your fingertips. The not so good news is that there is no integrated solution within PostGIS (at least as of v3.2.1), and this is where this tutorial comes in: we will show you how to use the open source routing engine Valhalla with PostGIS to map match your GPS traces along an OSM road network. Specifically, we will make use of PL/Python, PostgreSQL's procedural language that lets you use the Python language within Postgres, as well as [pyvalhalla](https://pypi.org/project/pyvalhalla/), high level Valhalla bindings for Python.

## Map Matching in Valhalla: A Primer

There have been different approaches that aim to efficiently map match large amounts of GPS data to road networks, but the Hidden Markov Model (HMM) approach has been the most widely used in recent years. In short, it is a probabilistic model that determines the most likely edge sequence based on candidate nodes for each GPS measurement. Specifically, two probabilities determine which candidate node matches each measurement: (1) how close a GPS measurement is to a candidate node, and (2) how much the graph distance from a measurement's candidate node to a candidate node of the next measurement deviates from the Euclidean distance between the two measurements. The problem with this approach is that especially in dense urban areas, where there are many candidate nodes for each measurement, finding the edge sequence that maximizes path probability is expensive. Valhalla speeds this process up significantly by making clever use of Dijkstra's algorithm. If you're into the nitty-gritty details, you can find the exact implementation very well explained [here](https://github.com/valhalla/valhalla/blob/master/docs/meili/algorithms.md).


## Requirements

- PostgreSQL with **PostGIS enabled**, we can happily recommend [Kartoza](kartoza.com)'s [docker image]([Kartoza](https://github.com/kartoza/docker-postgis)) (see [this tutorial](https://gis-ops.com/postgrest-tutorial-installation-and-setup/))

## Set up PL/Python and pyvalhalla

In order to be able to use PL/Python, we need to enable it. With Kartoza's Docker image, this is as easy as executing the following statement in your database client:

```sql
CREATE EXTENSION plpython3u;
```
> **Note**: the 'u' at the end of `plpython3u` means untrusted, since PL/Python facilitates access to the file system from Postgres (among other dangerous shenanigans), so you might want to reconsider before using it in a production environment!


Next, we will need to make sure that we can access pyvalhalla, so we need to install it with pip (make sure to run this from within the PostGIS container if you're using one):

```sh
pip3 install pyvalhalla
```

In order to make sure we can use the Valhalla bindings from PL/Python, we quickly check Valhalla's version:

```sql
CREATE OR REPLACE FUNCTION valhalla_version()
RETURNS TEXT
AS
$$
    import valhalla
    return valhalla.__version__
$$ LANGUAGE plpython3u;


SELECT valhalla_version(); -- should return something like '3.0.2'
```

Finally, we need a graph that Valhalla can route on. For this, you can simply use our [Valhalla Docker image](https://hub.docker.com/r/gisops/valhalla). We have described how to use it [in another tutorial](https://gis-ops.com/valhalla-how-to-run-with-docker-on-ubuntu/), so we won't go into further detail here. For the sake of ease, we have also added the graph tiles needed to follow this tutorial [here](https://github.com/gis-ops/tutorials/tree/master/postgres/data), so don't worry if you're not familiar with Docker.


## Preprocessing the data

For this tutorial, we will be using a GPS track that I recorded while riding my bike in the beautiful city of Gijón in the Spanish autonomous region of Asturias. You can find the `.gpx` file [here]().

We can load the gpx file contents into PostGIS by using `ogr2ogr`, and make use of OGR's SQL dialect to only load the track points:

```sh
 ogr2ogr -f "PostgreSQL" PG:"host=localhost port=5432 dbname=gis user=<user> password=<password>" \
 		"./gijon_route.gpx" -nln bicycle_route -sql "SELECT * FROM track_points"

```

## Map Matching

Now we're getting to the fun part: We can now invoke Valhalla from PL/Python, so let's create a function that
does just that. For now, we're happy with simple map matching that just returns the line along the graph that we're feeding Valhalla.

```sql
CREATE OR REPLACE FUNCTION valhalla_map_match(
    IN locations varchar,
    OUT polyline varchar
) RETURNS varchar AS
$$
    import json
    from string import Template
    from valhalla import Actor, get_config
    
    config = get_config(tile_extract='/path/to/valhalla_tiles.tar', verbose=False)
    actor = Actor(config)
    query_template = Template('{"shape": $locations, "costing": "bicycle", "shape_match":"walk_or_snap", "filters":{"attributes":["shape"],"action":"include"}}')
    
    query_string = query_template.substitute(locations=locations)
    response = json.loads(actor.trace_attributes(query_string))
    
    return response["shape"]
$$ LANGUAGE plpython3u;
```

We create an `Actor` instance and refer to our valhalla tile extract, which needs to be accessible from inside the PostGIS docker container if you're using one. Then we can call our `trace_attributes` endpoint that does the map matching. The shape we're looking for can be found as an encoded polyline in the response object.

Now we just need our `bicycle_route` locations to be in JSON format, call our function with the stringified location JSON as input, and turn the polyline into a PostGIS geometry.

```sql
WITH locations AS (SELECT json_agg(t)::varchar AS locations
                   FROM (SELECT st_x(_ogr_geometry_) AS lon,
                                st_y(_ogr_geometry_) AS lat,
                                time
                         FROM bicycle_route) t),
     response AS (SELECT valhalla_map_match(locations) AS polyline FROM locations)

SELECT st_linefromencodedpolyline(polyline, 6)
FROM response;
```

> **Note**: we can use PostGIS' `st_linefromencodedpolyline()` function but it's important to call it with `nprecision=6`, which is the precision Valhalla uses.

The result looks pretty impressive! There are a few mistakes here and there, but they are mostly related to the quality of OSM data in Northern Spain, and with the fact that I might have taken some one way streets and ways that are only open to pedestrians (whoops). 
<p align="center">
<img width="400" alt="pgrouting" src="https://raw.githubusercontent.com/gis-ops/tutorials/cb_postgis_mapmatching/postgres/img/map_matched_qgis.gif">
</p>

Now, to take it a bit further, and to show what Valhalla is capable of, let's find out the road use types I rode on during my ride. The great thing about the `trace_attributes` endpoint is that we can retrieve a lot of useful information about the matched edges (and points!) by specifying them in the `"attributes"` key of our request. I simply choose `edge.use` (which gives us the edges' type of road use) and `edge.length` for its length (the default unit is kilometers). For a full list of attributes, check out [the documentation](https://github.com/valhalla/valhalla-docs/blob/master/map-matching/api-reference.md).

Our new function now looks like this:

```sql
CREATE OR REPLACE FUNCTION valhalla_trace_attributes(
    IN locations varchar,
    OUT length double precision,
    OUT use varchar
) RETURNS SETOF RECORD AS
$$
    import json
    from string import Template
    from valhalla import Actor, get_config

    config = get_config(tile_extract='/home/data/valhalla_tiles.tar', verbose=False)
    actor = Actor(config)
    query_template = Template('{"shape": $locations, "costing": "bicycle", "shape_match":"walk_or_snap", "filters":{"attributes":["edge.speed","edge.length", "edge.use"],"action":"include"}}')
    query_string = query_template.substitute(locations=locations)
    response = json.loads(actor.trace_attributes(query_string))

    return [(a["length"], a["use"]) for a in response["edges"]]
$$ LANGUAGE plpython3u;
```

And we call the function like this:

```sql
WITH locations AS (SELECT json_agg(t)::varchar AS locations
                   FROM (SELECT st_x(_ogr_geometry_) AS lon,
                                st_y(_ogr_geometry_) AS lat,
                                time
                         FROM bicycle_route) t),
     response AS (SELECT valhalla_trace_attributes(locations) AS record FROM locations)

SELECT SUM((record).length * 1000) as length, (record).use AS use FROM response GROUP BY use;
```

This produces the following result:

 length |         use         
--------|---------------------
   3349 | cycleway
   8696 | path
   8    | pedestrian_crossing
  19996 | road
   1039 | driveway

As you can see, I was forced to share the road with motorized vehicles a lot of the time, and most paths I used are actually cycleways, they just aren't categorized properly in OSM. Interestingly, the routes' total length fell within 50 m of the distance Strava estimated.

## Wrap up

Congratulations on completing this tutorial! You learned how to easily perform map matching on GPS tracks stored in PostGIS using the power of PL/Python and pyvalhalla. Now you're equipped to map match your own GPS traces and retrieve relevant information on the trips made. And this is just the beginning of what you can do with the power of PL/Python and pyvalhalla, so stay tuned for more tutorials!


And if you're in need of further support, feel free to reach out to us at enquiry[at]gis-ops.com! 
