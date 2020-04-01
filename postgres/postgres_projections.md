# Measuring Distances and Why Projections Matter (+ Practical Examples)

Entering the world of projections can be slightly overwhelming. 
Basically every projection has advantages and disadvantages. 
Some may preserve elements of direction, distance or area better or worse than others which is why a careful selection of a suitable projection is so crucial. 
With this basic tutorial followed by some practical examples we would like to just touch this broad topic and help you understand why and when they matter when you are trying to measure distances or compute areas of interest for analysis.

## Specifying a Location on a Plane requires a Map Projection

Projecting the globes 3D ellipsoid on a plane 2D surface isn't an easy task. 
Well mathematically speaking it may be an easy task however you will quickly notice it is impossible to do so by not distorting the shapes and boundaries of the countries, oceans and continents.
To this end there exist all different kinds of projections which use a *Geographic Coordinate System* (GCS) as input.
The GCS subject to a geodetic datum uses a three-dimensional spherical surface to define a location on the earth with the help of longitudes and latitudes in degrees.
Some well known GCS are _The World Geodetic System 84_ [(WGS84 Datum)](https://en.wikipedia.org/wiki/World_Geodetic_System), _The North American Datum 83_ [(NAD83 Datum)](https://en.wikipedia.org/wiki/North_American_Datum) or _The Ordnance Survey of Great Britain 36_ [(OSGB36 Datum)](https://en.wikipedia.org/wiki/Ordnance_Survey_National_Grid).
Using the GCS as input the projections themselves are referred to as a *Projected Coordinate Systems* (PCS).

The following image features two different PCS, namely the [_Web Mercator Projection_](https://en.wikipedia.org/wiki/Web_Mercator_projection) ([EPSG:3857](https://epsg.io/3857)) and the [_Mollweide Projection_](https://en.wikipedia.org/wiki/Mollweide_projection) ([EPSG:54009](https://epsg.io/54009)) both derived from the [_World Geodetic System 84 Datum_](https://en.wikipedia.org/wiki/World_Geodetic_System) (note: there exist many more different types of world projection types such as equidistant PCS which show true distances only from the center of the projection or along a special set of lines).

The former is used in prominent web mapping applications such as <a href="https://maps.google.com" target="_blank" title="Google Maps">Google Maps</a> or <a href="https://www.bing.com/maps" target="_blank" title="Bing Maps">Bing Maps</a> which shows areas near the poles as greatly exaggerated.
The latter is an equal-area projection which "trades the accuracy of angle and shape for a accuracy of proportions in area" which means that in the distribution of countries in relation to each other is fairly realistic.

<img src="https://user-images.githubusercontent.com/10322094/78296855-30d98900-74ca-11ea-941e-375ebe212829.jpg" width="800">

On a side note: you might ask yourself why the Web Mercator Projection is so prevalent in web mapping applications? 
Well, the reason is quite straightforward.
Web maps consist of tiles which are square. 
The Web Mercator Projection is equally square and this way the map tiles fit nicely into a powers-of-two schema as you progress through each successive zoom-level. 

Voila, so both of these projections are subject to a cartesian coordinate system (X and Y axes) and both have their units defined in meters. 
Hence, are the coordinates given as eastings and northings from the origin of the projection which at this point should allow us to start measuring?
Well yes but it's treacherous and this is where you have to be careful as both of these projections for example do not preserve distance if you were to calculate the euclidean metric (just compare the image above to your globus on your desk and you will see). 

What we should be looking at are larger scale PCS as uniform (national) grids which will yield realistic & trustworthy distance results.

## So How Do Grids Work?

The fundamental concept of how grids including their eastings and northings work is the same, so let's pick one tangible example.

If we for example have a map dataset of the United Kingdom and we want to compute distances between locations which could be cities, we should make sure that our projection suits the region, e.g. the [_British National Grid (BNG)_](https://en.wikipedia.org/wiki/Ordnance_Survey_National_Grid) [(EPSG:27700)](https://epsg.io/27700) derived from the OSGB36 Datum.
Each grid cell (square) features an identifier which consists of 2 grid letters, the first being the identifier of the 500 x 500 km square it belongs to.
5 of these exist, namely `S`, `T`, `N`, `H` and `O`.
These parent squares are then again subdivided into 25 further squares of 100 x 100 km size which is depicted by the second letter from `A-Z` starting in the north-west corner of the grid and `Z` being in the south-east corner. 
The following image should help you comprehend.

<img src="https://user-images.githubusercontent.com/10322094/78184831-d840b800-7405-11ea-9637-dded30172c5b.jpg" width="450">

Let's focus on Cornwall which lies in the `SW` square.
Obviously this 100 x 100 km square can be broken down into a smaller grid.
For the sake of example we have added the BNG 10 x 10 km grid which is depicted by rows and colums from south-west to north-east and the first being `SW00`. 
The city of *Penzance* (who doesn't love [The Pirates of Penzance...](https://en.wikipedia.org/wiki/The_Pirates_of_Penzance)) can be found in `SW42` which is the second row and fourth column.
This `SW` grid cell is located 100 km east of the south-west origin of SV (easting 0, northing 0).
It's south-west point is at (easting 100, northing 0), it's south-east point is at (easting 200, northing 0), it's north-west point is at (easting 100, northing 100) and *Penzance* features an easting of `147092` and a northing of `030263`, telling us it's 147 km east and 30 km north from our origin which is in `SV` (or just simply: `SW 47092 30263`).

<img src="https://user-images.githubusercontent.com/10322094/78188238-987ccf00-740b-11ea-9921-eaf36013e11a.jpg" width="450">

Similarly to the British National Grid PCS each country may have their own grid(s) which are suitable for describing locations on a plane without distortions and computing spatial information, e.g. the [United States National Grid](https://en.wikipedia.org/wiki/United_States_National_Grid).
There also exists (The Universal Transverse Mercator coordinate system (UTM))[https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system] which features zones uniform over the globe and is also suitable for measurements.


## Comparisons, yes please!

By now you are probably interested to see if there really exist differences in the spatial calculations of distances that we were talking about earlier.
For the sake of completeness we have also added the [_Haversine Formula_](https://en.wikipedia.org/wiki/Haversine_formula), also know as the [_The Great Circle Distance_](https://en.wikipedia.org/wiki/Great-circle_distance) which can be used to measure distances between points from coordinates given in degrees (latitude and longitude).

In this following example we will be computing straight line distances between Penzance and London in PostGIS with different projections to emphasize the importance of choosing wisely.
The input coordinates are given in [EPSG:4326](https://epsg.io/4326) as latitude and longitude.

### Using Web Mercator Projection [EPSG:3857](https://epsg.io/3857)

```sql
SELECT round(CAST(
    ST_Distance(
      ST_Transform('SRID=4326;POINT(-5.539267 50.118445)'::geometry, 3857),
      ST_Transform('SRID=4326;POINT(-0.127724 51.507407)'::geometry, 3857)
    )/1000 As numeric),
  2);
```

650.22 kilometers.

### Using World Mollweide (equal area) [EPSG:54009](https://epsg.io/54009)

```sql
SELECT round(CAST(
    ST_Distance(
      ST_Transform('SRID=4326;POINT(-5.539267 50.118445)'::geometry, 54009),
      ST_Transform('SRID=4326;POINT(-0.127724 51.507407)'::geometry, 54009)
    )/1000 As numeric),
  2);
```

435.82 kilometers.


### Using World Sinusoidal (equal area & equidistant along parallels) [EPSG:54008](https://epsg.io/54008)

```sql
SELECT round(CAST(
    ST_Distance(
      ST_Transform('SRID=4326;POINT(-5.539267 50.118445)'::geometry, 54008),
      ST_Transform('SRID=4326;POINT(-0.127724 51.507407)'::geometry, 54008)
    )/1000 As numeric),
  2);
```

416.98 kilometers.


### Using WGS84 with Haversine's Formula (Great Circle Distance) [EPSG:4326](https://epsg.io/4326)

```sql
SELECT round(CAST(
    ST_DistanceSpheroid(
      'SRID=4326;POINT(-5.539267 50.118445)', 
      'SRID=4326;POINT(-0.127724 51.507407)', 
      'SPHEROID["WGS 84",6378137,298.257223563]'
    )/1000 As numeric),
  2);
```

411.39 kilometers.


### Using UTM zone 30N [EPSG:32630](https://epsg.io/32630)

```sql
SELECT round(CAST(
    ST_Distance(
      ST_Transform('SRID=4326;POINT(-5.539267 50.118445)'::geometry, 32630),
      ST_Transform('SRID=4326;POINT(-0.127724 51.507407)'::geometry, 32630)
    )/1000 As numeric),
  2);
```

411.28 kilometers.


### Using British National Grid [EPSG:27700](https://epsg.io/27700)

```sql
SELECT round(CAST(
    ST_Distance(
      ST_Transform('SRID=4326;POINT(-5.539267 50.118445)'::geometry, 27700),
      ST_Transform('SRID=4326;POINT(-0.127724 51.507407)'::geometry, 27700)
    )/1000 As numeric),
  2);
```

411.31 kilometers.


### Using a grid suitable for Australia [EPSG:28355](https://epsg.io/28355)

```sql
SELECT round(CAST(
    ST_Distance(
      ST_Transform('SRID=4326;POINT(-5.539267 50.118445)'::geometry, 28355),
      ST_Transform('SRID=4326;POINT(-0.127724 51.507407)'::geometry, 28355)
    )/1000 As numeric),
  2);
```

433.65 kilometers (which is of course way off for the UK but would be very suitable for measuring distances in Melbourne or Sydney!).

### Measuring in QGIS with [EPSG:27700](https://epsg.io/27700)

<img src="https://user-images.githubusercontent.com/10322094/78191458-bfd69a80-7411-11ea-8921-a6001305c4ac.jpg" width="450">


We believe the message should be clear.
*A rule of thumb* for choosing a suitable projected coordinate system as Robin Lovelace in [_Geocomputation with R_](https://github.com/robinlovelace/geocompr) has pointed out nicely is:

> The choice should always depend on the properties that are most important to preserve in the subsequent creation of maps of analysis. 


## Further Reading Links

* [ESRI on GCS vs. PCS](https://www.esri.com/arcgis-blog/products/arcgis-pro/mapping/gcs_vs_pcs/)

* [PostGIS Geography versus Geometry](https://postgis.net/workshops/postgis-intro/geography.html)

* [The Difference between Geometric and Geographic Columns in PostGIS](https://gis.stackexchange.com/questions/26082/what-is-the-difference-between-geometric-and-geographic-columns)

* [How Can EPSG:3857 be in Meters?](https://gis.stackexchange.com/questions/242545/how-can-epsg3857-be-in-meters)

* [The Difference between WGS84 and EPSG:4326](https://gis.stackexchange.com/questions/3334/difference-between-wgs84-and-epsg4326)

* [ESRI's blog on "How Long is that Line again?"](https://community.esri.com/groups/coordinate-reference-systems/blog/2014/09/01/geodetic-distances-how-long-is-that-line-again)

* [About Map Projections on Wikipedia](https://en.wikipedia.org/wiki/Map_projection)

* [Gisgeography.com on Equal Area Projection Maps](https://gisgeography.com/equal-area-projection-maps)

* [A Treasure of Knowledge about Map Projections](https://map-projections.net/)

* [The Guardian Writing About Different Projections](https://www.theguardian.com/global/gallery/2009/apr/17/world-maps-mercator-goode-robinson-peters-hammer)






