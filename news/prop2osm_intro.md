# Open Source Routing With TomTom And HERE

Open-source routing engines offer amazing capabilities, going far beyond what commercial applications like Google Maps can deliver.

However, one limitation which is hard to get around: every each open-source routing engine solely consumes [**OpenStreetMap**](https://openstreetmap.org) data. We're here to remove that limitation and offer a way to convert **any proprietary** street dataset into the [OSM data model](https://wiki.openstreetmap.org/wiki/Elements):

<div style="text-align: center; font-size: 1.4em"><a href="https://github.com/gis-ops/prop2osm">prop2osm</a></div>

If you don't want to read on and just have a quick dive into what we offer exactly, see if any of these links and apps provides some help:

- [live demo app](https://converter.gis-ops.com)
- [demo app](https://github.com/gis-ops/osm-converter-demo) for local installation

## Why Open Source Routing Engines?

Open source routing engines have gained massively in popularity, the latest after the shameless price increase of Google Maps in 2018. The clear advantages are

**Flexibility**: use hosted services (Mapbox, GraphHopper or OpenRouteService) or host your own routing service under your own control
**No vendor lock-in**: install your own routing service instance
**Transparency**: open source code lets you examine the algorithms and contribute to
**Price tag**: obviously it's for free to install/use and scalability becomes less a business case compared to hosted services

The open-source community offers a wide range of professional-grade routing and navigation applications which are free to install, run and use. You might know some of these frameworks:

- [OSRM](https://github.com/Project-OSRM/osrm-backend)
- [Graphhopper](https://graphhopper.com)
- [Valhalla](https://github.com/valhalla/valhalla)
- [Openrouteservice](https://openrouteservice.com)

For a detailed description, refer to our [overview article](https://gis-ops.com/open-source-routing-engines-and-algorithms-an-overview/) of open-source routing engines.

## Why proprietary data?

We love OpenStreetMap. Period.

But we also believe one should use the most appropriate tool/data for a given job, there's no one-size-fits-all. If you're building an outdoor routing/map app, OSM is most often the best data source available (see [Komoot](https://www.komoot.com)).

While street coverage in OSM is excellent in most regions around the world, most road segments are **missing many important attributes**.

Let's take truck/lorry routing as an example. There's many important properties you'd have to know about the roads you're traveling on in order to not risk an expensive offense, to name just a few

- maximum (truck) speed allowed (case "don't get a speeding ticket")
- maximum weight allowed (case "don't take down an entire bridge")
- maximum height allowed (case "don't shave off the top of your truck")
- are hazardous materials allowed? (case "don't poison protected areas")

Unfortunately there's no good source of truth to judge whether or not these attributes are well captured in a given road dataset. However, simply comparing the relative amounts <sup> [1](#footnote2) </sup>  between OSM and TomTom gives an ok-ish first indication:

|              	| TomTom      	| OSM         	|
|--------------	|-------------	|-------------	|
| total amount 	| 242,435,394 	| 186,836,359 	|
| `maxspeed`   	| 94.5 %      	| 6.7 %       	|
| `maxweight`  	| 0.02 %      	| 0.0005 %    	|
| `maxheight`  	| 0.005 %     	| 0.0004 %    	|
| `hazmat`     	| 0.002 %     	| 0.00005 %   	|

<div id="footnote1" /><sup>1</sup><sub>Dividing the amount of road segments with these attributes by the total amount of road segments, i.e. also pedestrian-only road segments are captured here, diluting the results somewhat</sub>
<br/><br/>

The absolute amount of road segments has (almost) no meaning, as TomTom road segments are usually shorter than in OSM; it's just shown for reference. However, the relative abundance of attributes for these few examples is striking: **TomTom has at least one magnitude, of multiple magnitudes, better coverage**.

## Why not combine them?

Many FOSS routing engines already offer an amazing set of user-definable options to alter the way a route is calculated. 
