## Real-Time and Historical Traffic in Valhalla

Apart from its numerous unique features, [Valhalla](https://github.com/valhalla/valhalla), as the only FOSS routing engine, also has fully integrated support for traffic data:

- **live traffic**:  Integrate a live traffic feed from e.g. TomTom or HERE in your Valhalla routing engine instance, for optimal ETA calculation in shorter routes
- **historical traffic**: Valhalla supports up to 5 mins intervals of historical traffic data from e.g. TomTom or HERE, for optimal ETA calculation on short and long routes

Ideally, Valhalla is operated with both traffic signatures. Internally, live traffic is mostly used in close proximity to the route's origin point and its influence deteriorates linearly moving away from the origin. Meanwhile other speed data sources such as historical traffic data will be blended into the routing calculations at the same rate the impact of live traffic lessens. If in a pinch, **for most use cases historical traffic data is far more valuable than real-time traffic data**.

**Note**, that not all actions/endpoints support traffic-/time-aware calculations. While `/route` and `/isochrones` support traffic, `/sources_to_targets` (aka `/matrix`) does not.

Purchasing appropriate data is less expensive than most people assume. In the case of an asset-based TomTom contract (e.g. for fleet management, where each vehicle is an asset), costs are within a few Euro per asset per year. It's a very valuable investment if ETA accuracy is of essence.

### Showcases

So you can see the impact of traffic-enabled routing with Valhalla we created 2 videos.

The following video shows a time series of 500 routes which are requested every 15 minutes of the week. Increasing ETAs are obvious from 8:00 am to 7:00 pm:

<figure class="video_container">
  <video controls="true" allowfullscreen="true" poster="aux/valhalla_directions.jpg">
    <source src="aux/valhalla_directions.mp4" type="video/mp4">
    <source src="aux/valhalla_directions.ogg" type="video/ogg">
    <source src="aux/valhalla_directions.webm" type="video/webm">
  </video>
</figure>

A more impressive video show a time series of 5 isochrones, also in 15 mins intervals over the whole week.

<figure class="video_container">
  <video controls="true" allowfullscreen="true" poster="aux/valhalla_isochrones.jpg">
    <source src="aux/valhalla_isochrones.mp4" type="video/mp4">
    <source src="aux/valhalla_isochrones.ogg" type="video/ogg">
    <source src="aux/valhalla_isochrones.webm" type="video/webm">
  </video>
</figure>

### Traffic implementation in Valhalla

You might be asking why not other FOSS routing engines support a traffic implementation. The reason is: it's tough business.

Consider what happens on a route from e.g. Berlin to Munich: as the routing algorithm tracks its way towards Munich, time passes and that needs to be accounted for in order to properly respect time-dependent speeds or restrictions (such as "no access between 9am - 5pm") with all its complexities, such as timezones.

So for true traffic support, a routing engine must be able to track the time along the routing algorithm's expansion. That requires more flexible algorithms which lack a lot of the performance goodies one typically likes to see in a routing engine, such as conventional Contraction Hierarchies.

Below we describe some of the internals of Valhalla's traffic implementations. If you need help or support, contact us on enquiry@gis-ops.com.

#### Historical traffic data

Valhalla supports loading each edge (aka road segment) with a total of 2016 time-dependent speed values, which corresponds to a full week's worth of 5 mins intervals. It's the quasi-standard of commercial traffic data.

This kind of traffic data source needs the same base street network as the traffic data is originating from. In practice: if you consider buying TomTom historical traffic data, you'd need the TomTom MultiNet street network data to build a Valhalla routing graph first. We provide [services & software](https://gis-ops.com/routing-and-optimisation/#data-services) to convert TomTom & HERE data to make it usable with FOSS routing engines such as Valhalla.

Once you have a routing graph built, you need to transform the historical traffic data into Valhalla's [expected CSV format](https://github.com/valhalla/valhalla/blob/master/test/data/traffic_tiles/0/003/196.csv), which is a CSV consisting of the following information:

| edge_id  | freeflow speed | constrained speed | variable speeds      |
|----------|----------------|-------------------|----------------------|
| 0/3196/0 | 45             | 35                | BbwACv/mAA//8gAK//kA |

The first column is simply the internal `GraphId`. A mapping of "OSM" IDs (aka TomTom/HERE IDs) to internal `GraphId`s can be generated with the tool [`valhalla_ways_to_edges`](https://github.com/valhalla/valhalla/blob/master/src/mjolnir/valhalla_ways_to_edges.cc). The second and third column are the freeflow (night time) and constrained (day time) speeds. The tricky part is the last column: it's a [DCT-II](https://en.wikipedia.org/wiki/Discrete_cosine_transform) compressed version of the 2016 variable speed values. There is an implementation for compression and decompression in the Valhalla repository as well.

Once the CSV traffic "tiles" have been generated, you can load the historical data on top of the routing graph with Valhalla's [`valhalla_add_predicted_traffic`](https://github.com/valhalla/valhalla/blob/master/src/mjolnir/valhalla_add_predicted_traffic.cc) tool.

#### Live traffic data

While historical traffic data is still somewhat easy, since you only have to generate the traffic "tiles" once, real-time traffic integration is lot more involved. Typically data providers offer a feed which **updates minutely** for every supported region of the world. If the graph covers an entire continent such as Europe, that feed will contain speed updates for millions of edges.

Valhalla implements live traffic via a memory mapped `tar` archive. The internal file layout is the exact same as for the routing tiles. One traffic tile consists of:
- [tile header](https://github.com/valhalla/valhalla/blob/6e28861fd8985935a1e647af9a5a399560945b52/valhalla/baldr/traffictile.h#L185-L192) with info about tile ID, edge count, tile version etc
- [64 bit integer](https://github.com/valhalla/valhalla/blob/6e28861fd8985935a1e647af9a5a399560945b52/valhalla/baldr/traffictile.h#L54-L65) for every edge in the corresponding routing tile, which consolidates info on segmented speeds on the edge

The new [`valhalla_build_extract`](https://github.com/valhalla/valhalla/blob/6e28861fd8985935a1e647af9a5a399560945b52/scripts/valhalla_build_extract#L45) tool will produce a blank skeleton of a traffic.tar with the `-t` option. The path to this archive will be stored in Valhalla's configuration file at `mjolnir.traffic_extract`. Whenever one of the 64 bit integers in the traffic archive changes, Valhalla will realize it and take into account the new value(s).

The challenge is to actually develop that application updating the traffic archive (in whatever language), and that is performant and accurate enough to provide meaningful traffic updates on large regions. The gist of it is:

- pull updated traffic information from provider
- match each traffic segment's OpenLR(/TMC) geometry string to Valhalla's graph using `/trace_attributes` to retrieve all edges' `GraphId`s. Beware that the traffic provider's geometries might not be the same as your routing graph's geometries, e.g. TomTom live traffic feed on a OSM routing graph, so you might have to do a more complex flow of `/locate`, `/route` and `/trace_attributes` to reliable match the provider's geometries to your graph
- once you have the Valhalla representation of a OpenLR traffic entry, you can start matching the entry's speeds to the graph edges to compose the [`TrafficSpeed`](https://github.com/valhalla/valhalla/blob/6e28861fd8985935a1e647af9a5a399560945b52/valhalla/baldr/traffictile.h#L54-L65) struct for each edge; this is only more complicated for start & end edges of each OpenLR record
- after you did this process for all traffic entries, you should have one `TrafficSpeed` 64 bit integer for each Valhalla edge which matched to the current traffic input
- at this point you still need to match those shortcuts whose edges had their speeds updated: Valhalla uses shortcuts in its more performant bidirectional algorithm on longer routes; here you need to calculate the weighted average of all underlying edge speeds and only set the `overall_encoded_speed` part of the `TrafficSpeed`
- finally you have completed a traffic update and you can now write these entries into the existing traffic archive which is shared with the Valhalla server

This is only a brief summary of the high-level steps which need to be taken. There's a lot more details to be said about the whole process. The most important part is: don't use HTTP when matching OpenLR to Valhalla's graph! That's much too slow. Either develop the application in C++, in Python (and use our [pyvalhalla](https://github.com/gis-ops/pyvalhalla) bindings) or develop bindings in your favorite language.

## Related projects

We maintain a multitude of related projects, most of which are open-source:

- [**`pyvalhalla`**](https://github.com/gis-ops/pyvalhalla): High-level Python bindings to the C++ Valhalla library.
- [**Valhalla QGIS Plugin**](https://plugins.qgis.org/plugins/valhalla/): A fairly simple QGIS Plugin to request routes, isochrones & matrices from a Valhalla HTTP server, complete with batch support via Processing algorithms.
- [**Valhalla Docker**](https://github.com/gis-ops/docker-valhalla): A user-friendly docker image to start a Valhalla container to build and serve routing graphs for routing, isochrones, matrices etc.
- [**`routingpy`**](https://github.com/gis-ops/routing-py): Python library to requesting from a multitude of providers (e.g. Mapbox, Vahlhalla, Google Maps etc.) with a common interface. All provider interfaces in `routing-py` require the same arguments so it's very trivial to switch providers.
- [**GIS tutorials**](https://github.com/gis-ops/tutorials): Regularly updated tutorials on geospatial topics covering many routing problems, QGIS Plugin developement, PostgreSQL/PostGIS/pgrouting and many more. They're open-source so the community has a chance to propose fixes or point out problems/mistakes.
- [**prop2osm**](https://github.com/gis-ops/prop2osm): We can help you convert any proprietary road dataset to the OpenStreetMap format so open-source routing engines like Valhalla & OSRM can build graphs from your proprietary data. By default we support TomTom & HERE, but adding other sources is fairly trivial. The software can be licensed or we convert data for you as a service including proper quality control.
