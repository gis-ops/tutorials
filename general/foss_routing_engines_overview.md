# Open Source Routing Engines & Algorithms - An Overview

With this article we aim to give a reasonable overview of a few selected open-source routing engines we've worked with (and for) in the past. We'll rather focus on properties which are important when deciding which routing engine to use for a particular use case.

At the end you'll find a glossary for a (hopefully) approachable explanation of some important concepts in graph theory.

If you have any questions or enquiry, please contact us on enquiry@gis-ops.com.

## TOC

<!-- TOC depthFrom:1 depthTo:3 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Brief History](#user-content-brief-history)
- [Why Open Source](#user-content-why-open-source)
- [Routing Engines](#user-content-routing-engines)
	- [TL;DR: Overview](#user-content-tldr-overview)
	- [OSRM](#user-content-osrm)
	- [Graphhopper](#user-content-graphhopper)
	- [Valhalla](#user-content-valhalla)
	- [Openrouteservice (ORS)](#user-content-openrouteservice-ors)
	- [pgRouting](#user-content-pgrouting)
- [So which routing engine should I use?](#user-content-so-which-routing-engine-should-i-use)
- [Other routing engines](#user-content-other-routing-engines)
- [Data Sources](#user-content-data-sources)
- [GIS • OPS projects](#user-content-gisops-projects)
- [Glossary](#user-content-glossary)
	- [Graph](#user-content-graph)
	- [Node](#user-content-node)
	- [Edge](#user-content-edge)
	- [Cost/weight](#user-content-costweight)
	- [Algorithms](#user-content-algorithms)
	- [Contraction (Hierarchies)](#user-content-contraction-hierarchies)

<!-- /TOC -->


## Brief History

Routing and navigation has been in the hands of industry players for decades. Unsurprisingly, car manufacturers (Japanese leading the way) were the first ones to commercially distribute car navigation systems in the early 80's, while companies like NavTeq (today HERE) and TomTom were providing the proprietary street data.

However, in the 2000's multiple open projects popped up which were destined to change the landscape of routing and navigation forever! The PostgreSQL add-on `pgDijkstra` by Camptocamp's Sylvain Pasche (predecessor of [pgRouting](https://github.com/pgRouting/pgrouting)) opened that door in the mid 2000's shortly after [OpenStreetMap](https://openstreetmap.org) (OSM) was established by Steve Coast in 2004. The founding and rapid development of OSM was the key component for the development of open-sourced routing engines. After all, what good are highly performant open routing algorithms without similarly open street data to route on.

Today OSM hosts the mind-boggling number of **> 7.6 billion nodes** (i.e. locations: POIs, trees, waypoints, traffic lights etc) and almost **200 million road segments**. It is arguably the world's biggest open database of physical objects and in many developing countries the best data source. This huge archive not only attracts the biggest tech companies, governments and NGO's, it also triggered a gigantic wealth of software development consuming OSM data, ranging from basemap generators to history statistics. And yes, also routing engines.

## Why Open Source

For many people, free and open source software (FOSS) had a questionable aftertaste for a long time, being scolded for clunkiness and common user-unfriendliness. This concept has been overhauled in the past decade by a large army of developers who contributed millions of man hours to millions of open source projects. In some instances entire tech branches almost entirely rely on open source software, such as machine learning. Building software in the open with others to be able to review or even contribute source code makes the whole process entirely transparent.

Open source routing engines have gained massively in popularity, the latest after the shameless price increase of Google Maps in 2018. The clear advantages are

**Flexibility**: use hosted services (Mapbox, GraphHopper or OpenRouteService) or host your own routing service under your own control
**No vendor lock-in**: install your own routing service instance
**Transparency**: open source code lets you examine the algorithms and contribute to
**Price tag**: obviously it's for free to install/use and scalability becomes less a business case compared to hosted services

## Routing Engines

The open-source community offers a wide range of professional-grade routing and navigation applications which are free to install, run and use. One thing they **all** have in common: they support OpenStreetMap data out-of-the-box (see [Data Sources](#user-content-data-sources) for details on other data sources). However, the individual engines excel at one thing or another over all the others. And we'd like to point out a few specialties about routing engines we've worked with in the past (there are quite a few others, see [below](#user-content-other-routing-engines)).

All engines are **very** easy to set up locally on a server or PC, most provide Docker images for one-line setups. So we won't focus on that. Rather on what makes them special.

### TL;DR: Overview

Below we give a overview of open-source routing engines we've worked with in the past (thus is not **at all** complete) and highlight some of their properties. **Note**, this table is **only** referring to the capabilities of the core routing engine (without additional software/add-on's) when it's deployed locally on a server/computer. The score-based attributes (with stars) are meant to be relative to the worst/best candidate and are somewhat subjective. The more stars, the "better", i.e. 5 stars for RAM requirements is a good thing (needs little RAM).

|                                                  	| OSRM                          	| Graphhopper                           	| Valhalla                                	| Openrouteservice                      	| pgRouting<sup>[1](#footnote1)</sup> 	|
|--------------------------------------------------	|-------------------------------	|---------------------------------------	|-----------------------------------------	|---------------------------------------	|-------------------------------------	|
| **Profiles**<br> Car                             	| :heavy_check_mark:            	| :heavy_check_mark:                    	| :heavy_check_mark:                      	| :heavy_check_mark:                    	| -                                   	|
| Truck                                            	| :negative_squared_cross_mark: 	| :negative_squared_cross_mark:         	| :heavy_check_mark:                      	| :heavy_check_mark:                    	| -                                   	|
| Pedestrian                                       	| :heavy_check_mark:            	| :heavy_check_mark:                    	| :heavy_check_mark:                      	| :heavy_check_mark:                    	| -                                   	|
| Bike                                             	| :heavy_check_mark:            	| :heavy_check_mark:                    	| :heavy_check_mark:                      	| :heavy_check_mark:                    	| -                                   	|
| Transit                                          	| :negative_squared_cross_mark: 	| :heavy_check_mark:                    	| :heavy_check_mark:                      	| :negative_squared_cross_mark:         	| -                                   	|
| Others                                           	| -                             	| other bikes<br> motorcycle<br> hiking 	| taxi<br> bus<br> scooter<br> motorcycle 	| other bikes<br> wheelchair<br> hiking 	| -                                   	|
| **API**<br> Routing                              	| :heavy_check_mark:            	| :heavy_check_mark:                    	| :heavy_check_mark:                      	| :heavy_check_mark:                    	| :heavy_check_mark:                  	|
| Isochrones                                       	| :negative_squared_cross_mark: 	| :heavy_check_mark:                    	| :heavy_check_mark:                      	| :heavy_check_mark:                    	| :heavy_check_mark:                  	|
| Matrix                                           	| :heavy_check_mark:            	| :negative_squared_cross_mark:         	| :heavy_check_mark:                      	| :heavy_check_mark:                    	| :heavy_check_mark:                  	|
| Map Matching                                     	| :heavy_check_mark:            	| :heavy_check_mark:                    	| :heavy_check_mark:                      	| :negative_squared_cross_mark:         	| :negative_squared_cross_mark:       	|
| Elevation                                        	| :negative_squared_cross_mark: 	| :negative_squared_cross_mark:         	| :heavy_check_mark:                      	| :negative_squared_cross_mark:         	| :negative_squared_cross_mark:       	|
| Optimization                                     	| :negative_squared_cross_mark: 	| :negative_squared_cross_mark:         	| :heavy_check_mark:                      	| :negative_squared_cross_mark:         	| :heavy_check_mark:                  	|
| **Features**<br> Turn restrictions               	| :heavy_check_mark:            	| :heavy_check_mark:                    	| :heavy_check_mark:                      	| :negative_squared_cross_mark:         	| :heavy_check_mark:                  	|
| Avoid locations/polygons                         	| :negative_squared_cross_mark: 	| :heavy_check_mark:                    	| :heavy_check_mark:                      	| :heavy_check_mark:                    	| :heavy_check_mark:                  	|
| Dynamic vehicle attributes                       	| :negative_squared_cross_mark: 	| :negative_squared_cross_mark:         	| :heavy_check_mark:                      	| :heavy_check_mark:                    	| :heavy_check_mark:                  	|
| Alternative routes                               	| :heavy_check_mark:            	| :heavy_check_mark:                    	| :heavy_check_mark:                      	| :heavy_check_mark:                    	| :negative_squared_cross_mark:       	|
| Round trips                                      	| :negative_squared_cross_mark: 	| :heavy_check_mark:                    	| :negative_squared_cross_mark:           	| :heavy_check_mark:                    	| :negative_squared_cross_mark:       	|
| Time awareness                                   	| :negative_squared_cross_mark: 	| :negative_squared_cross_mark:         	| :heavy_check_mark:                      	| :negative_squared_cross_mark:         	| :negative_squared_cross_mark:       	|
| **Activity**<sup> [2](#footnote2) </sup>         	| ***                           	| *****                                 	| *****                                   	| *                                     	| ****                                	|
| **Performance**<sup>[3](#footnote3) </sup>       	| *****                         	| ****                                  	| ***                                     	| ****                                  	| **                                  	|
| **RAM requirements**<sup> [4](#footnote4) </sup> 	| *                             	| ***                                   	| ****                                    	| *                                     	| *****                               	|
| **Customizability***<sup>[5](#footnote5) </sup>  	| ***                           	| ***                                   	| **                                      	| *                                     	| ****                                	|
| **Flexibility**<sup>[6](#footnote6) </sup>       	| *                             	| ***                                   	| ****                                    	| *                                     	| *****                               	|
| **Mobile**<sup>[7](#footnote7) </sup>            	| :negative_squared_cross_mark: 	| :heavy_check_mark:                    	| :heavy_check_mark:                      	| :negative_squared_cross_mark:         	| :negative_squared_cross_mark:       	|

<div id="footnote1" /><sup>1</sup><sub> pgRouting relies entirely on "profiles" being generated in SQL</sub>
<div id="footnote2" /><sup>2</sup><sub> Activity is a measure for commit frequency, issue responses/fixes and community involvement</sub>
<div id="footnote3" /><sup>3</sup><sub> Performance is somewhat subjective here and also depends on the exact query/request.</sub>
<div id="footnote4" /><sup>4</sup><sub> Measures how much RAM is needed to <b>build and load</b> the graph, <b>not for single requests</b></sub>
<div id="footnote5" /><sup>5</sup><sub> Customizability should reflect the ease with which profiles can be customized</sub>
<div id="footnote6" /><sup>6</sup><sub> Flexibility denotes the capability of the routing engine to customize the weights <b>per request</b>, e.g. avoid highways/toll roads</sub>
<div id="footnote7" /><sup>7</sup><sub> Whether the routing engine is suitable for mobile/offline</sub>

### OSRM

Initially a [KIT](https://algo2.iti.kit.edu) project led by Dennis Luxen and Christian Vetter, the back-then rising star Mapbox quickly became aware of the highly performant routing engine, hired Dennis Luxen and took over the main development. In 2019 they dropped maintenance of OSRM after hiring some Valhalla engineers and driving its development. Currently, a small, but dedicated, group of contributors maintains and develops OSRM. Activity on feature development has definitely dropped significantly in the last 2 years, but there's still amazing features being added, e.g. [this PR](https://github.com/Project-OSRM/osrm-backend/pull/5907).

#### Advantages

- **Performance**: This is where OSRM really shines in all its glory! Routing takes a few ms, even for long routes > 1000 km. The Matrix API can deliver millions of results in mere seconds.
- **Infrastructure**: There's a good collection of related open-source projects around OSRM: the [frontend](https://github.com/Project-OSRM/osrm-frontend), its [Node bindings](https://github.com/Project-OSRM/osrm-backend#using-the-nodejs-bindings) and C++ library, and their [navigational instructions](https://github.com/Project-OSRM/osrm-text-instructions) package, plus a lot of community tutorials, add-on's and so on.
- **Customizability**: Profiles in OSRM are defined as [Lua scripts](https://www.lua.org), a fairly simple scripting language. It provides [many examples and ready functions](https://github.com/Project-OSRM/osrm-backend/tree/master/profiles) to use when defining new profiles or adapt existing ones. It's a pretty low-barrier, powerful way to modify profile definitions and even OSM attributes. Here's a [small adaptation](https://gist.github.com/TimMcCauley/5bd61b968849ebca4974b636e16f4fa9#file-car-location-dependent-speeds-lua-L448-L464) of an official Lua script to scale the maximum allowed speed for road segments which fall into the boundaries of a user-specified **GeoJSON**!
- **Traffic**: OSRM can [update speed records](https://github.com/Project-OSRM/osrm-backend/wiki/Traffic) in its graph via simple CSV files, which can be used for regular traffic updates.

#### Disadvantages

- **RAM requirements**: The full pre-processing pipeline for the OSM planet file takes > 250 GB of RAM (can be reduced with some tweaks), **per profile**. However, at runtime (i.e. when firing requests), this is reduced to ~35-40 GB.
- **Flexibility**: OSRM is not a good choice if you want give some road attributes different weights **per request** (e.g. to avoid highways or tolls). All weight information is baked into the graph and can't be assigned dynamically.

### Graphhopper

Starting as a personal project of one of the founders, Graphhopper quickly evolved into an open-source commercial service with a main focus on solving highly complex vehicle routing problems. However, Graphhopper remains very dedicated to maintaining and improving its high-quality routing engine for the general public.

#### Advantages

- **Performance**: Even though it lags behind OSRM a little, Graphhopper is one of the fastest routing engines out there. Even continental-scale routes rarely take longer than a few hundred ms.
- **Flexibility**: In the past year Graphhopper saw a great deal of development regarding its runtime flexibility with (even request-specific) [custom profiles](https://github.com/graphhopper/graphhopper/blob/1.0-pre39/docs/core/profiles.md#custom-profiles). However, this will have a huge impact on the performance on longer routes. Their so-called "speed" mode is as unflexible (but almost as fast) as OSRM's most performant routing algorithm (they're in fact very similar).
- **Transit**: Graphhopper [supports public transport routing](https://github.com/graphhopper/graphhopper/tree/master/reader-gtfs) via published [GTFS](https://developers.google.com/transit/gtfs) feeds. These feeds must be published by the local public transportation network and can even contain real-time information for transit lines.

#### Disadvantages

- **RAM requirements**: For best performance the preprocessing stage in Graphhopper requires quite a lot of RAM, though not as much as OSRM. For the planet, be prepared for 64 GB - 128 GB RAM for preprocessing **per profile**. Holding the graph in memory is a lot less demanding and fits in < 32 GB **per profile**.
- **Customizability**: Preparing additional profiles for Graphhopper is quite demanding as Java source code has to be written (no Lua here) with custom rules how to use OSM attributes. However, often one can use an existing profile and instead customize its weightings in a new "profile" (see **Flexibility** above).
- **Few closed source features**: Quite notably Graphhopper decided to close their matrix API code due to its business-critical position, as well as their `truck` profiles (presumably for the same reason). Being an (almost) entirely bootstrapped company without big investors (and no plans on doing so either) delivering highest quality projects, one has to respect that.

### Valhalla

Originally a [Mapzen](https://www.mapzen.com) [[RIP](https://www.wired.com/story/mapzen-shuts-down/)] project, Mapbox took the chance to hire most of its engineers to evolve Valhalla further (and shortly after it dropped OSRM maintenance). Around the same time Tesla chose Valhalla as their in-car navigation system due to its favorable runtime requirements and its unique flexibility in runtime costing of road segments. One of the main advantages of Valhalla is that **all profiles use the same graph**, which is made possible by its dynamic runtime costing (eeeh?! :D you can influence the route finding with many custom factors/penalties/costs, e.g. avoid highways).

#### Advantages

- **Flexibility**: Valhalla's main selling point is the dynamic request parameterization most other routing engines lack while maintaining a good performance with a low memory footprint. Each route request can be calculated with a different set of costings, penalties and factors, of which [there are many](https://github.com/valhalla/valhalla/blob/master/docs/api/turn-by-turn/api-reference.md#automobile-and-bus-costing-options), on top of the statically defined profiles (sorry Kevin, "costing models" of course ;)).
- **RAM requirements**: Due to its genius decision to route on a [**tiled, hierarchical** graph](https://valhalla.readthedocs.io/en/latest/tiles/) (similar to e.g. map tiles) and the clever tile loading mechanisms, Valhalla can run on very modest hardware like a low-end smartphone or a Raspberry Pi for regional road datasets. The OSM planet builds easily on a standard laptop with 16 GB RAM **for all profiles** within 12ish hours.
- **Time dependent routing and traffic**: Valhalla is time-aware and that is quite unique in this field. One can specify departure or arrival time and Valhalla's algorithms will consider temporal restrictions and live or historical traffic data sources while calculating the route.
- **Features**: Of course it has all the "standard" features, such as routing, isochrones and matrix. Additionally Valhalla offers: map matching, multimodal routing, elevation querying, a simple Traveling Salesman solver and a fully integrated Python SDK.

#### Disadvantages

- **Performance**: Valhalla refrained from costly (additional) pre-processing and rather decided to build some of the speed-up techniques used by other engines into the graph structure itself (namely the hierarchies and shortcuts). However, this is not as optimized as e.g. in OSRM. While standard routing is quite performant (ms for regional routes, 1-2 second response time from Madrid to Moscow), matrix requests take comparatively long, see [this issue](https://github.com/valhalla/valhalla/issues/2604#issuecomment-717944419).
- **Setup**: The documentation around the setup of Valhalla is a little thin and can be quite overwhelming in the beginning. This is especially true for running it in a scalable manner, e.g. as a public HTTP API. We set up a [Docker project](https://github.com/gis-ops/docker-valhalla) to alleviate some of that pain.

### Openrouteservice (ORS)

As one of the earliest open source routing engines, ORS started its journey in the GIScience department of the University of Heidelberg, Germany, in 2008. The initial implementation was in PostgreSQL, before the framework shifted to build on top of Graphhopper. In fact, Graphhopper's matrix module was based on the work of Openrouteservice for a longer time.

#### Advantages

- **Performance**: Similar to Graphhopper, with even long routes taking rarely longer than a few hundred milliseconds.
- **Flexibility**: For a long time this was the main advantage of ORS over Graphhopper: being able to parameterize the route with additional weights (avoid highways, tolls etc). However, this also comes at a great performance penalty.
- **Infrastructure**: ORS hosts a variety of related side projects & microservices: elevation HTTP API, POI HTTP API, vehicle routing problem solver (via [VROOM](https://github.com/VROOM-Project/vroom)), geocoding (via [Pelias](https://github.com/pelias)), a [QGIS plugin](https://plugins.qgis.org/plugins/ORStools/) and a Python & R client library for all available APIs.

#### Disadvantages

- **RAM requirements**: Similar to Graphhopper, but even worse. For preprocessing and for running the graphs with the highest routing performance, the OSM planet needs at least 128 GB RAM servers **per profile**.
- **Customizability**: Similar to Graphhopper. Additional profiles must be developed in Java source code. And often you'll have to adjust two projects: openrouteservice **and** Graphhopper.

### pgRouting

Building on top of PostgreSQL, the most powerful open-source SQL DBMS, and its geospatial extension PostGIS, pgRouting offers a wide range of [built-in functions](https://docs.pgrouting.org/latest/en/index.html). It's part of the OSGeo umbrella and receives most maintenance and contributions by the wonderful Vicky Vergara and [Georepublic](https://georepublic.info/en/).

#### Advantages

- **Setup**: It's as easy as installing any other extension for PostgreSQL `CREATE EXTENSION pgRouting`! There's also many helper executables to deal with graph generation/validation etc. If you're in need of a battle-tested PostgreSQL/PostGIS installation, try out [Kartoza's fabulous docker image](https://github.com/kartoza/docker-postgis).
- **Flexibility**: pgRouting has access to the full power of PostgreSQL & PostGIS, so naturally it's the most flexible routing engine: adjust your routing query with simple SQL commands to change all the costings on-the-fly.
- **Customizability**: pgRouting delegates the definition of "profiles" entirely to the user. In fact, a "profile" in pgRouting terms **can be** simply a (or multiple) table(s) containing all information about edge access, speed limits etc. Moreover, this sort of "static" profile isn't even necessary as you can adjust all properties on-the-fly per request!
- **RAM requirements**: pgRouting doesn't consume much RAM for building basic graphs. However, it's quite expensive to calculate long routing queries (e.g. continental scale).

#### Disadvantages

- **Performance**: This is mostly an issue for large graphs, or rather for calculating long routes. The general recommendation is that a single query shouldn't have to look at more than 1 Mio rows (aka edges), though your database can contain a whole more. 1 Mio edges is more or less (+/-50 %) the car-accessible street network of Switzerland. So continent-wide routing queries are prohibitively slow. **Note** there's been work on improving query performance by introducing contraction hierarchies to limit the search space, but we didn't try that yet.

## So which routing engine should I use?

If you actually read through the previous chapters, you might already guess what we're about to say: depends.

It heavily depends on the specific use case, infrastructure and skills. Generally speaking:

If you're comfortable with SQL and only need regional routing queries, use pgRouting.

If you need highly performant matrix queries on a continental scale, use OSRM.

If you need highly dynamic requests/time-aware routing or have a low-spec device, use Valhalla.

If you need highly performant national/continental routing requests on a lower-spec server, use Graphhopper.

## Other routing engines

There's also quite a few open source routing engines we didn't have the chance to explore yet, but do sound very exciting:

- [Itinero](https://www.itinero.tech): A fairly niche but very feature-rich routing engine implemented with C#. Its original focus was solving the Traveling Salesman Problem. Since then it evolved to support intermodal route planning (transit and bike-sharing), offline navigation and isochrones.
- [BRouter](http://brouter.de/brouter-web/#map=5/50.990/9.860/standard): Initially a purely bike-focused routing engine, it now supports a huge variety of transport profiles. The main advantage of BRouter is its high flexibility: each route request can be entirely customized on-the-fly via its own scripting language (which OSM tags to use for which edge weight, access restrictions etc).
- [OpenTripPlanner](https://www.opentripplanner.org): One of the oldest open-source routing engines starting development in 2009 by a collaborative group of companies/agencies/independent developers. It's written in Java and quite actively in development. Its main strength over other alternatives are the fully integrated public transport routing with true multi-modality for a variety of combinations (e.g. transit-pedestrian-bike). As such it's used in many public transportation agencies across the globe.

## Data Sources

While the individual implementations, features and performance of all open source engines vary greatly, they all have one thing in common: they **solely** support OSM as street data source out-of-the-box. In most cases that's all you'll ever need. OSM in most countries has a great coverage of existing road segments with its most important `highway` attribute (declaring the road class, e.g. motorway, residential etc) mostly accurate.

However, for more specialized routing applications, OSM road segments often lack the relevant attributes for routing algorithms to consume. If you think about routing trucks for example, where attributes like `maxweight`, `maxheight` and whether or not vehicles carrying hazardous goods are allowed on a road segment, are crucial. This sort of information is often omitted and makes it hard to use OSM for these applications.

In these special routing applications it's far more reasonable to use proprietary, vetted and guaranteed datasets from commercial vendors. And here's the plug (been waiting for it? :D): GIS • OPS developed a tool to convert proprietary road datasets from HERE and TomTom into the OSM data model, thus allowing our customers to take full advantage of the software & analysis universe built around OpenStreetMap.

You can read more about it [in our blog](FIXME) and play around with our demo app on https://converter.gis-ops.com. You can even try it out locally on your own computer by following the instructions on https://github.com/gis-ops/osm-converter-demo.

## GIS • OPS projects

We've been working hard over the past 2 years to create and contribute to some tools which make it easier to work with the overwhelming task of setting up and using open-source routing engines:

- [routing-py](https://github.com/gis-ops/routing-py): Python library to access lots of public routing, isochrones and matrix APIs in a consistent manner, both closed (e.g. Google, HERE) and open source projects. We abstract the basic request parameters for routing, such as locations, profiles, contour intervals for isochrones, sources/destinations for matrices, for all routing providers, so that changing a routing provider is mostly done in 1 second. At the same time, the library maintains all specific request parameters which makes the individual routing engine unique.
- [routing-graph-packager](https://github.com/gis-ops/routing-graph-packager): The newest project in our family: a simple server Flask app to create and distribute routing graphs **on a schedule**. One can create a "job" via a HTTP API specifying an area with a bounding box, the routing engine to be used to generate the graph, and whether to update the graph packages daily, weekly or monthly. It also takes care of updating the OSM data files on a daily basis and can be configured to also consume TomTom and HERE data sources. So far, we only implemented Valhalla.
- [Valhalla Docker](https://github.com/gis-ops/docker-valhalla): This is our Docker implementation for Valhalla. It's highly flexible in terms of configuration and a really low-barrier way of setting up and maintaining a Valhalla installation yourself.
- [prop2osm](https://github.com/gis-ops/prop2osm): One rather limiting property of open-source routing engines is the fact that they can only consume OSM data. In this spirit we developed a commercial tool to convert proprietary street data sources into the OSM data model, so open-source routing engines can be used with TomTom and HERE data. We have demo app running on https://converter.gis-ops.com which highlights some of the advantages of using proprietary street data with Valhalla: special restrictions/attributes like `maxspeed`, `maxweight` and `hazmat` are close to complete in TomTom and HERE data, whereas really sparse in OSM.

## Glossary

In case you're not entirely familiar about all the terminology being used, we put together a few definitions for the most important graph concepts:

### Graph

The graph is the very basis for routing to work. It consists of nodes (e.g.  junctions), which are connected by edges (i.e. road segments). The crucial property of a graph is the topological consistency: nodes and edges can be uniquely identified, and nodes which should connect to an edge actually have the exact same coordinates as the relevant end of the edge.

The performance of traversing a graph for given locations depends on many things, but most of all it's dependent on how many nodes and edges it has look at during the traversal. Another important factor is whether the graph is entirely in physical memory (as is the case for most routing engines) or has to be pulled from the file-system at run-time (e.g. pgRouting).

There's a lot more to say about graphs (directed vs undirected, centrality etc). It's a very cross-disciplinary concept, ranging from biology/genetics to machine learning and (of course) routing (which is really the origin of graph theory). In fact, a rather high-level, quick summary of graphs is presented in a tutorial about [modeling protein interaction](https://www.ebi.ac.uk/training-beta/online/courses/network-analysis-of-protein-interaction-data-an-introduction/introduction-to-graph-theory/).

### Node

A node is a junction in the graph where one connected edge transitions onto another connected edge. In the case of a road graph that's for example a junction connecting two road segments. A node **must be** connected to at least one road segment/edge (case dead-end), but can be connected to any number of segments/edges (case intersection of multiple roads). Nodes are not to be confused with geometry vertices of road segments: those are meaningless to a graph (though some people refer to nodes as a general term for point objects).

For the case of OSM, graph nodes are not necessarily 1:1 to OSM junctions. When OSM ways are crossing each other, they have to be split up and a junction node has to be introduced at the crossing point.

### Edge

An edge is connecting nodes with each other. In the case of a road graph that's mostly represented by road segments. It's what the routing algorithms traverse, transitioning between road segments/edges via nodes. In most implementations it's the properties of edges determining how costly it is to travel along them, e.g. their length, assigned maximum speed, road class, road surface, slope etc. Each edge **must be** connected to at least two nodes, but can be connected to (in theory) any number of nodes at each end.

An edge is usually directed in the context of routing, i.e. it has explicit start and end nodes and can only be traveled along in one direction (where an undirected edge can be traveled either way).

OSM ways are **not necessarily** 1:1 related to graph edges, as quite a few OSM ways cross other OSM ways. During processing, routing engines have to break up those ways at their crossing points and insert a junction/node. Single OSM ways are most often turned into 2 directed edges (unless a way has e.g. a one-way restriction as in most motorway road segments).

### Cost/weight

You mostly hear about "shortest path" algorithms. However, this is highly misleading. It's often not distance one is interested in, rather how long it takes to go from A from B. Or how much fuel it wastes. Hence a better term is "least cost path". The cost can be whatever you like it to be, e.g. distance, time, fuel consumption..

The cost is what routing algorithms try to minimize when searching a route from A to B. In most cases, the basis for cost is time. While traversing the graph from the starting node/edge, the cost is accumulated along the path. An edge's cost is added to the overall path cost once it's "settled", i.e. it's definitely used in the resulting route because it's the cheapest way to get from the edge's start node to its end node (remember, the start and end node of an edge are often connected to more edges than just one, so it could be cheaper to get to either one of these nodes by taking other edges).

However, the time it takes to travel along a certain edge can be modulated with other edge properties. E.g. an edge is a motorway and requires tolls. The algorithm can take the duration as base cost (i.e. base cost = 10 seconds to travel a 280 m long edge at 100 KPH) and can adjust the cost if the edge should be favored (reduce the final cost) or avoided (increase the final cost) by altering the base cost with a factor representing the user's propensity to travel along toll roads. The cost unit in this case can still be time, but its value is not anymore purely a function of distance and speed but was weighted with additional information. One can also define fixed costs, e.g. during border crossings, which is typically taking a fixed amount of time.

Of course, cost doesn't need to be a property of an _edge_ (like max speed), it can be anything which is encountered along a route. Openrouteservice for example has been experimenting with the very enticing feature of "green routing": pedestrian routes can optionally favor walking along or through green areas such as parks, which is proven to reduce stress and increase health.

### Algorithms

The instructions of exactly how to traverse a given graph, i.e. in which order to travel along the edges and nodes, is referred to as routing algorithm.

A routing algorithm is really just a concept and can be implemented and can be tweaked in many ways. The A\* of Valhalla is not the exact same as pgRouting's A\*, but the concepts are the same. Most routing engines use just a few algorithm concepts, often selected dynamically according to the type of routing calculation (dynamic restrictions, time-awareness, route/isochrone/matrix). Most of these algorithms are based on the classic Dijkstra and use one or more heuristics to speed up the graph traversal. Moreover, most variants need at least some degree of preprocessing where additional information about the graph is being gathered to accelerate the computation in the query phase (i.e. when the graph is built and a route should be calculated). Some concepts are more dynamic than others: plain A\* and Dijkstra (a special case of A\*) are the most flexible as it can dynamically assign weight/cost to each visited edge. However, they're terribly slow on huge networks. Introducing contraction hierarchies to speed up the query phase often bakes the cost fixed into the graph edges and gone is the dynamic behavior.

### Contraction (Hierarchies)

This is a very popular speed-up concept to make the graph traversal **much faster**. It's a quite complex topic: "contracted" nodes are removed from the graph if they're superfluous. Nodes are superfluous if they connect edges which can be merged without losing a degree of freedom on that node and no transition is possible to other hierarchies at that node. The edges which were connecting the contracted nodes are turned into shortcuts directly connecting the neighbor nodes (of the contracted nodes) and the properties (most essentially the cost) are summed up over all contracted edges.

Moreover, contraction can be done in hierarchies, i.e. on multiple hierarchical levels. Levels are often related to road classes, so one could build one contraction hierarchy per (rather aggregated) road class (`highway` attribute in OSM). On nodes where these hierarchies overlap (e.g. on ramps leading to a motorway from a secondary road), the algorithm can "jump" to a higher hierarchy which is faster to travel along and most likely fewer edges have to be visited for a given distance, thereby reducing the search space. Most implementations choose to only allow hierarchical "upward jumps", i.e. the algorithm can't transition/jump from a motorway down to a secondary road while traversing the graph.

By employing bidirectional algorithms, i.e. algorithms which simultaneously start traversing the graph from the beginning and end of the route and meet somewhere in the middle, this guarantees the cheapest/least-cost path (in the context of contraction hierarchies, which use heuristics in the building phase). By removing nodes/edges from the graph, creating shortcuts and allowing only upwards transitions, the search space is significantly reduced and algorithms are magnitudes faster calculating long routes than without contraction hierarchies. Puuh, tough to understand, let alone explain! Try this sweet [interactive demo](https://www.mjt.me.uk/posts/contraction-hierarchies/) if you want to do a deep dive.
