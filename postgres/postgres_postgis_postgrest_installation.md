### PostgREST tutorials

This tutorial is part of our PostgREST tutorial series:

- [PostgREST - Installation and Setup](https://gis-ops.com/postgrest-tutorial-installation-and-setup/)
- [PostgREST - Spatial API](https://gis-ops.com/postgrest-postgis-api-tutorial-in-5-minutes/)
- [PostgREST - DEM API](https://gis-ops.com/postgrest-postgis-api-serve-digital-elevation-models)

# PostgREST installation and setup

**Disclaimer**: This tutorial was developed on Mac OSX 10.14.6 and tested on Ubuntu 18.04.
Windows compatibility cannot be guaranteed.

In this tutorial you'll learn how to install and setup [PostgREST](https://github.com/PostgREST/postgrest), the RESTful API framework for any existing PostgreSQL database.

## Step 1 - Docker PostgreSQL & PostGIS setup

If you are willing to run PostgreSQL via Docker we recommend to use [Kartoza's docker recipe](https://hub.docker.com/r/kartoza/postgis/) which comes bundled with PostGIS as an extension.

We will keep it simple and guide you through this tutorial using this image but the general steps are almost identical for a host installation.

Create your Docker Postgres container named `postgrest_tut` on port 5432 (or whichever port you prefer).

```sh
sudo docker run --name "postgrest_tut" -p 5432:5432 -e POSTGRES_MULTIPLE_EXTENSIONS=postgis -d -t kartoza/postgis
```

You will have to configure Postgres to make sure it trusts connections (this is merely for the tutorial and shouldn't be used in production this way).

```sh
sudo docker exec -it postgrest_tut bash
```

Inside the container first of all install an editor, e.g. nano, and then navigate to the folder where the Postgres config lives.

```sh
apt-get update && apt-get install nano

# this could also be a different version and depends on your installation
cd /etc/postgresql/12/main/
```

In `pg_hba.conf` you will have to make a small change to the settings under `Database administrative login by Unix domain socket` from `peer` to `trust`. On lines 84 & 85, it should look like this:

```sh
# Database administrative login by Unix domain socket
local   all             postgres                                trust
```

Then restart the Docker container and bring up the `psql` prompt:

```sh
sudo docker restart postgrest_tut
sudo docker exec -it postgrest_tut psql -U postgres
```

Within the prompt you will have to enable the PostGIS extension with:

```sh
postgres=# CREATE EXTENSION postgis;
postgres=# \q
```

In some tutorials we make use of the `raster2pgsql` utility provided by PostGIS. However, that's not available in Kartoza's Docker image and only available in the PostGIS `apt-get` package. So you'll have to install it manually inside the Docker container:

```sh
sudo docker exec -it postgrest_tut bash -c "apt-get update && apt-get install postgis"
```

## Step 2 - PostgREST installation

To keep it simple, we suggest you follow the installation instructions on [postgrest.org](http://postgrest.org/en/v6.0/tutorials/tut0.html) which will depend on your operating system.

Once everything is installed you will be able to simply run PostgREST with:

```sh
postgrest
```

And if everything is working correctly it will print out its version and information about configuration.

## Step 3 - Create API Schema

Postgrest will require its own API schema, so bring up the `psql` prompt of our Docker container again (alternatively `psql -U postgres` if it's running on your host OS).

```sh
sudo docker exec -it postgrest_tut psql -U postgres

psql (9.6.3)
Type "help" for help.

postgres=#
```

Create an arbitrarily named schema for your database objects which will be exposed via the PostgREST API. Execute the following SQL statements inside the `psql` prompt:

```sql
CREATE SCHEMA api;
```

Next, you should add a role to use for anonymous web requests. When a request hits the API, PostgREST will switch into this database role to run the queries.

```sql
CREATE ROLE web_anon NOLOGIN;

GRANT USAGE ON SCHEMA api TO web_anon;
```

Now, the `web_anon` role has permission to access functions in the API schema.

As the authors of PostgREST point out, it's actually good practice to create a dedicated role for connecting to the database, instead of using the highly privileged `postgres` role. To do that, name the role `authenticator` and also grant this user the ability to switch to the `web_anon` role:

```sql
CREATE ROLE authenticator NOINHERIT LOGIN PASSWORD 'gisops';
GRANT web_anon TO authenticator;
```

We'll regularly use the World Robinson's [EPSG:54030](https://epsg.io/54030) projection to make sure we use a suitable projection for our spatial calculations. However, PostGIS misses that projections in its CRS table, so please add it to your database:

```sh
INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 54030, 'ESRI', 54030, '+proj=robin +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs ', 'PROJCS["World_Robinson",GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Robinson"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["Central_Meridian",0],UNIT["Meter",1],AUTHORITY["EPSG","54030"]]');
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

The PostgREST server is now ready to serve web requests.
