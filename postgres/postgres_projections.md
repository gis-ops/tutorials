# When and Why Projections Matter (+ Practical Examples)

Entering the world of projections can be slightly overwhelming. 
With this basic tutorial we would like to touch this vast topic and help you understand why and when they matter.
Generally speaking which projection to choose is fairly use case specific and we would like to give you a pinch of background information to get you started before we do dive into some hands-on examples.

## Specify a Location on a Plane requires a Map Projection

Projecting the globes 3D ellipsoid on a plane 2D surface isn't an easy task. 
Well mathematically speaking it may be an easy task however you will quickly notice it is impossible to do so and not distort the shapes and boundaries of the continents.
To this end there exist all different kinds of projections mostly derived from the [Worlds Geodetic System 84](https://en.wikipedia.org/wiki/World_Geodetic_System) which have their own specific disadvantages and advantages.
If you were to flatten (project) the WGS84 reference ellipsoid onto a plane areas near the poles will look greatly exaggerated ([EPSG: 4326](https://epsg.io/4326)).
On the other hand it has its advantages near the equatorial latitudes.
Some other projections such as Robinson's have advantages of visualisation in the higher latitudes.
There also exist a whole range of equal-area map projected coordinate systems (e.g. Mollweide) which make sure that regions will preserve their size corresponding to the actual area.
The following examples show a range of different types of projections (from top to bottom and left to right):

* World Geodetic System 1984 [EPSG: 4326](https://epsg.io/4326)  
* World Sinusoidal (equal-area projection) [EPSG: 54008](https://epsg.io/54008)  
* World Wagner V EPSG: 54075 derived from Mollweide
* World Azimuthal Equidistant (equal-area projection) [EPSG: 54032](https://epsg.io/54032)  
* World Goode Homolosine Land (equal-area projection) 54052 
* World Mollweide (equal-area projection) [EPSG: 54009](https://epsg.io/54009)  

![Different Projections](https://user-images.githubusercontent.com/10322094/78188742-75065400-740c-11ea-8c7e-d083393336c3.jpg "Different Projections")

Diving into more detail would go beyond the scope of this article. 
If you are interested in learning more theory and information about different we have compiled a list of links in the tail of this post.
We do highly recommend that you conduct ample research subject to your geographic extent of data whilst creating maps for different use cases.

## Projected vs. Geographic Coordinate Systems and Measuring Distances and Areas 

Let's circle back to the World Geodetic System 84. 
Amongst many there exist 2 quite prominent projections of this specific datum, namely WGS84 [EPSG: 4326](https://epsg.io/4326) and Pseudo-Mercator [EPSG: 3857](https://epsg.io/3857) (if this sounds a little confusing, please read [this thread](https://gis.stackexchange.com/a/21372/6253) if you are).
The former is a geographic coordinate system with its coordinates presented in latitude and longitude whereas the latter is subject to a cartesian projected coordinate system on a projected flat surface with its coordinates having a simple relation to eastings and northings. 
So what does this mean and why should you care?
Obviously you could compute distances, areas or what not in both types of projections with the difference being that the result would yield results in *degrees* or *meters*.
Our friends from *PostGIS* have written quite a nice article describing the differences with some [great examples computing the distance between Paris and London in both types of projections](https://postgis.net/workshops/postgis-intro/geography.html).


## Cartesian, great! Can I start measuring now?

The short answer is you could, the long answer you shouldn't yet.
And this is where you have to be very careful by choosing your cartesian projection system wisely.
Let's dive into a tangible example.  
Remember: cartesian coordinates normally have a relation to eastings and northings which implicitly have an origin (0,0).

If we for example have a map dataset of the United Kingdom and we want to compute distances between points which could be cities, we should make sure that our projection suits the region.
The Ordnance Survey of Great Britain 36 [EPSG:4277](https://epsg.io/4277) / [OSGB36 Datum](https://en.wikipedia.org/wiki/Ordnance_Survey_National_Grid) is a geographic coordinate system from which the British National Grid is derived being a projected coordinate system [EPSG: 27700](https://epsg.io/27700) (By the way, what ESPG:3857 is for EPSG:4326 that is EPSG:27700 for EPSG:4277).

## The British National Grid (EPSG:27700)

Each grid cell (square) features an identifier which consists of 2 grid letters, the first being the identifier of the 500x500km square it belongs to.
5 of these exist, namely S, T, N, H and O.
These parent squares are then again subdivided into 25 further squares of 100x100km size which is depicted by the second letter from A-Z starting in the north-west corner of the grid and Z being in the south-east corner. 
The following image should help you understand.

![osgb27700-100_100km](https://user-images.githubusercontent.com/10322094/78184831-d840b800-7405-11ea-9637-dded30172c5b.jpg)

Let's focus on Cornwall which lies in the `SW` square.
Obviously this 100x100km square can be broken down into a smaller grid.
For the sake of example we have added the OSGB 10x10km grid which is depicted by rows and colums from south-west to north-east and the first being `SW00`. 
The city of *Penzance* (who doesn't love [The Pirates of Penzance...](https://en.wikipedia.org/wiki/The_Pirates_of_Penzance)) can be found in `SW42` which is the second row and fourth column.
This `SW` grid cell is located `100 km` east of the south-west origin of SV (easting 0, northing 0).
It's south-west point is at (easting 100, northing 0), it's south-east point is at (easting 200, northing 0), it's north-west point is at (easting 100, northing 100) and *Penzance* features an easting of `147092` and a northing of `030263`, telling us it's `147 km` east and `30 km` north from our origin in SV.

![osgb27700_SW](https://user-images.githubusercontent.com/10322094/78188238-987ccf00-740b-11ea-9921-eaf36013e11a.jpg)

Similarly to the Ordnance Survey of Great Britain each country has its own national grid(s) which are suitable for describing locations on a plane and computing spatial information, e.g. the [United States National Grid](https://en.wikipedia.org/wiki/United_States_National_Grid).


## Comparisons, yes please.

By now you are probably most interested to see if there really exist differences in the calculations that we were talking about earlier.
In this following example we will be computing straight line distances between Penzance and London in PostGIS with different projections to emphasize the importance.
The input coordinates are given in EPSG:4326 as latitude and longitude.

### Using WGS 84 / Pseudo-Mercator EPSG:3857

```sql
SELECT round(CAST(
    ST_Distance(
      ST_Transform('SRID=4326;POINT(-5.539267 50.118445)'::geometry, 3857),
      ST_Transform('SRID=4326;POINT(-0.127724 51.507407)'::geometry, 3857)
    )/1000 As numeric),
  2);
```

650.22 kilometers.

### Using World Mollweide

```sql
SELECT round(CAST(
    ST_Distance(
      ST_Transform('SRID=4326;POINT(-5.539267 50.118445)'::geometry, 54009),
      ST_Transform('SRID=4326;POINT(-0.127724 51.507407)'::geometry, 54009)
    )/1000 As numeric),
  2);
```

435.82 kilometers.


### Using British National Grid EPSG:27700

```sql
SELECT round(CAST(
    ST_Distance(
      ST_Transform('SRID=4326;POINT(-5.539267 50.118445)'::geometry, 27700),
      ST_Transform('SRID=4326;POINT(-0.127724 51.507407)'::geometry, 27700)
    )/1000 As numeric),
  2);
```

411.31 kilometers.


We believe the message should be clear.


![Penzance to London Flight of the Crow Distance](https://user-images.githubusercontent.com/10322094/78191458-bfd69a80-7411-11ea-8921-a6001305c4ac.jpg)


## Further Reading Links

https://postgis.net/workshops/postgis-intro/geography.html

https://gis.stackexchange.com/questions/26082/what-is-the-difference-between-geometric-and-geographic-columns

https://community.esri.com/groups/coordinate-reference-systems/blog/2014/09/01/geodetic-distances-how-long-is-that-line-again

https://en.wikipedia.org/wiki/Map_projection

https://gisgeography.com/equal-area-projection-maps/

https://map-projections.net/

https://www.theguardian.com/global/gallery/2009/apr/17/world-maps-mercator-goode-robinson-peters-hammer






