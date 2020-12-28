### Valhalla Tutorials

This tutorial is part of our Valhalla tutorial series:

-   [Valhalla Docker: How to setup and run Valhalla on Ubuntu with Docker](https://gis-ops.com/valhalla-how-to-run-with-docker/)
-   [Valhalla local [Part1]: How to build and install Valhalla on Ubuntu](https://gis-ops.com/valhalla-part-1-how-to-install-on-ubuntu/)
-   [Valhalla local [Part2]: How to configure and run Valhalla locally on Ubuntu](https://gis-ops.com/valhalla-part-2-how-to-run-valhalla-on-ubuntu/)
-   [Valhalla local [Part3]: How to build Valhalla with elevation support on Ubuntu](https://gis-ops.com/valhalla-part-3-how-to-build-with-elevation-support-on-ubuntu/)  

---

# How to configure and run Valhalla locally on Ubuntu 20.04

This tutorial will show you how to configure Valhalla to be able to run its HTTP API on Ubuntu 20.04, including its administrative and timezone databases.

## Introduction

[Valhalla](https://github.com/valhalla) is a high-performance open source routing software (MIT license) written in C++ and mainly designed to consume OpenStreetMap data. The core engineers work for [Mapbox](https://www.mapbox.com/) and one of the most prestigious companies using Valhalla is [Tesla](https://tesla.com) as their in-car navigation system.

For a comprehensive feature list and a more general overview of FOSS routing engines, read our [article](https://gis-ops.com/open-source-routing-engines-and-algorithms-an-overview/).

 > **Disclaimer**  
 > Validity only confirmed for **Ubuntu 20.04** and **Valhalla 3.0.9**.

## Did you know?

-   If you haven't setup Valhalla on Ubuntu 20.04 yet, head over to the tutorial on [How to build and install Valhalla 3.0.9 on Ubuntu 20.04](https://gis-ops.com/valhalla-how-to-build-and-install-on-ubuntu/).
-   For a more easy approach to setup and run Valhalla, you can alternatively have a look at our [How to setup and run Valhalla on Ubuntu 20.04 in Docker](https://gis-ops.com/valhalla-how-to-run-with-docker/).  

This tutorial will guide you through the process of how to configure and run Valhalla. This tutorial is the direct successor of the tutorial on [How to build and install Valhalla on Ubuntu 20.04](https://gis-ops.com/valhalla-how-to-build-and-install-on-ubuntu-20-04/). You can follow this tutorial analogous on any Ubuntu 20.04 in a docker or other virtual environment with a built and installed version of Valhalla.  

So let's go, `open your terminal!`

## 1. Preparations

### Test your Valhalla installation

First you should test your local Valhalla installation by typing the following `commands` into your terminal:

```bash
valhalla_build_config
valhalla_build_admins
valhalla_build_tiles -h
valhalla_service
```

-   `valhalla_build_config` should return a long JSON output into your terminal.
-   `valhalla_build_admins` should return `Unable to parse command line options because: the option '--config' is required but missing`.
-   `valhalla_build_tiles -h` should return `valhalla_build_tiles 3.0.9` and a few more lines explaining the tool.
-   `valhalla_service` should return something like `… [ERROR] Usage: valhalla_service config/file.json [concurrency]`. This is a good sign for now and shows us that the tool is installed.

If this is the case, Valhalla seems to be installed. So you can continue.

### Update the system  

First update your systems packages with:

```bash
sudo apt-get update
```

This will give you access to the latest available Ubuntu packages through `apt-get`.

### Install the needed packages

```bash
sudo apt-get install -y curl jq unzip spatialite-bin
```

-   `curl` is a handy tool to download nearly anything from any source through its CLI.
-   `jq` is a tool to deal with JSON structures.
-   `unzip` for unzipping files. It is used internally by Valhalla.
-   `spatialite-bin` for the spatialite support of Valhalla to build timezone support and admin areas.

### Download the script files and setup your working directory

Stay in the same folder and run the following commands to download and prepare the needed scripts:

```bash
git clone https://github.com/valhalla/valhalla.git ~/valhalla/
cd ~/valhalla/scripts/
mkdir valhalla_tiles && mkdir conf
```

-   `git clone` will give you access to the latest Valhalla code.
-   `valhalla_tiles` will hold your processed Valhalla files.
-   `conf` will hold your Valhalla config file.

### Download the desired OSM extract

In order to build tiles for Valhalla you need an OSM extract. You can download your desired region from [Geofabrik](https://download.geofabrik.de). Just copy the URL to the extract of your choice. To keep things small we will stick to a small extract in the following example:

```bash
curl -O https://download.geofabrik.de/europe/albania-latest.osm.pbf
```

## 2. Prepare the config files

### Build your config file

The config file is the core part of the Valhalla setup and will hold all necessary (and optional) configurations and file paths, so Valhalla knows where to look for and where to store data. Be sure to follow the instructions strictly:

```bash
valhalla_build_config --mjolnir-tile-dir ${PWD}/valhalla_tiles --mjolnir-tile-extract ${PWD}/valhalla_tiles.tar --mjolnir-timezone ${PWD}/valhalla_tiles/timezones.sqlite --mjolnir-admin ${PWD}/valhalla_tiles/admins.sqlite > ${PWD}/conf/valhalla.json
```

-   `${PWD}` is the system variable for the current working directory.
-   `valhalla_build_config` is the Valhalla tool to build the needed config file.
-   `--mjolnir-tile-dir` defines the folder where the Valhalla tiles will be processed.
-   `--mjolnir-tile-extract` defines the file where the tarred Valhalla tiles will be stored.
-   `--mjolnir-timezone` defines the folder where the SQLite file holding the time zone areas will be stored.
-   `--mjolnir-admin` defines the path where the SQLite file holding the admin areas will be stored.
-   `> ${PWD}/conf/valhalla.json` is the output file path for the config file.

You can see all options by either opening the `valhalla_build_config` Python script in a text editor or examining the (rather unreadable) output of `valhalla_build_config --help`.

### Optional: Build admin areas

This step is optional, but really recommended. It builds a database of administrative information of countries and regions. Valhalla uses the database during the graph building to determine things like the legal driving side on roads, border crossings etc.

Also, there's a rather serious [bug](https://github.com/valhalla/valhalla/issues/2320) where navigation in roundabouts is wrong if the admin database is not used. If you build the admin database and still encounter this issue, try to build it with the OSM planet rather than an extract.

```bash
valhalla_build_admins --config ./conf/valhalla.json albania-latest.osm.pbf
```

This command builds the admin database to `./valhalla_tiles/admins.sqlite` as specified in the `valhalla_build_config` step. It uses the Albania OSM PBF to extract the necessary information. If you still encounter the above mentioned issue, try to build it with the OSM planet rather than an extract.

### Optional: Build time zones

This step is optional. The time zone areas are used by Valhalla to calculate local departure and arrival times:

```bash
./scripts/valhalla_build_timezones > ./valhalla_tiles/timezones.sqlite
```

## 3. Build the routing tiles

With all the preparations done, we can finally build the routing tiles, i.e. the graph. The last step is aggregating all tiles into a tar file. That's much more efficient for Valhalla's loading and caching processes.

```bash
cd ~/valhalla/scripts/
valhalla_build_tiles -c ./conf/valhalla.json albania-latest.osm.pbf
find valhalla_tiles | sort -n | tar -cf "valhalla_tiles.tar" --no-recursion -T -
```

At the end you should find the `valhalla_tiles_tar` file in `~/valhalla/scripts/` with approximately the same size as the input PBF file.

## 4. Run and test Valhalla

### Run Valhalla

Now we're ready to run Valhalla with our `valhalla.json` and on the specified amount of cores:

```bash
valhalla_service ~/valhalla/scripts/conf/valhalla.json 2
```

### Test Valhalla

Valhalla should be running now and we're going to test that.  

If you used the example OSM extract you can just use the following command:

```bash
curl http://localhost:8002/route \
--data '{"locations":[
              {"lat":41.318818,"lon":19.461336},
              {"lat":41.321001,"lon":19.459598}
           ],
         "costing":"auto"
        }' | jq '.'
```

If you used another OSM extract, use appropriate coordinates.

### Assess the response

The response of your Valhalla server should return something like the following structure, depending on your OSM extract and the used coordinates:

<details><summary>Response JSON</summary>
<p>
```json
{
  "trip": {
    "language": "en-US",
    "status": 0,
    "units": "miles",
    "status_message": "Found route between points",
    "legs": [
      {
        "shape": "yx{xmA_lybd@oClBqWxRqWhRsFlEeKlHaChBiGbFqGtEkWxRyQbN",
        "summary": {
          "max_lon": 19.461329,
          "max_lat": 41.321014,
          "time": 28,
          "length": 0.178,
          "min_lat": 41.318813,
          "min_lon": 19.45956
        },
        "maneuvers": [
          {
            "travel_mode": "drive",
            "begin_shape_index": 0,
            "length": 0.154,
            "time": 24,
            "type": 1,
            "end_shape_index": 9,
            "instruction": "Drive northwest on Rruga Stefan Kaçulini.",
            "verbal_pre_transition_instruction": "Drive northwest on Rruga Stefan Kaçulini for 2 tenths of a mile.",
            "travel_type": "car",
            "street_names": [
              "Rruga Stefan Kaçulini"
            ]
          },
          {
            "travel_type": "car",
            "travel_mode": "drive",
            "verbal_pre_transition_instruction": "Continue on Rruga Glaukia for 100 feet. Then You will arrive at your destination.",
            "verbal_transition_alert_instruction": "Continue on Rruga Glaukia.",
            "length": 0.024,
            "instruction": "Continue on Rruga Glaukia.",
            "end_shape_index": 10,
            "type": 8,
            "time": 4,
            "verbal_multi_cue": true,
            "street_names": [
              "Rruga Glaukia"
            ],
            "begin_shape_index": 9
          },
          {
            "travel_type": "car",
            "travel_mode": "drive",
            "begin_shape_index": 10,
            "time": 0,
            "type": 4,
            "end_shape_index": 10,
            "instruction": "You have arrived at your destination.",
            "length": 0,
            "verbal_transition_alert_instruction": "You will arrive at your destination.",
            "verbal_pre_transition_instruction": "You have arrived at your destination."
          }
        ]
      }
    ],
    "summary": {
      "max_lon": 19.461329,
      "max_lat": 41.321014,
      "time": 28,
      "length": 0.178,
      "min_lat": 41.318813,
      "min_lon": 19.45956
    },
    "locations": [
      {
        "original_index": 0,
        "lon": 19.461336,
        "lat": 41.318817,
        "type": "break"
      },
      {
        "original_index": 1,
        "lon": 19.459599,
        "lat": 41.320999,
        "type": "break"
      }
    ]
  }
}
```  
</p>
</details>
<br/>

In case you get a `response` looking like this:

```json
{
"error_code": 171,
"error": "No suitable edges near location",
"status_code": 400,
"status": "Bad Request"
}
```

It is most likely that you didn't change the coordinates for the `curl` request to ones that are inside your chosen OSM extract.
