# How to Build a Powerful Spatial REST API with PostgREST, PostgreSQL and PostGIS

![GeoJSONs over New York](https://user-images.githubusercontent.com/10322094/69978653-219efa80-152d-11ea-80d8-710b087ff12c.png "GeoJSONs over New York")

**Disclaimer**: This tutorial was developed on Mac OSX 10.14.6 and tested on Ubuntu 18.04. 
Windows compatibility cannot be guaranteed.

In this tutorial you will learn how to build a spatial REST API with the powerful PostgREST library utilizing PostGIS under its hood - in mere minutes!

We will implement a range of different API endpoints with the following functionality

- Calculate the length of a LineString
- Calculate the area of a polygon
- Derive the intersection of two polygons

In case you have never heard of PostgREST before, let's have a look what look what the authors say:

*PostgREST is a standalone web server that turns your PostgreSQL database directly into a RESTful API. The structural constraints and permissions in the database determine the API endpoints and operations.*

It couldn't be easier.

## Prerequisites

To follow this tutorial, you will need to install the following:

### Install PostgreSQL + PostGIS
###### 9.3/2.4 or greater, either as a Docker container or within your host OS directly

If you are willing to run PostgreSQL with Docker we recommend you to use [Kartoza's docker recipe](https://hub.docker.com/r/kartoza/postgis/) which comes bundled with PostGIS as an extension.

We will keep it simple and guide you through this tutorial using this image but the general steps are almost identical for a host installation, no worries.

Let's start our docker Postgres container on port 5432 (or whichever port you prefer).

```sh
sudo docker run --name "postgrest_tut" -p 5432:5432 -e POSTGRES_MULTIPLE_EXTENSIONS=postgis -d -t kartoza/postgis
```

We will quickly have to configure Postgres to make sure it trusts our connections (this is merely for the tutorial and shouldn't be used in production this way).

```sh
sudo docker exec -it postgrest_tut bash
```

Inside the container first of all install an editor, e.g. nano, and then navigate to the folder where the Postgres config is living.

```sh
apt-get update && apt-get install nano

cd /etc/postgresql/12/main/
```

In `pg_hba.conf` you will have to make a small change to the settings under `Database administrative login by Unix domain socket` (should be on line 85) from `peer` to `trust` and restart the Docker container afterwards.

```sh
sudo docker restart postgrest_tut
```

Afterwards you should be able to execute the following command which will bring up the `psql` prompt.

```sh
sudo docker exec -it postgrest_tut psql -U postgres
```

Finally we will have to enable the PostGIS extension.

```sh
postgres=# CREATE EXTENSION postgis;
```

### Install PostgREST

To keep it simple, we suggest you follow the installation instructions on [postgrest.org](http://postgrest.org/en/v6.0/tutorials/tut0.html) which will depend on your operating system.

Once everything is installed properly you will be able to simply run PostgREST with

```sh
postgrest
```

And if everything is working correctly it will print out its version and information about configuration.

## Step 1 - Creating our Schema

For this tutorial we don't necessarily require a database because we will be implementing logic in Postgres as functions which will spatially compute information on the fly.
However we will require a schema, so let's bring up the `psql` prompt of our Docker container (alternatively `psql -U postgres` if it's running on your host OS).

```sh
sudo docker exec -it tutorial psql -U postgres

psql (9.6.3)
Type "help" for help.

postgres=#
```

The first thing to do is to create an arbitrary named schema for the database objects which will be exposed in the API.
Execute all SQL statements inside the `psql` prompt you started.

```sh
CREATE SCHEMA api;
```

Next we should add a role to use for anonymous web requests. When a request comes in, PostgREST will switch into this database role to run queries.

```sh
CREATE ROLE web_anon NOLOGIN;

GRANT USAGE ON SCHEMA api TO web_anon;
```

Now, the `web_anon` role has permission to access functions in the api schema!

As the authors of PostgREST point out, it's actually good practice to create a dedicated role for connecting to the database, instead of using the highly privileged `postgres` role. To do that, name the role `authenticator` and also grant him the ability to switch to the `web_anon` role:

```sh
CREATE ROLE authenticator NOINHERIT LOGIN PASSWORD 'gisops';
GRANT web_anon TO authenticator;
```

To make sure we use a suitable projection for our spatial calculations, we will use World Robinson's [EPSG:54030](https://epsg.io/54030).
Please add it to your database with:

```sh
INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 54030, 'ESRI', 54030, '+proj=robin +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs ', 'PROJCS["World_Robinson",GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Robinson"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["Central_Meridian",0],UNIT["Meter",1],AUTHORITY["EPSG","54030"]]');
``` 

Optionally, PostgREST can read a configuration file, e.g. to specify the database connection. Go ahead and create a file named `gisops-tutorial.conf` with the following information (remember to adapt the port and password if you have changed it in the earlier steps).

```sh
db-uri = "postgres://authenticator:gisops@localhost:5432/postgres"
db-schema = "api"
db-anon-role = "web_anon"
server-port = 3000
```

Now we are ready to start PostgREST.

```sh
postgrest gisops-tutorial.conf
# or ./postgrest gisops-tutorial.conf
```

You should be able to see something like this:

```sh
Listening on port 3000
Attempting to connect to the database...
Connection successful
```

The PostgREST server is now ready to serve web requests. But, guess what, there is nothing to serve yet. So let's move on and implement some spatial API endpoints!

## Step 2 - Let's return a simple GeoJSON Object

As mentioned earlier, we will implement stored procedures which will calculate spatial information on the fly. You as a user will have the ability to post `GeoJSON` objects as the payload to the API. For the sake of demonstration, we will start with a simple procedure which will return the payload without changing it.

Let's bring back our `psql` prompt:

```sh
sudo docker exec -it postgrest_tut psql -U postgres
```

We will add a simple function to the `api` schema. It takes a single `JSON` argument and just returns it again as-is.

```sh
CREATE OR REPLACE FUNCTION api.singlegeojsonparam(single_param json) RETURNS json

    LANGUAGE sql
    AS $_$
    SELECT single_param;

$_$;
```

Hit enter... That's it, let's try it out!

```sh
curl -X POST \
  http://localhost:3000/rpc/singlegeojsonparam \
  -H 'Content-Type: application/json' \
  -H 'Prefer: params=single-object' \
  -d '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[100.0,0.0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]},"properties":{"prop0":"value1","prop1":{"this":"that"}}},{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[100.0,0.0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]},"properties":{"prop0":"value2","prop1":{"this":"that"}}}]}'
```

If you're not too familiar with POST requests sending JSON data, this might be a little unfamiliar to you. The body is just one JSON object, and usually its keys would be interpreted as body parameters. However, by specifying the request header `Prefer: params=single-object`, we can let the backend know to intepret the entire POST body as the value of a single parameter. Quite handy for endpoints only expecting one single JSON object.

## Step 3 - Calculating the Length of a LineString

Now we can start with some more fun stuff. Let's go ahead and write a function that is able to calculate the length of a LineString provided in [EPSG:4326](https://spatialreference.org/ref/epsg/wgs-84/). Note, that the GeoJSON we are providing is in degrees, so we will have to transform to pseudo-mercator (or something similar). Additionally, we will cast it to `numeric` and after dividing it by 1.000 (to obtain a result in `kilometers`) we will round it to 2 decimals.

```sh
CREATE OR REPLACE FUNCTION api.calc_length(linestring json) RETURNS numeric AS $$

    SELECT ROUND(
      CAST(
        ST_Length(
          ST_Transform(
            ST_GeomFromGeoJSON(LineString), 54030
          )
        )/1000 AS numeric
      ),2
    )

$$ LANGUAGE SQL;
```

Easy enough. Let's give this a try.

```sh
curl -X POST \
  http://localhost:3000/rpc/calc_length \
  -H 'Content-Type: application/json' \
  -H 'Prefer: params=single-object' \
  -d '{"type":"LineString","coordinates":[[-101.744384,39.32155],[-101.552124,39.330048],[-101.403808,39.330048],[-101.332397,39.364032],[-101.041259,39.368279],[-100.975341,39.304549],[-100.914916,39.245016],[-100.843505,39.164141],[-100.805053,39.104488],[-100.491943,39.100226],[-100.437011,39.095962],[-100.338134,39.095962],[-100.195312,39.027718],[-100.008544,39.010647],[-99.865722,39.00211],[-99.684448,38.972221],[-99.51416,38.929502],[-99.382324,38.920955],[-99.321899,38.895308],[-99.113159,38.869651],[-99.0802,38.85682],[-98.822021,38.85682],[-98.448486,38.848264],[-98.206787,38.848264],[-98.020019,38.878204],[-97.635498,38.873928]],"crs":{"type":"name","properties":{"name":"EPSG:4326"}}}'
```

Voila! For our route through Kansas, USA it returns:

```sh
367.15
```

kilometers!


## Step 4 - Calculating the Area of a Polygon

By now you have most likely picked up the gist of how easy it is to implement custom functions. Similary to the LineString example we could also calculate the area of a polygon. Let's make this a little trickier and let the user send a `GeoJSON FeatureCollection`. To keep it a little simpler, the endpoint can only process the first feature of the `FeatureCollection`, so only one polygon.


```sh
CREATE OR REPLACE FUNCTION api.calc_area(featurecollection json) RETURNS numeric AS $$

    SELECT ROUND(
      CAST(
        ST_Area(
          ST_Transform(
            ST_GeomFromGeoJSON(
              featurecollection->'features'->0->'geometry'
            ), 54030
          )
        )/1000000 AS numeric
      ),2
    )

$$ LANGUAGE SQL;
```

Let's see the result:

```sh
curl -X POST \
  http://localhost:3000/rpc/calc_area \
  -H 'Content-Type: application/json' \
  -H 'Prefer: params=single-object' \
  -d '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-73.6962890625,41.02135510866602],[-73.8446044921875,41.253032440653186],[-74.168701171875,41.20758898181025],[-74.44335937499999,40.88444793903562],[-74.520263671875,40.60144147645398],[-74.2840576171875,40.53050177574321],[-73.8885498046875,40.63479884404164],[-72.83935546875,40.805493843894155],[-72.6800537109375,40.950862628132775],[-73.6962890625,41.02135510866602]]],"crs":{"type":"name","properties":{"name":"EPSG:4326"}}}}]}'
  ```

Our polygon covering part of New York is of size

```sh
6017.49
```

square kilometers. Easy.


## Step 5 - Calculating the Intersection of 2 Polygons

Last but not least let's implement one more function which will calculate the intersection of 2 polygons. The function by now should be self-explanatory. We just have to make sure we are returning a `GeoJSON` instead of a numeric value.


```sh
CREATE OR REPLACE FUNCTION api.calc_intersection(featurecollection json) RETURNS json AS $$

      SELECT ST_AsGeoJSON(
        ST_Intersection(
          ST_GeomFromGeoJSON(
            featurecollection->'features'->0->'geometry'
          ),
          ST_GeomFromGeoJSON(
            featurecollection->'features'->1->'geometry'
          )
        )
      )::json;

$$ LANGUAGE SQL;
```

We'll call this API with a feature collection comprising 2 polygons.


```sh
curl -X POST \
  http://localhost:3000/rpc/calc_intersection \
  -H 'Content-Type: application/json' \
  -H 'Prefer: params=single-object' \
  -d '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-73.6962890625,41.02135510866602],[-73.8446044921875,41.253032440653186],[-74.168701171875,41.20758898181025],[-74.44335937499999,40.88444793903562],[-74.520263671875,40.60144147645398],[-74.2840576171875,40.53050177574321],[-73.8885498046875,40.63479884404164],[-72.83935546875,40.805493843894155],[-72.6800537109375,40.950862628132775],[-73.6962890625,41.02135510866602]]],"crs":{"type":"name","properties":{"name":"EPSG:4326"}}}},{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-73.6798095703125,41.56203190200195],[-74.3280029296875,41.75492216766298],[-74.34997558593749,41.74262728637672],[-74.7894287109375,41.21998578493921],[-74.29504394531249,40.87614141141369],[-73.4326171875,40.91766362458114],[-73.6798095703125,41.56203190200195]]],"crs":{"type":"name","properties":{"name":"EPSG:4326"}}}}]}'
```

Which will respond with the GeoJSON intersection.

```sh
{
  "type": "Polygon",
  "coordinates": [
      [
          [
              -74.3926939034368,
              40.944056911669
          ],
          [
              -74.168701171875,
              41.2075889818102
          ],
          [
              -73.8446044921875,
              41.2530324406532
          ],
          [
              -73.6962890625,
              41.021355108666
          ],
          [
              -73.4662745356238,
              41.0053998532882
          ],
          [
              -73.4326171875,
              40.9176636245811
          ],
          [
              -74.2950439453125,
              40.8761414114137
          ],
          [
              -74.3926939034368,
              40.944056911669
          ]
      ]
  ]
}
```

### Wrap-up

Congratulations for completing this tutorial. By now you will have learnt how to set up and use the PostgREST web API for spatial purposes using PostGIS.

In comparison to other frameworks it's probably the most straight-forward web framework we have ever stumbled across. This obviously only touches the surface of what is possible, but if you are looking for a quick way to set up an API to handle spatial computations on-the-fly we can definitely recommend using PostgREST.

Please feel free to get in touch with us if you have any further questions, need support or have ideas for other tutorials on PostgREST!
