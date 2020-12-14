## Valhalla QGIS Plugin

We're happy to announce the final release of our QGIS Plugin for the amazing routing engine [Valhalla](https://github.com/valhalla/valhalla)!

If you don't know Valhalla yet, you can read some more about its advantages and disadvantages in [our blog](https://gis-ops.com/open-source-routing-engines-and-algorithms-an-overview/#user-content-valhalla).

![Valhalla plugin demo](https://github.com/gis-ops/tutorials/blob/master/news/aux/valhalla_plugin_front.png?raw=true)

## TOC

<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:0 orderedList:0 -->
- [Installation](#user-content-installation)
- [Usage](#user-content-usage)
	- [Provider selection](#user-content-provider-selection)
	- [GUI](#user-content-gui)
		- [General parameters](#user-content-general-parameters)
		- [Routing](#user-content-routing)
		- [Isochrones/Isodistances](#user-content-isochronesisodistances)
		- [Matrix (`sources_to_targets`)](#user-content-matrix-sources_to_targets)
		- [Locate](#user-content-locate)
		- [Extract OSM](#user-content-extract-osm)
	- [Processing Toolbox](#user-content-processing-toolbox)
- [Our Valhalla contributions](#user-content-our-valhalla-contributions)
- [Related projects](#user-content-related-projects)

<!-- /TOC -->

## Installation

You can download the plugin via various sources:

- official [QGIS plugin repository](https://plugins.qgis.org/plugins/Valhalla/)
- our own [QGIS plugin repository](https://qgisrepo.gis-ops.com)

You'll also need access to a Valhalla instance, either remote (e.g. [Mapbox](https://www.mapbox.com)) or local. Both are pre-configured inside the plugin. For Mapbox you'll need a Mapbox API token.

For a local installation of Valhalla, you can try our [Valhalla docker image](https://github.com/gis-ops/docker-valhalla).

## Usage

This plugin offers two main modes of usage:

- **custom UI**: in the "Web toolbar" and the "Web" menu entry there is a custom GUI. Users of the [ORS Tools](https://plugins.qgis.org/plugins/ORStools/) plugin will be very familiar with this.
- **processing algorithms**: Valhalla has its own algorithm family in the "Processing Toolbox" of QGIS, with which you can batch calculate routes/isochrones/matrices and even use them in the "Graphical Modeler".

### Provider selection

You'll need access to a Valhalla instance, either remote (e.g. [Mapbox](https://www.mapbox.com)) or local. For a local installation of Valhalla, you can try our [Valhalla docker image](https://github.com/gis-ops/docker-valhalla).

By default the plugin has Mapbox and `localhost` pre-configured. You can easily add or remove providers by either:

- using the entry in _Web_ ► _Valhalla_ ► _Provider Settings_
- or by clicking the tools icon in the main GUI

### GUI

If you're a user of the [ORS Tools](https://plugins.qgis.org/plugins/ORStools/) plugin the Valhalla's interface will be very familiar to you.

The main advantage of Valhalla over ORS is that you can **calculate routes, isochrones and matrices with a full set of restrictions** (such as vehicle dimensions).

The following methods are implemented:

- **Routing**
- **Isochrones**
- **Matrix**
- **Locate**: extract information about edges and nodes from Valhalla
- **Extract OSM**: with a local OSM file **and [osmium](https://github.com/osmcode/osmium-tool) installed**, you can extract road segments from a OSM PBF file and load them as LineString layers with all their attributes

#### General parameters

Valhalla uses [dynamic costing](https://gis-ops.com/open-source-routing-engines-and-algorithms-an-overview/#user-content-valhalla) to calculate routes, isochrones and matrices. As such almost all options are relevant for all methods. You can see more details for the parameters when you hover with the mouse over its box.

All methods require you to specify a transportation profile (or costing model in Valhalla lingo). Not all costing models are implemented in this plugin (yet).

You can choose to either calculate the "Fastest" route or the "Shortest". The former will take into account all specified costing options (s. below) and find a route where the overall time is minimized. The latter will solely take distance into account and disregard all costing options to calculate the **shortest** path.

For all methods you need to specify one or multiple locations. These are added (or removed) via the "Add" and "Delete" buttons.

One group of advanced parameters are called **Costing Options** and are accessed in the **Configuration** group box. These are often profile-specific and a full list can be viewed in the [Valhalla documentation](https://github.com/valhalla/valhalla/blob/master/docs/api/turn-by-turn/api-reference.md). **Note**, the costing options are only taken into account if its box is ticked.

Another optional parameter is a layer which contains locations to avoid. This **must be** a `Point` layer, **not** a `MultiPoint` layer.

#### Routing

Not much to say that wouldn't be pretty obvious. You can define multiple waypoints, where the exact amount depends on the Valhalla routing engine configuration.

![Valhalla route demo](https://github.com/gis-ops/tutorials/blob/master/news/aux/valhalla_plugin_route.png?raw=true)

#### Isochrones/Isodistances

Isochrones also respect all general and advanced parameters, which is quite powerful.

You can calculate isochrones from multiple locations. By default, each location will fire a separate request to the routing engine. However, if the "Aggregate" option is ticked, it will return the region which is reachable from **any input location** within the defined time/distance intervals.

Optionally, isochrones and/or isodistances can be calculated, which will be collected in separate output layers. The output layers can either be represented as Polygon (default) or as LineString layers. **Note**, Valhalla polygons often have self-intersections.

Optionally, you can opt in to return 2 point layers (option "No Points" unticked): one Point layer with the input points of the source locations and one MultiPoint layer with the points Valhalla used to start the routing algorithm on (so-called snapped points, i.e. snapped to the road network).

![Valhalla isochrone demo](https://github.com/gis-ops/tutorials/blob/master/news/aux/valhalla_plugin_isochrone.png?raw=true)

#### Matrix (`sources_to_targets`)

The `sources_to_targets` will calculate the distance and duration for all input locations to each other, i.e. a symmetrical matrix. Again, also the matrix respects all optional parameters.

The output is a table without any geometry. The point of a matrix is to only return trip summaries and not care about trip details, such as the geometry or navigational instructions.

![Valhalla matrix demo](https://github.com/gis-ops/tutorials/blob/master/news/aux/valhalla_plugin_matrix.png?raw=true)

#### Locate

The `locate` method provides detailed information about streets and intersections close to the input point(s). It also respects all the costing options and only returns the road segments and intersections which are actually accessible considering the parameters you specified. E.g. if you specify a bicycle type `Road`, you will not get information about road segments with bad surface types, because Valhalla disallows traveling on those with a road bike.

The output of the `locate` method is just a window with the raw JSON response. It's mostly useful during debugging.

One more important attribute which can be extracted is the **OSM ID** of ways.

![Valhalla matrix demo](https://github.com/gis-ops/tutorials/blob/master/news/aux/valhalla_plugin_matrix.png?raw=true)

#### Extract OSM

This is a special function: it allows you to extract way objects from a PBF with all its attributes. Every matched OSM way will be inserted into its own layer, so all attributes are preserved.

Internally it's calling the `locate` method, so it'll also respond to all set costing options and profiles. The OSM IDs are extracted from the `locate` response and fed into [`osmium`](https://github.com/osmcode/osmium-tool) which returns the OSM objects.

This is really useful when you're curious why Valhalla would route over one way and not another, even though the other way seems much more logical. It helps you verify and debug routing.

**Note**, this method needs [`osmium`](https://github.com/osmcode/osmium-tool) installed and access to a local PBF (ideally the same used to prepare Valhalla's routing graphs).

![Valhalla matrix demo](https://github.com/gis-ops/tutorials/blob/master/news/aux/valhalla_plugin_locate.png?raw=true)

### Processing Toolbox

You'll find a family of algorithms in QGIS "Processing Toolbox". These allow you to take input from QGIS layers to **batch perform routing, isochrones and matrix** calculations.

The algorithms are grouped into profiles/costing models and every algorithm has an extensive help text to guide you what it's doing and expecting on input, so we'll omit that info here.

You can even use all profile-specific costing options during batch calculation.

## Our Valhalla contributions

We're highly invested into developing Valhalla further and can account for multiple contributions improving its usability: we implemented

- "shortest" to calculate (mostly) shortest path only considering distance
- isodistances, not only isochrones
- ability to avoid entire polygons during routing
- returning the isochrone center coordinate
- more Windows compatibility
- MinGW64 builds so cross-compiling for Windows on Linux works

## Related projects

As routing experts we have a bunch of related projects, most of which are open-source:

- [Valhalla Docker](https://github.com/gis-ops/docker-valhalla): This is our Docker implementation for Valhalla. It's highly flexible in terms of configuration and a really low-barrier way of setting up and maintaining a Valhalla installation yourself.
- [routing-graph-packager](https://github.com/gis-ops/routing-graph-packager): The newest project in our family: a simple server Flask app to create and distribute routing graphs **on a schedule**. One can create a "job" via a HTTP API specifying an area with a bounding box, the routing engine to be used to generate the graph, and whether to update the graph packages daily, weekly or monthly. It also takes care of updating the OSM data files on a daily basis and can be configured to also consume TomTom and HERE data sources. So far, we only implemented Valhalla.
- [prop2osm](https://github.com/gis-ops/prop2osm): One rather limiting property of open-source routing engines is the fact that they can only consume OSM data. In this spirit we developed a commercial tool to convert proprietary street data sources into the OSM data model, so open-source routing engines can be used with TomTom and HERE data. We have demo app running on https://converter.gis-ops.com which highlights some of the advantages of using proprietary street data with Valhalla: special restrictions/attributes like `maxspeed`, `maxweight` and `hazmat` are close to complete in TomTom and HERE data, whereas really sparse in OSM.
- [routing-py](https://github.com/gis-ops/routing-py): Python library to access lots of public routing, isochrones and matrix APIs in a consistent manner, both closed (e.g. Google, HERE) and open source projects. We abstract the basic request parameters for routing, such as locations, profiles, contour intervals for isochrones, sources/destinations for matrices, for all routing providers, so that changing a routing provider is mostly done in 1 second. At the same time, the library maintains all specific request parameters which makes the individual routing engine unique.
