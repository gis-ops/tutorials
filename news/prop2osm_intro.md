# Open Source Routing With TomTom And HERE

Open-source routing engines offer amazing capabilities, going far beyond what commercial applications like Google Maps can deliver. We wrote [an overview article](https://gis-ops.com/open-source-routing-engines-and-algorithms-an-overview) of FOSS routing engines if you're interested.

However, one limitation which is hard to get around: every open-source routing engine solely consumes [**OpenStreetMap**](https://openstreetmap.org) data. We developed software to remove that limitation and offer a way to convert **any proprietary** street dataset into the [OSM data model](https://wiki.openstreetmap.org/wiki/Elements):

<p style="text-align: center; font-size: 1.4em"><a href="https://github.com/gis-ops/prop2osm">prop2osm</a></p>

Data such as TomTom & HERE have detailed and accurate road attributes such as reliable legal speed limits and HGV/truck restrictions (weight, bridge heights etc). We can also process any traffic source such as historical traffic data and live traffic data for the routing engines [Valhalla](https://github.com/valhalla/valhalla) and [OSRM](https://github.com/Project-OSRM/osrm-backend) (only live traffic support).

If you don't want to read on and just have a quick dive into what we offer exactly, see if any of these links and apps provides some help:

- [live demo app](https://converter.gis-ops.com)
- [demo app](https://github.com/gis-ops/osm-converter-demo) for local installation

## TOC

<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:0 orderedList:0 -->

- [Why Open Source Routing Engines?](#user-content-why-open-source-routing-engines)
- [Why proprietary data?](#user-content-why-proprietary-data)
- [Why not combine them?](#user-content-why-not-combine-them)
- [TomTom and HERE in action with Valhalla](#user-content-tomtom-and-here-in-action-with-valhalla)
	- [Demo app](#user-content-demo-app)
- [Services](#user-content-services)
- [Further Information](#user-content-further-information)

<!-- /TOC -->

## Why Open Source Routing Engines?

Open source routing engines have gained massively in popularity, the latest after the shameless price increase of Google Maps in 2018. The clear advantages are

**Flexibility**: use hosted services (Mapbox, GraphHopper or OpenRouteService) or host your own routing service under your own control<br/>
**No vendor lock-in**: install your own routing service instance<br/>
**Transparency**: open source code lets you examine the algorithms and contribute to<br/>
**Price tag**: obviously it's for free to install/use and scalability becomes less a business case compared to hosted services<br/>

The open-source community offers a wide range of professional-grade routing and navigation applications which are free to install, run and use. You might know some of these frameworks:

- [OSRM](https://github.com/Project-OSRM/osrm-backend)
- [Graphhopper](https://graphhopper.com)
- [Valhalla](https://github.com/valhalla/valhalla)
- [Openrouteservice](https://openrouteservice.org)

For a detailed description and even more routing engines, refer to our [overview article](https://gis-ops.com/open-source-routing-engines-and-algorithms-an-overview/) of open-source routing engines.

## Why proprietary data?

We love OpenStreetMap. Period.

But we also believe one should use the most appropriate tool/data for a given job, there's no one-size-fits-all. If you're building an outdoor routing/map app, OSM is most often the best data source available (see [Komoot](https://www.komoot.com)).

While street coverage in OSM is excellent in most regions around the world, most road segments are **missing many important attributes**.

Let's take truck/lorry routing as an example. There's many important properties you'd have to know about the roads you're traveling on in order to not risk an expensive offense, to name just a few

- maximum (truck) speed allowed (case "don't get a speeding ticket")
- maximum weight allowed (case "don't take down an entire bridge")
- maximum height allowed (case "don't shave off the top of your truck")
- are hazardous materials allowed? (case "don't poison protected areas")

Unfortunately there's no good source of truth to judge whether or not these attributes are well captured in a given road dataset. However, simply comparing the relative amounts<sup>[1](#footnote2) </sup>  between OSM and TomTom gives an ok-ish first indication:

|              	| TomTom      	| OSM         	|
|--------------	|-------------	|-------------	|
| total amount 	| 242,435,394 	| 186,836,359 	|
| `maxspeed`   	| 94.5 %      	| 6.7 %       	|
| `maxweight`  	| 0.02 %      	| 0.0005 %    	|
| `maxheight`  	| 0.005 %     	| 0.0004 %    	|
| `hazmat`     	| 0.002 %     	| 0.00005 %   	|

<div id="footnote1" /><sup>1</sup><sub>Dividing the amount of road segments with these attributes by the total amount of road segments, i.e. also pedestrian-only road segments are captured here, diluting the results somewhat</sub>
<br/><br/>

The absolute amount of road segments has (almost) no meaning, as TomTom road segments are usually shorter than in OSM; it's just shown for reference. However, the relative abundance of attributes for these few examples is striking: **TomTom has at least one magnitude, or even multiple magnitudes, better coverage** than OSM (in this admittedly very crude analysis).

And last, but not least, using proprietary data sources also mitigates a lot of liability.

## Why not combine them?

Many FOSS routing engines already offer an amazing set of user-definable options to alter the way a route is calculated. A routing algorithm typically tries to minimize the _cost_ of the overall route, while the cost is mostly the time it takes to travel (see [here](https://gis-ops.com/open-source-routing-engines-and-algorithms-an-overview/#user-content-costweight) for details):

- **avoid tolls**: specify if toll roads should be avoided
- **vehicle dimensions**: specify your vehicle's dimensions to not travel on road segments you're legally not allowed on
- **slope affinity**: specify whether elevation changes along a road should be favored or avoided (e.g. important for road bike navigation)
- **road surfaces**: specify whether you want to avoid bad road surfaces
- **avoid locations/areas**: pass points or polygons to define road segments/areas the route is not allowed to pass through
- and many more...

This is really impressive! However, as briefly discussed above, the road segments in the router-native OSM dataset often do not contain the appropriate attributes to make the best out of those amazing features.

By enabling FOSS routing engines to work with other data sources one can make full use of these. See for example below a **truck route** with OSM and TomTom in Austria calculated with [Valhalla](https://github.com/valhalla/valhalla), where there's a weight restriction of 7 tons on the road which OSM doesn't have:

![Difference in truck route between OSM and TomTom](https://github.com/gis-ops/tutorials/blob/master/news/aux/example_route_7tons.png)

## TomTom and HERE in action with Valhalla

With the software [**prop2osm**](https://github.com/gis-ops/prop2osm), we offer a way to easily make proprietary datasets usable with any routing engine which natively consumes OSM data. By default, we support **TomTom and HERE datasets**, but intentionally left the implementation easily adaptable to other road datasets. Or even to other use cases, such as using open map renderers which mostly only support OSM (e.g. the brilliant [OpenMapTiles](https://github.com/openmaptiles/openmaptiles)) or geocoding engines (such as [Pelias](https://github.com/pelias/pelias) or [Nominatim](https://nominatim.org)).

### Demo app

Enough talking, let's see some action. To showcase the value of **prop2osm** we developed a demo app which contains sample datasets for TomTom (in Austria) and HERE (in Minnesota, USA). In the app you can:
- view the restrictions which are available in the sample areas, both for OSM and TomTom/HERE
- route with Valhalla on multiple waypoints for **car and truck**, i.e. from A to D via B and C, **simultaneously for OSM and TomTom/HERE**, so you can compare the outputs easily
- calculate reachability areas for **car and truck simultaneously for OSM and TomTom/HERE**, so you can compare the outputs easily
- define dynamic restrictions which influence the routing/reachability, such as truck dimensions, desire to use highways etc

![Demo app screenshot](https://github.com/gis-ops/tutorials/blob/master/news/aux/demo_app.png)

You can access the demo app yourself on https://converter.gis-ops.com and play around to your heart's content.

You can even install the whole stack yourself via `docker-compose` by following our instructions on https://github.com/gis-ops/osm-converter-demo. That will give you:
- 3 Valhalla instances, one for each dataset, with pre-built routing graphs
- 1 web app listening on http://localhost:3005

Let us know via [Twitter](https://twitter.com/gis_ops) or [email](mailto:enquiry@gis-ops.com) what you think.

### Traffic integration

Using e.g. the TomTom data, historical traffic data can be purchased which we turn into traffic tiles [Valhalla](https://github.com/valhalla/valhalla) can use. The traffic information has a 5 mins resolution over an average week, i.e. 2016 speed values for every road segment, based on historical traffic patterns. And Valhalla can use that information to predict the traffic along the route and calculate the optimal path according to those traffic patterns.

Additionally, live traffic sources makes sure vehicles (and route finding) can respond to spontaneous events such as traffic jams or road closures because of accidents. According to TomTom's licensing, live traffic can be used with third-party networks such as OSM. However, this service is fairly expensive, while historical traffic data is much cheaper. 

Ideally both traffic sources are used. Read more about it and see some showcases of traffic influenced routing with TomTom [here](https://gis-ops.com/traffic-in-valhalla/).

## Services

We provide [commercial services](https://gis-ops.com/routing-and-optimisation/#data-services) to make your TomTom/HERE data compatible with any FOSS routing engine.

The way it works:

**Input**: your TomTom/HERE data

&#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595;

`some badass processing`<br/>
`0011101001000110101110`<br/>
`bidibdrrrrdüükkkkirrff`<br/>

&#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595; &#8595;

**Output**: a PBF file compatible with all routing engines

**Note**, optionally you can also license TomTom or HERE data through us (in collaboration with [WIGeoGIS](https://www.wigeogis.com/de/home)).

The output file will be converted to the [OSM data model](https://labs.mapbox.com/mapping/osm-data-model/), either in [PBF](https://wiki.openstreetmap.org/wiki/PBF_Format) or XML format. It will have the same properties as you'd find in "real" OSM files with the most relevant objects and attributes for routing applications. No effort has been made so far to adapt the output to other applications, such as map rendering or geocoding, but we're certainly open for the idea.

## Further Information

If you're interest is not satisfied, feel free to get in touch with us: enquiry@gis-ops.com. If you prefer to inform yourself some more, check out these links:

- [Public prop2osm info](https://github.com/gis-ops/prop2osm)
- Demo app: https://converter.gis-ops.com
- [Demo app DIY](https://github.com/gis-ops/osm-converter-demo)
- [FOSS routing engine overview](https://gis-ops.com/open-source-routing-engines-and-algorithms-an-overview/)
