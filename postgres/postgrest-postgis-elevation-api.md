# How to Build a Digital Elevation Model API with PostgREST, PostgreSQL and PostGIS

![Digital Elevation Model of the Dolomites](https://user-images.githubusercontent.com/10322094/71978844-96e0a800-321c-11ea-8df7-f6d8851248a0.png "Digital Elevation Model of the Dolomites")

**Disclaimer**: This tutorial was developed on Mac OSX 10.14.6 and tested on Ubuntu 18.04. 
Windows compatibility cannot be guaranteed.

In this tutorial you will learn how to build a Digital Elevation Model API with the powerful PostgREST library utilizing PostGIS under its hood which is able to return height information for arbitrary coordinates.

If you are interested in reading some further information on DEM's in general, we can recommend [Wikipedia](https://en.wikipedia.org/wiki/Digital_elevation_model) and [QGIS.org](https://docs.qgis.org/3.4/en/docs/gentle_gis_introduction/raster_data.html).

## Prerequisites

To follow this tutorial it's required to install the following:

### Install PostgreSQL + PostGIS
###### 9.3/2.4 or greater, either as a Docker container or within your host OS directly

If you are willing to run PostgreSQL via Docker we recommend to use [Kartoza's docker recipe](https://hub.docker.com/r/kartoza/postgis/) which comes bundled with PostGIS as an extension.

We will keep it simple and guide you through this tutorial using this image but the general steps are almost identical for a host installation.

Let's start our Docker Postgres container which we will name `postgrest_elevation` on port 5432 (or whichever port you prefer).

```sh
sudo docker run --name "postgrest_elevation" -p 5432:5432 -e POSTGRES_MULTIPLE_EXTENSIONS=postgis -d -t kartoza/postgis
```

We will have to configure Postgres to make sure it trusts our connections (this is merely for the tutorial and shouldn't be used in production this way).

```sh
sudo docker exec -it postgrest_elevation bash
```

Inside the container first of all install an editor, e.g. nano, and then navigate to the folder where the Postgres config lives.

```sh
apt-get update && apt-get install nano

# this could also be a different version and depends on your installation
cd /etc/postgresql/12/main/
```

In `pg_hba.conf` you will have to make a small change to the settings under `Database administrative login by Unix domain socket` (should be on line 85) from `peer` to `trust` and restart the Docker container afterwards.

```sh
sudo docker restart postgrest_elevation
```

Afterwards you should be able to execute the following command which will bring up the `psql` prompt.

```sh
sudo docker exec -it postgrest_elevation psql -U postgres
```

Within the prompt you will have to enable the PostGIS extension with:

```sh
postgres=# CREATE EXTENSION postgis;
postgres=# \q
```

If you are using Docker you will unfortunately have to install PostGIS in the again to be able to use `raster2pgsql` in a later stage:

```sh
sudo docker exec -it postgrest_elevation bash -c "apt-get update && apt-get install postgis"
```

### Installing PostgREST

To keep it simple, we suggest you follow the installation instructions on [postgrest.org](http://postgrest.org/en/v6.0/tutorials/tut0.html) which will depend on your operating system.

Once everything is installed you will be able to simply run PostgREST with:

```sh
postgrest
```

And if everything is working correctly it will print out its version and information about configuration.

## Step 1 - Creating our API Schema

We will require a schema, so let's bring up the `psql` prompt of our Docker container again (alternatively `psql -U postgres` if it's running on your host OS).

```sh
sudo docker exec -it postgrest_elevation psql -U postgres

psql (9.6.3)
Type "help" for help.

postgres=#
```

The first thing to do is to create an arbitrarily named schema for the database objects which will be exposed via the API.
Execute the following SQL statements inside the `psql` prompt:

```sh
CREATE SCHEMA api;
```

Next we should add a role to use for anonymous web requests. When a request hits the API, PostgREST will switch into this database role to run the queries.

```sh
CREATE ROLE web_anon NOLOGIN;

GRANT USAGE ON SCHEMA api TO web_anon;
```

Now, the `web_anon` role has permission to access functions in the api schema.

As the authors of PostgREST point out, it's actually good practice to create a dedicated role for connecting to the database, instead of using the highly privileged `postgres` role. To do that, name the role `authenticator` and also grant him the ability to switch to the `web_anon` role:

```sh
CREATE ROLE authenticator NOINHERIT LOGIN PASSWORD 'gisops';
GRANT web_anon TO authenticator;
```

PostgREST requires a configuration file to specify the database connection. Go ahead and create a file named `gisops-tutorial.conf` with the following information (remember to adapt the port and password if you have changed it in the earlier steps).

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

The PostgREST server is now ready to serve web requests. Surprise, there is nothing to serve yet. So let's move on and import the elevation data.

## Step 2 - Importing the Digital Elevation Model to our Database

In this tutorial you will be using a clipped region of the [EU DEM 1.1 Copernicus Dataset](https://land.copernicus.eu/imagery-in-situ/eu-dem) of the beautiful Dolomites in the Alps.
You can obviously download whatever data you are interested in and (optionally clip it with QGIS)[https://www.youtube.com/watch?v=XZBlYq6Fg4M]. 
This DEM is projected in [ETRS89-extended / LAEA Europe](https://epsg.io/3035) at 25 meters resolution with a vertical accuracy of +/- 7 meters RMSE and was published in 2016. You can find further metadata [here](https://land.copernicus.eu/imagery-in-situ/eu-dem/eu-dem-v1.1?tab=metadata).

Copy the TIF file into the root of your container first:

```sh
sudo docker cp dolomites.tif postgrest_elevation:/
```

Next, you will have to use `raster2pgsql` which you installed earlier via its CLI to import the DEM to the PostgreSQL database.
Depending on the size of the tif file you are importing this may take a while.

```
sudo docker exec -it postgrest_elevation bash -c "raster2pgsql -s 3035 -I -C -M -t "auto" dolomites.tif -F api.demelevation | psql -U postgres -d postgres"


Last but not least enter your `psql` prompt again to grant the `web_anon` user access to this table:

```sh
sudo docker exec -it postgrest_elevation psql -U postgres
postgres=# GRANT SELECT ON api.demelevation TO web_anon;
```

## Step 3 -  Returning Height Values via the API

Up next you will implement a simple [PL/pgSQL](https://en.wikipedia.org/wiki/PL/pgSQL) stored function which will return a height value on the fly. To keep it geospatial, the input payload will be modeled as a `GeoJSON` object. 

Let's bring back our `psql` prompt:

```sh
sudo docker exec -it postgrest_tut psql -U postgres
```

We will add a simple function to the `api` schema which consumes a single `GeoJSON Point` and returns a height value from the raster table in meters.


```sh
CREATE OR REPLACE FUNCTION api.get_height(Point json) 
RETURNS numeric AS $$
DECLARE Transformed_Point GEOMETRY;

BEGIN
    
    Transformed_Point := ST_Transform(ST_GeomFromGeoJSON(Point), 3035);

    RETURN(SELECT ROUND(
      CAST(
        (SELECT ST_Value(dem.rast, the_point.geom) AS height_in_meters
        FROM api.demelevation AS dem 
        CROSS JOIN (SELECT Transformed_Point As geom) AS the_point
        WHERE ST_Intersects(dem.rast, Transformed_Point))
        AS numeric
      ),2
    ));

END;

$$ LANGUAGE PLPGSQL;
```

This function `get_height` consumes a coordinate reference system specified (Geo-)JSON object which is named `Point` which in the first step is transformed into the same projection of the raster, namely `EPSG:3035`.
Afterwards this point (`the_point`) is cross joined with the digital elevation model where they both intersect.
To retrieve the value at this given intersection of the raster it makes use of the function `ST_Value()` which is casted to a numeric and rounded to 2 decimals. 

Hit enter to store the function in the schema. That's it, go ahead an give it a shot.

```sh
curl -X POST \
  http://localhost:3005/rpc/get_height \
  -H 'Content-Type: application/json' \
  -H 'Prefer: params=single-object' \
  -d '{"type": "Point","coordinates":[11.6438, 46.9381],"crs":{"type":"name","properties":{"name":"EPSG:4326"}}}'
```

By specifying the request header `Prefer: params=single-object`, we can let PostgREST know to intepret the entire POST body as the value of a single parameter. Quite handy for endpoints only expecting one single JSON object.
The GeoJSON has a crs specified (4326) which could basically be any projection of your choice.

The response will be a height value in meters.


### Wrap-up

Congratulations for completing this tutorial. By now you will have learnt how to set up and use the PostgREST web API to return height values from a digital elevation model.

Please feel free to get in touch with us if you have any further questions, need support or have ideas for other tutorials on PostgREST!