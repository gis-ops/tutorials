# Valhalla as a Python library

The amazing OSM-based open-source routing engine [Valhalla](https://github.com/valhalla/valhalla) has been around for a while, initially being a [Mapzen (RIP)](https://www.mapzen.com/blog/shutdown) project. It's come a long way since its inception in 2015, featuring now a host of unique feature combinations, like

- complete support for historical and real-time traffic (see our [arcticle](https://gis-ops.com/traffic-in-valhalla/))
- multi-modal routing support for public transit and bike-sharing stations
- highly flexible user parameterization to influence route finding based on individual needs (see the documentation on [routing options](https://github.com/valhalla/valhalla/blob/master/docs/api/turn-by-turn/api-reference.md))
- very low memory footprint compared to alternative routing engines, making it ideal for mobile devices

## Motivation for a Python package

If you want to use Valhalla with a single client to e.g. map-match millions of GPS traces as fast as possible, the much faster alternative is to use the Valhalla library directly in the code you're writing your software in. If you use C++ as your project's language, it's almost trivial to add Valhalla as a library and use its functionality directly. However, if you want to use Python as your project's language, you'd first have to build Valhalla's Python bindings (fairly easy), then make them usable for your project (semi-easy) and, in case you're working with multiple people in a team, build and package the bindings for all platforms (e.g. Windows, Mac or Linux) your team uses (:exploding_head: difficult).

## Enter `pyvalhalla`

Don't worry, we did the :exploding_head: part for you already! We build and package Valhalla's Python bindings for all major platforms and all actively developed Python versions (3.7 - 3.10 at the time of writing). Now it's as easy as

`pip install pyvalhalla`

to install the Python package, giving you access to Valhalla's native C++ library directly from Python and your whole analysis a performance boost!

A small test over Berlin, calculating 500 routes between random addresses and Alexanderplatz, takes **127 seconds** using HTTP, while it only takes **27 seconds** with `pyvalhalla`. So that two-line-change reduced time by 80%.

You'll still need to pre-build a routing graph before you can use the bindings fully. If you have docker installed, you can use our user-friendly [Valhalla docker image](https://github.com/gis-ops/docker-valhalla) to build the graph. This line will fire up a graph build for Berlin (will take 5-10 minutes):

`docker run -dt --name valhalla_gis-ops -p 8002:8002 -v $PWD/custom_files:/custom_files -e tile_urls=http://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf gisops/valhalla:latest`

After the graph built successfully (check with `docker logs valhalla_gis-ops`), try the following lines to test:

```python
import valhalla

# The config is a JSON which defaults many Valhalla configuration options
config = valhalla.get_config(tile_extract='path/to/berlin/custom_files/valhalla_tiles.tar')  # check the path for the graph's valhalla_tiles.tar

# If you pass the config as a dict, a temporary JSON file will be created
# If you pass a file path of an existing config JSON file, it will use that as config file
actor = valhalla.Actor(config)

# print the temporary file path of the generated JSON
print(actor.config_path)

# get some info on the available config options
print(valhalla.get_help()["service_limits"]["auto"]["max_distance"])

# Now the valhalla actor is configured and can use the graph to access
# route, isochrone, matrix, expansion, map-matching etc

locations = [
	{"lat": 52.476586, "lon": 13.418555},
	{"lat": 52.516273, "lon": 13.377314}
]

route = actor.route({
	"costing": "bicycle",
	"locations": locations
})
isochrone = actor.isochrone({
	"costing": "pedestrian",
	"locations": [locations[0]],
	"contours": [
		{"time": 5},
		{"time": 10}
	]
})
expansion = actor.expansion({

	"costing": "pedestrian",
	"locations": [locations[0]],
	"contours": [
		{"time": 5},
		{"time": 10}
	],
	"action": "isochrone",
	"skip_opposites": True,
	"expansion_properties": ["durations", "distances"]
})
```

The central configuration tool for Valhalla is the config JSON. You can either generate a python `dict` to represent configuration with `valhalla.get_config()`, which will create a temporary JSON file in your OS's temporary directory. Or you can pre-generate a config JSON file and pass the file path to the `valhalla.Actor()`. The file path of the config JSON can always be accessed with the `Actor`'s `config_path` attribute.

If you ever encounter restrictions like `Maximum distance exceeded`, check the configuration. You can use `valhalla.get_help()` to retrieve a description of the parameter you're specifying, e.g. `print(valhalla.get_help()["service_limits"]["auto"]["max_distance"])` will print to the console `'Maximum b-line distance between all locations in meters'`.

If you find that `pyvalhalla` doesn't install on your computer because you work on an unsupported operating system, you can contact us for support on enquiry@gis-ops.com.

## Related projects

We maintain a multitude of related projects, most of which are open-source:

- [**Valhalla QGIS Plugin**](https://plugins.qgis.org/plugins/valhalla/): A fairly simple QGIS Plugin to request routes, isochrones & matrices from a Valhalla HTTP server, complete with batch support via Processing algorithms.
- [**Valhalla Docker**](https://github.com/gis-ops/docker-valhalla): A user-friendly docker image to start a Valhalla container to build and serve routing graphs for routing, isochrones, matrices etc.
- [**`routingpy`**](https://github.com/gis-ops/routing-py): Python library to requesting from a multitude of providers (e.g. Mapbox, Vahlhalla, Google Maps etc.) with a common interface. All provider interfaces in `routing-py` require the same arguments so it's very trivial to switch providers.
- [**GIS tutorials**](https://github.com/gis-ops/tutorials): Regularly updated tutorials on geospatial topics covering many routing problems, QGIS Plugin developement, PostgreSQL/PostGIS/pgrouting and many more. They're open-source so the community has a chance to propose fixes or point out problems/mistakes.
- [**prop2osm**](https://github.com/gis-ops/prop2osm): We can help you convert any proprietary road dataset to the OpenStreetMap format so open-source routing engines like Valhalla & OSRM can build graphs from your proprietary data. By default we support TomTom & HERE, but adding other sources is fairly trivial. The software can be licensed or we convert data for you as a service including proper quality control.
