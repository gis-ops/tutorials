# How to build a powerful Spatial REST API with PostgREST, PostgreSQL and PostGIS 

In this tutorial you will learn how to build a spatial REST API with the powerful PostgREST library utilizing PostGIS under its hood.
We will implement a range of different API endpoints which will feature the following functionality

- Calculate the length of a linestring
- Calculate the area of a polygon
- Derive the intersection of two polygons

In case you have never heard of PostgREST before, let's have a look what look what they say..

"PostgREST is a standalone web server that turns your PostgreSQL database directly into a RESTful API. The structural constraints and permissions in the database determine the API endpoints and operations."

It couldn't be easier. 
Without further ado let's get started!


## Prerequisites

To follow this tutorial, you will need to install the following:

### Install PostgreSQL + PostGIS (9.3/2.4 or greater, either as a Docker container or within your host OS directly)

If you are willing to run PostgreSQL with Docker we recommend you to use [kartoza's docker recipe](https://hub.docker.com/r/kartoza/postgis/) which comes directly bundled with PostGIS as an extension.
To this end we will keep it simple and guide you through this tutorial using this image but please feel free to alternatively install PostgreSQL and PostGIS on your host OS.

```sh
sudo docker run --name "postgrest_tut" -p 5432:5432 -e POSTGRES_MULTIPLE_EXTENSIONS=postgis -d -t kartoza/postgis
```

We will quickly have to configure postgres to make sure it trusts our connections (this is merely for the tutorial and shouldn't be used in production this way).

```sh
sudo docker exec -it postgrest_tut bash
```

Inside the container first of all install an editor, e.g. nano, and then navigate to the folder where the postgres config is sitting. 

```sh
apt-get update && apt-get install nano
cd /etc/postgresql/11/main/
```

In `pg_hba.conf` you will have to make a small change to the settings under `Database administrative login by Unix domain socket` (should be on line 85) from `peer` to `trust` and restart the Docker container afterwards.

```sh
sudo docker restart postgrest_tut
```

Afterwards you should be able to execute the following command which will bring up the `psql prompt`.

```sh
sudo docker exec -it postgrest_tut psql -U postgres
```

Finally we will have to enable the PostGIS extension.

```sh
postgres=# CREATE EXTENSION postgis;
```

Done! Let's move on.

### Install PostgREST 

To keep it simple, we suggest you follow the installation instructions on [postgrest.org](http://postgrest.org/en/v6.0/tutorials/tut0.html) which will depend on your operating system).

Once everything is installed you will be able to simply run postgrest with

```sh
postgrest
```

And if everything is working correctly it will print out its version and information about configuration.


## Step 1 - Creating our Schema

We don't neccessarily require a database because we will be implementing logic in PostgreSQL functions which will spatially compute information on the fly.
However we will require a schema, so let's log in to the the psql prompt of the docker container (alternatively `psql -U postgres` if it's running on your host OS)


```sh
sudo docker exec -it tutorial psql -U postgres
```


## Step 2 - Let's return a simple GeoJSON Object

## Step 2 - Calculating the length of a LineString

## Step 3 - Calculating the area of a Polygon

## Step 4 - Calculating the area intersection of 2 Polygons



### Wrap-up

bla






