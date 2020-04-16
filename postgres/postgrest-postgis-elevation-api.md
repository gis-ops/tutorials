### PostgREST tutorials

This tutorial is part of our PostgREST tutorial series:

- [PostgREST - Installation and Setup](https://gis-ops.com/postgrest-tutorial-installation-and-setup/)
- [PostgREST - Spatial API](https://gis-ops.com/postgrest-postgis-api-tutorial-geospatial-api-in-5-minutes/)
- [PostgREST - DEM API](https://gis-ops.com/postgrest-postgis-api-tutorial-serve-digital-elevation-models/)

# How to Build a Digital Elevation Model API with PostgREST, PostgreSQL and PostGIS

![Digital Elevation Model of the Dolomites](https://user-images.githubusercontent.com/10322094/71978844-96e0a800-321c-11ea-8df7-f6d8851248a0.png "Digital Elevation Model of the Dolomites")

**Disclaimer**: This tutorial was developed on Mac OSX 10.14.6 and tested on Ubuntu 18.04.
Windows compatibility cannot be guaranteed.

In this tutorial you will learn how to build a Digital Elevation Model API with the powerful PostgREST library utilizing PostGIS under its hood which is able to return height information for arbitrary coordinates.

If you are interested in reading some further information on DEM's in general, we can recommend [Wikipedia](https://en.wikipedia.org/wiki/Digital_elevation_model) and [QGIS.org](https://docs.qgis.org/3.4/en/docs/gentle_gis_introduction/raster_data.html).

## Prerequisites

To implement all steps of this tutorial it's required to install PostgreSQL, PostGIS and PostgREST.
You can use the following installation guide which will help you get a docker container up and running which PostgREST will use in the subsequent steps.

### [Installing and Setting up PostgreSQL, PostGIS and PostgREST](https://github.com/gis-ops/tutorials/blob/postgrest-elevation-api/postgres/postgres_postgis_postgrest_installation.md)

## Step 1 - Importing the Digital Elevation Model to our Database

In this tutorial you will be using a clipped region of the [EU DEM 1.1 Copernicus Dataset](https://land.copernicus.eu/imagery-in-situ/eu-dem) of the beautiful Dolomites in the Alps. You can obviously download whatever data you are interested in and [optionally clip it with QGIS](https://www.youtube.com/watch?v=XZBlYq6Fg4M).
This DEM is projected in [ETRS89-extended / LAEA Europe](https://epsg.io/3035) at 25 meters resolution with a vertical accuracy of +/- 7 meters RMSE and was published in 2016. You can find further metadata on the [Copernicus pages](https://land.copernicus.eu/imagery-in-situ/eu-dem/eu-dem-v1.1?tab=metadata).

First you'll have to download the appropriate GeoTIFF file from the [Copernicus Download site](https://land.copernicus.eu/imagery-in-situ/eu-dem/eu-dem-v1.1?tab=download). Note, that downloading data requires a registration at the Copernicus system.

After downloading a DEM, copy the GeoTIFF into the root of your PostGIS container first:

```sh
sudo docker cp dolomites.tif postgrest_tut:/
```

Next, you will have to use `raster2pgsql` (ships with Kartoza's Docker image) to import the DEM to the PostgreSQL database. Depending on the size of the GeoTIFF file you are importing this may take a while.

```sh
sudo docker exec -it postgrest_tut bash -c 'raster2pgsql -s 3035 -I -C -M -t "auto" dolomites.tif -F api.demelevation | psql -U postgres -d postgres'
```

Finally enter your `psql` prompt again to grant the `web_anon` user access to this table:

```sh
sudo docker exec -it postgrest_tut psql -U postgres

postgres=# GRANT SELECT ON api.demelevation TO web_anon;
```

In case you encounter an error while importing the raster file à la

```bash
type raster does not exist
```

you can try to execute some of the scripts located in `/usr/share/postgresql/12/contrib/postgis-3.0/`. As far as we know, executing `rtpostgis.sql` should be enough:

```sql
sudo docker exec -it postgrest_tut bash
psql -f rtpostgis.sql -d postgres -U postgres
```

## Step 2 -  Returning Height Values via the API

Up next you will implement a simple [PL/pgSQL](https://en.wikipedia.org/wiki/PL/pgSQL) stored function which will return a height value on the fly. The input payload will be modeled as a `GeoJSON` object.

Let's bring back our `psql` prompt:

```sh
sudo docker exec -it postgrest_tut psql -U postgres
```

This simple function consumes a single GeoJSON `Point` and returns a height value from the raster table in meters. Paste the following snippet into the `psql` prompt:

```sql
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

This function `get_height` consumes a GeoJSON object named `Point` which initially is transformed into the CRS of the raster, here `EPSG:3035`. Then this point (`the_point`) is cross-joined with the cells it intersects. To retrieve the value at this given intersection of the raster it makes use of the function `ST_Value()` which is cast to a numeric and rounded to 2 decimals.

Hit enter to store the function in the schema. That's it, go ahead an give it a shot:

```sh
curl -X POST \
  http://localhost:3005/rpc/get_height \
  -H 'Content-Type: application/json' \
  -H 'Prefer: params=single-object' \
  -d '{"type": "Point","coordinates":[11.6438, 46.9381],"crs":{"type":"name","properties":{"name":"EPSG:4326"}}}'
```

By specifying the request header `Prefer: params=single-object`, you let PostgREST know to interpret the entire POST body as the value of a single parameter. Quite handy for endpoints only expecting one single JSON object.

The input GeoJSON has a CRS specified (EPSG:4326) which could be any projection of your choice listed in the PostGIS CRS table `spatial_ref_sys`. The [official documentation](https://postgis.net/docs/ST_GeomFromGeoJSON.html) doesn't mention this, however if you have a quick glimpse at the [PostGIS sources](https://github.com/postgis/postgis/blob/master/liblwgeom/lwin_geojson.c#L432) you can see for yourself. Note, the GeoJSON CRS specification is not officially supported anymore in [newer GeoJSON versions](https://tools.ietf.org/html/rfc7946#section-4) due to interoperability issues. However it is still tolerated, but could potentially be deprecated in a future PostGIS release.

**The response will be a height value in meters.**

### Wrap-up

Congratulations for completing this tutorial. By now you will have learnt how to set up and use the PostgREST web API to return height values from a digital elevation model.

Please feel free to get in touch with us at **enquiry[at]gis-ops.com** if you have any further questions, need support or have ideas for other tutorials on PostgREST!
