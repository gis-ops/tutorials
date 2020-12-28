### Valhalla Tutorials

This tutorial is part of our Valhalla tutorial series:

-   [Valhalla Docker: How to setup and run Valhalla on Ubuntu with Docker](https://gis-ops.com/valhalla-how-to-run-with-docker/)
-   [Valhalla local [Part1]: How to build and install Valhalla on Ubuntu](https://gis-ops.com/valhalla-part-1-how-to-install-on-ubuntu/)
-   [Valhalla local [Part2]: How to configure and run Valhalla locally on Ubuntu](https://gis-ops.com/valhalla-how-to-run-with-docker-on-ubuntu/)
-   [Valhalla local [Part3]: How to build Valhalla with elevation support on Ubuntu](https://gis-ops.com/valhalla-part-3-how-to-build-with-elevation-support-on-ubuntu/)  

---

# How to configure and run Valhalla with elevation support on Ubuntu

This tutorial will guide you through the required steps to build Valhalla routing tiles with elevation support so you can:

- query the elevation at certain locations (lat/lon) via the `/height` HTTP endpoint
- use elevation for certain Valhalla costing models, e.g. bike to avoid/prefer hills

The elevation data is sourced from the previous Mapzen project [`tilezen`](https://github.com/tilezen) which is a merged dataset from the best open data sources for elevation. See [here](https://github.com/tilezen/joerd/blob/master/docs/data-sources.md#footprints-database) for details of the data sources. The dataset is hosted on Amazon's [OpenData repository](https://registry.opendata.aws/terrain-tiles/) and comprises 1.6 **TB**!!

## Introduction

[Valhalla](https://github.com/valhalla) is a high-performance open source routing software (MIT license) written in C++ and mainly designed to consume OpenStreetMap data. The core engineers work for [Mapbox](https://www.mapbox.com/) and one of the most prestigious companies using Valhalla is [Tesla](https://tesla.com) as their in-car navigation system.

For a comprehensive feature list and a more general overview of FOSS routing engines, read our [article](https://gis-ops.com/open-source-routing-engines-and-algorithms-an-overview/).

 > **Disclaimer**  
 > Validity only confirmed for **Ubuntu 20.04** and **Valhalla 3.0.9**.  

---

## Prerequisites

-   A running Ubuntu with an installed Version of Valhalla or in best case completed our tutorial [How to build and install Valhalla on Ubuntu](https://gis-ops.com/how-to-install-and-use-docker-on-ubuntu/) and be ready to configure your Valhalla setup on Ubuntu 20.04.
-   You definitely need all the dependencies from the previous tutorial installed.

## 1. Preparations

-   Again, be sure to have a running Ubuntu OS with the latest version of Valhalla and/or completed our tutorial [How to build and install Valhalla on Ubuntu](https://gis-ops.com/how-to-install-and-use-docker-on-ubuntu/)
-   All dependencies from the previous tutorial installed. You're going to need them!

As a first step towards the elevation support, we need to install a vital dependency that wasn't part of the previous tutorial:

```bash
sudo apt-get update
sudo apt-get install -y parallel
```

### Test your Valhalla installation

First you should test your local Valhalla installation by typing the following `commands` into your terminal:

```bash
valhalla_build_config
valhalla_build_admins
valhalla_build_tiles -h
valhalla_service
valhalla_build_elevation
```

-   `valhalla_build_config` should return a long JSON output into your terminal.
-   `valhalla_build_admins` should return `Unable to parse command line options because: the option '--config' is required but missing`.
-   `valhalla_build_tiles -h` should return `valhalla_build_tiles 3.0.2` and a few more lines explaining the tool.
-   `valhalla_service` should return something like `… [ERROR] Usage: valhalla_service config/file.json [concurrency]`. This is a good sign for now and shows us that the tool is installed.
-   `valhalla_build_elevation` should return something similar to `/usr/bin/valhalla_build_elevation min_x max_x min_y max_y [target_dir=elevation] [parallelism=8] [decompress=true]`

If all of this is the case, Valhalla should be installed and you're good to go.
If something isn't working as expected, please rebuild/reinstall Valhalla using our tutorial [How to build and install Valhalla on Ubuntu](https://gis-ops.com/how-to-install-and-use-docker-on-ubuntu/).

### Get the source code

If you didn't clone/download Valhalla source code locally yet, you can do it now:

```bash
git clone https://github.com/valhalla/valhalla.git
```

For this tutorial we'll only need the `./valhalla/scripts` folder.

### Download the desired OSM extract

In order to build tiles for Valhalla you need an OSM extract. You can download your desired region from [Geofabrik](https://download.geofabrik.de). Just copy the URL of the extract of your choice. In this tutorial we will once again download Albania:

```bash
curl -o ~/valhalla/albania-latest.osm.pbf https://download.geofabrik.de/europe/albania-latest.osm.pbf
```

## 2. Build the elevation tiles

Now we're going to build the elevation tiles for Albania:#

```bash
cd ~/valhalla/
valhalla_build_elevation 18 38 22 43 ${PWD}/elevation_tiles
```

`valhalla_build_elevation` expects a bounding box for the extent it should download data for, in the format `minx, miny, maxx, maxy`. Klokan Tech has a [good tool](https://boundingbox.klokantech.com/) to easily copy/paste coordinates of bounding boxes.

The result should look similar to this:

```cmd
extracting 420 elevation tiles
Academic tradition requires you to cite works you base your article on.
When using programs that use GNU Parallel to process data for publication
please cite:

  O. Tange (2011): GNU Parallel - The Command-Line Power Tool,
  ;login: The USENIX Magazine, February 2011:42-47.

This helps funding further development; AND IT WON'T COST YOU A CENT.
If you pay 10000 EUR you should feel free to use GNU Parallel without citing.

To silence this citation notice: run 'parallel --citation'.


Computers / CPU cores / Max jobs to run
1:local / 8 / 8

Computer:jobs running/jobs completed/%of started jobs/Average seconds to complete
local:0/400/100%/0.4s
checking all files exist
checking file sizes
```

Important are the last two lines `checking all files exist` and `checking file sizes`, indicating a successful build. A `ll ./elevation_tiles` should confirm that.

**World Bounding Box**
If you're about to build with the OSM planet, you can use the following bounding box:

```bash
valhalla_build_elevation -180 -90 180 90 ${PWD}/elevation_tiles
```

But be careful, this will take some time to build and consume around 1.6 TB (yes, **Terabyte!**) of your disk.

## 3. Prepare the config files

### Build your config file

The config file is the core part of the Valhalla setup and will hold all necessary (and optional) configuration and file paths, so Valhalla knows where to look for and where to store data. Be sure to follow the instructions strictly.

We also add our newly generated elevation data:

```bash
cd ~/valhalla
valhalla_build_config \
  --mjolnir-tile-dir ${PWD}/valhalla_tiles \
  --mjolnir-tile-extract ${PWD}/valhalla_tiles.tar \
  --mjolnir-timezone ${PWD}/valhalla_tiles/timezones.sqlite \
  --mjolnir-admin ${PWD}/valhalla_tiles/admins.sqlite \
  --additional-data-elevation ${PWD}/elevation_tiles \
> conf/valhalla.json
```

-   `valhalla_build_config` is the Valhalla tool to build the needed config file.
-   `--mjolnir-tile-dir` defines the folder where the Valhalla tiles will be processed.
-   `--mjolnir-tile-extract` defines the file where the tarred Valhalla tiles will be stored.
-   `--mjolnir-timezone` defines the folder where the SQLite file holding the time zone areas will be stored.
-   `--mjolnir-admin` defines the path where the SQLite file holding the admin areas will be stored.
-   `--additional-data-elevation ${PWD}/elevation_tiles` defines the path where we created our elevation tiles in the step before.
-   `> conf/valhalla.json` is the output file path for the config file.

You can see all options by either opening the `valhalla_build_config` Python script in a text editor or examining the (rather unreadable) output of `valhalla_build_config --help`.

### Build admin areas

This step is optional, but really recommended. It builds a database of administrative information of countries and regions. Valhalla uses the database during the graph building to determine things like the legal driving side on roads, border crossings etc.

Also, there's a rather serious [bug](https://github.com/valhalla/valhalla/issues/2320) where navigation in roundabouts is wrong if the admin database is not used. If you build the admin database and still encounter this issue, try to build it with the OSM planet rather than an extract.

```bash
valhalla_build_admins --config ./conf/valhalla.json albania-latest.osm.pbf
```

### Build time zones

This step is optional. The time zone areas are used by Valhalla to calculate local departure and arrival times:

```bash
./scripts/valhalla_build_timezones > ./valhalla_tiles/timezones.sqlite
```

## 4. Build your tiles with elevation

With all the preparations done, we can finally build the routing tiles, i.e. the graph. The last step is aggregating all tiles into a tar file. That's much more efficient for Valhalla's loading and caching processes.

```bash
cd ~/valhalla
valhalla_build_tiles -c conf/valhalla.json albania-latest.osm.pbf
find valhalla_tiles | sort -n | tar -cf "valhalla_tiles.tar" --no-recursion -T -
```

## 5. Run and test Valhalla

### Run Valhalla

Now we're ready to run Valhalla with our `valhalla.json` and on the specified amount of cores:

```bash
valhalla_service ~/valhalla/scripts/conf/valhalla.json 2
```

### Test Valhalla

Valhalla should be running now and we're going to test if the integration of the elevation data was successful by querying the `/height` endpoint with some coordinates to extract the elevation.

If you used the example OSM extract you can just use the following command:

```bash
curl -X POST \
  http://localhost:8002/height \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "range": true,
    "shape": [
                {
        	"lat": 41.327326,
        	"lon": 19.819336
        },
        {
        	"lat": 41.178654,
        	"lon": 19.577637
        },
        {
            "lat": 40.346544,
            "lon": 19.940186
        }
    ]
}' | jq '.'
```

If you used another OSM extract, use appropriate coordinates.

### Assess the response

The response of your Valhalla server should return something like the following structure, depending on your OSM extract and the used coordinates:

<details><summary>Response JSON</summary>
<p>
```json
{
  "shape": [
    {
      "lat": 41.327328,
      "lon": 19.819336
    },
    {
      "lat": 41.178654,
      "lon": 19.577637
    },
    {
      "lat": 40.346542,
      "lon": 19.940186
    }
  ],
  "range_height": [
    [
      0,
      113
    ],
    [
      26136,
      27
    ],
    [
      123680,
      100
    ]
  ]
}
```
</p>
</details>
<br/>

# Next steps:

Now that Valhalla is successfully running with elevation, head over to our Tutorial [How to setup and run Valhalla on Ubuntu in Docker](https://gis-ops.com/valhalla-how-to-run-with-docker/) and see how easy it can be to set up an All-In-One solution of Valhalla with Docker.

# Citation:
-   O. Tange (2011): GNU Parallel - The Command-Line Power Tool,
  ;login: The USENIX Magazine, February 2011:42-47.
-   [Terrain Tiles](https://registry.opendata.aws/terrain-tiles/)
-   [Elevation coverage](https://github.com/tilezen/joerd/blob/master/docs/data-sources.md#footprints-database)
