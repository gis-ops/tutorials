# Quick and Easy Mapmatching in PostGIS 

> **Disclaimer**: This tutorial was developed on Mac OSX 10.15.6 and tested on Ubuntu 18.04 as well as Ubuntu 20.04. Windows compatibility cannot be guaranteed.

## Motivation

Mapmatching \[_relating a set of recorded serial location points to edges of a graph network_\] is one of those problems in geoinformatics that you would initially think of as being easy to solve: how hard can it be, after all, to snap some points to a road network and create a coherent route along that network from the point series? You start by importing your `.gpx` files into your favorite spatially enabled RDBMS, dabble with `ST_Line_Locate_Point()`, `ST_Snap()`, `ST_Azimuth()` for a while before coming to the sobering conclusion that it's just not that simple. And it really comes down to just one single problem: GPS signals are messy, and they are messy in [so many ways](https://www.aboutcivil.org/sources-of-errors-in-gps.html): issues can arise from the satellites' orbits, the signals being reflected by objects, as well as errors caused by the receiver.

So what's the good news? Many people before you have tackled this problem, both in industry as well as in academia, and so there are readily packaged open source solutions at your fingertips. The not so good news is that there is no integrated solution within PostGIS (at least as of v3.2.1), and this is where this tutorial comes in: we will show you how to use the open source routing engine Valhalla with PostGIS to map match your GPS traces along an OSM road network. Specifically, we will make use of PL/Python, PostgreSQL's procedural language that lets you use the Python language within Postgres, as well as pyvalhalla, high level Valhalla bindings for Python.

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

Finally, we need a graph that Valhalla can route on. 

...


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
    
    config = get_config(tile_extract='/home/data/valhalla_tiles.tar', verbose=False)
    actor = Actor(config)
    query_template = Template('{"shape": $locations, "costing": "bicycle", "shape_match":"walk_or_snap", "filters":{"attributes":["shape"],"action":"include"}}')
    
    query_string = query_template.substitute(locations=locations)
    response = json.loads(actor.trace_attributes(query_string))
    
    return response["shape"]
$$ LANGUAGE plpython3u;
```

Now we just need our `bicycle_route` locations to be in JSON format, and call our function with the stringified location JSON as input:

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


## Wrap up

Congratulations on completing this tutorial! You learned how to easily perform map matching on GPS tracks stored in PostGIS using the power of PL/Python and pyvalhalla. And this is just the beginning, since PL/Python allows us to do so many more things with Valhalla that PostGIS/pgRouting aren't equipped with.
