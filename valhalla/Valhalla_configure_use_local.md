### Valhalla Tutorials
This Tutorial is part of our [Valhalla tutorial series](https://github.com/gis-ops/tutorials/tree/master/valhalla):

-   [How to build and install Valhalla on Ubuntu 18.04](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_Install_Ubuntu1804.md)
-   [How to configure and run Valhalla locally on Ubuntu 18.04](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_configure_use_local.md)
-   [How to setup and run Valhalla on Ubuntu 18.04 in Docker](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_setup_run_docker.md)

---

# How to configure and run Valhalla locally on Ubuntu 18.04

## Introduction

[Valhalla](https://github.com/valhalla) is a high-performance open source routing software (MIT license) written in C++ and mainly designed to consume OpenStreetMap data.

Through its hardware near design, Valhalla offers a wide range of scalable and stable features, e.g.:

-   **Turn-by-turn directions**: Routes from point to point for a given profile with a wide range of options.
-   **Time/distance matrices**: Rapidly calculate many-to-many / one-to-many or many-to-one distances and times between locations.
-   **Optimized routes**: What is the shortest route to visit a set of locations (traveling salesman).
-   **Isochrones/isolines to determine reachability**: Compute the reachability of how far one can travel in a given time from an origin location.
-   **Map matching**: Match noisy GPS data to the street network.

There are some noteworthy & considerable advantages why to use Valhalla:

-   *The street network as tiled data structure*: Similarly to digital web maps and their specific zoom levels, Valhalla generates and exposes its routing graph as street network tiles which have a relationship to each other.  
-   *OpenStreetMap*: Valhalla consumes OpenStreetMap data and its huge range of tags into a consistent roadway hierarchy (tiles!) and is able to consider country-specific driving rules and speed limits.
-   *Narrative guidance*: Turn-by-turn routes comprise rich narrative guidance which are available in multiple languages and ready for output as text-to-speech (TTS) on a smartphone.
-   *Different traveling profiles*: Car, bicycle, pedestrian, heavy vehicle and much more..
-   *Dynamic costing*: One can influence the routing costs on the fly by changing costing parameters in each query.

The following list of companies using Valhalla in their productive systems emphasizes the quality of this well-established routing engine:

-   [Scoot](https://scoot.co/#splash-modal) (Electric vehicles)
-   [Mapillary](https://www.mapillary.com/) (Street imagery)
-   [Mapbox](https://www.mapbox.com/)(Directions, isochrones, time-distance matrices APIs)
-   [Tesla](https://tesla.com) (Electric cars)
-   [Sidewalk Labs](https://sidewalklabs.com/) (Urban real-estate development and operations)

The Valhalla code and more details can be found at their [GitHub repository](https://github.com/valhalla) which is maintained by [many contributors](https://github.com/valhalla/valhalla/graphs/contributors).

**Goals of this tutorials**:

-   get familiar with configuring and using Valhalla on Ubuntu 18.04
-   dive more into the use of the Ubuntu terminal and on running commands in it
-   learn how to use the basic Ubuntu tools like git, curl etc.
-   some new things about how to use Ubuntu and Linux in general ;)...  


 > **Disclaimer**  
 > Validity only confirmed for **Ubuntu 18.04** and **Valhalla 3.0.2**.  
 > The tutorials' aim is to be exact and to give precise information on how the software needs to be configured and used. But due to the individuality of every setup, configuring and using software is always an unforeseeable task, that may render your running system or the software unusable. You may continue this tutorial at your own responsibility.

**Basic vocabulary**
-   `cli` means `command line interface` and refers to tools that can be controlled through commands that you type into your terminal.
-   `OS` means `Operating System` and refers to the system you will run the following steps in.
-   `OSM` means `OpenStreetMap` and refers to the [OSM-Project](https://www.openstreetmap.org).

---

## Prerequisites
Let's start with the basic things.
The **prerequisites** section is **made for you** to give you an overview of what you need and what you should be capable of or at least read about, before you start this tutorial.

### Hard prerequisites
-   A basic understanding of Ubuntu
-   That's it (and remember: a red printed terminal line doesn't necessarily mean, it's an error ;))

### Recommendations
-   If you haven't setup Valhalla on Ubuntu 18.04 yet, head over to the tutorial on [How to build and install Valhalla 3.0.1 on Ubuntu 18.04](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_Install_Ubuntu1804.md).
-   For a more easy approach to setup and run Valhalla, you can alternatively have a look at our [How to setup and run Valhalla on Ubuntu 18.04 in Docker](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_setup_run_docker.md).  

---

This tutorial will guide you through the process of how to configure and run Valhalla. This tutorial is the direct successor of the tutorial on [How to build and install Valhalla on Ubuntu 18.04](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_Install_Ubuntu1804.md). You can follow this tutorial analogous on any Ubuntu 18.04 in a docker or another Virtual Environment with a built and installed version of Valhalla.  
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
-   `valhalla_build_tiles -h` should return `valhalla_build_tiles 3.0.2` and a few more lines explaining the tool.
-   `valhalla_service` should return something like `… [ERROR] Usage: valhalla_service config/file.json [concurrency]`. This is a good sign for now and shows us that the tool is installed.

If this is the case, Valhalla seems to be installed. So you can continue.

### Create the needed folders
Then you will need to create a few folders in your home folder where you are going to store all the files needed to configure and run Valhalla:

```bash
mkdir ~/valhalla && cd $_
mkdir valhalla_tiles && mkdir conf
```

-   `mkdir` is the command to create a new folder
-   `mkdir ~/valhalla` creates our workdir folder in your home folder `~/`.
-   `cd $_` changes the terminal path directly to the newly created folder. `$_` is a system variable and holds the output of the last command line call. In this case the path to the newly created folder.
-   `valhalla_tiles` will hold your processed Valhalla files.
-   `conf` will hold your Valhalla config file.


### Update the system  
First update your systems packages with:

```bash
sudo apt-get update
```

This will give you access to the latest available Ubuntu packages through apt-get.

### Install the needed packages
```bash
sudo apt-get install -y svn curl jq
```

-   `svn` will install the `svn` package that will be needed to download files from GitHub.
-   `curl` is a handy tool to download nearly anything from any source through the cli
-   `jq` is a cli tool to deal with JSON structures.

### Download the script files
Stay in the same folder and run the following command to download and prepare the needed scripts:

```bash
svn export https://github.com/valhalla/valhalla/trunk/scripts ~/valhalla/scripts
```

-   `svn` is a `subversion` tool and is used to download the needed directory from GitHub.  

### Download the desired OSM extract
In order to build tiles for Valhalla you need an OSM extract. You can download your desired region from [Geofabrik](https://download.geofabrik.de). Just copy the `*.osm.pbf` link to the extract of your choice. To keep things small we will stick to a small extract in the following example:

```bash
curl -O https://download.geofabrik.de/europe/albania-latest.osm.pbf
```

-   This will download the `albania-latest.osm.pbf` to the current folder.  

## 2. Prepare the config files
### Build your config file
The config file is the core part of the Valhalla setup and will hold all necessary file paths, so Valhalla knows where to look for and where to store data. Be sure to follow the instructions strictly:

```bash
valhalla_build_config --mjolnir-tile-dir ${PWD}/valhalla_tiles --mjolnir-tile-extract ${PWD}/valhalla_tiles.tar --mjolnir-timezone ${PWD}/valhalla_tiles/timezones.sqlite --mjolnir-admin ${PWD}/valhalla_tiles/admins.sqlite > conf/valhalla.json
```

-   `${PWD}` is the system variable for the current working directory.
-   `valhalla_build_config` is the Valhalla tool to build the needed config file.
-   `--mjolnir-tile-dir` defines the folder where the Valhalla tiles will be processed.
-   `--mjolnir-tile-extract` defines the file where the tarred Valhalla tiles will be stored.
-   `--mjolnir-timezone` defines the folder where the SQLite file holding the time zone areas will be stored.
-   `--mjolnir-admin` defines the path where the SQLite file holding the admin areas will be stored.
-   `> conf/valhalla.json` is the output file path for the config file.

### Optional: Build admin areas
This step is optional. The admin areas are used by Valhalla to process calculations whenever they cross administrative areas. As long as you're building a single country it is not necessary. Be sure to include them when you use sub-regions with multiple countries in it:

```bash
valhalla_build_admins --config conf/valhalla.json albania-latest.osm.pbf
```

-   `valhalla_build_admins` is the designated tool to build the admin areas.
-   `--config conf/valhalla.json` defines the path to the config file.
-   `albania-latest.osm.pbf` defines the OSM extract to be used. Change this according to your individual OSM extract.

### Optional: Build time zones
This step is optional. The time zone areas are used by Valhalla to calculate departure and arrival times:

```bash
./scripts/valhalla_build_timezones conf/valhalla.json
```

-   This command will execute the designated script from the downloaded script files. It is important that you run `valhalla_build_timezones` in the `script` folder!

## 3. Build your tiles
```bash
cd ~/valhalla
valhalla_build_tiles -c conf/valhalla.json albania-latest.osm.pbf
find valhalla_tiles | sort -n | tar -cf "valhalla_tiles.tar" --no-recursion -T -
```

-   `cd ~/valhalla` will bring us back to the important folder, in case you accidentally switched to another one ;)...
-   `valhalla_build_tiles` is the needed tool to build the Valhalla tiles.
-   `-c conf/valhalla.json` shows the tool where to find the config file.
-   `albania-latest.osm.pbf` shows the tool where to find the used OSM extract.
-   `find` is a Linux tool from the `findutils` package and is used to find folders and files. In the current example it will find the `valhalla_tiles` folder.
-   `sort` is part of the `coreutils` package and will sort the files in `-n` a numerical order.
-   `tar` is the `tape archiver` tool and is used to store files into archives with the ending of `.tar`.
-   `-cf` is going to create a new archive `c` and write it to the desired filename `f`.
-   `"valhalla_tiles.tar"` is the file name for the archive file.
-   `--no-recursion` prevents the `tar` command to scan sub directories.
-   `-T -` will use the content of the `valhalla_tiles` folder and store it in the current directory.

## 4. Run and test Valhalla
### Run Valhalla
Now we're ready to run Valhalla:

```bash
valhalla_service ~/valhalla/conf/valhalla.json 1
```

-   `valhalla_service` will start Valhalla with the correct config file `valhalla.json`.
-   `1` defines how many messages Valhalla will yield into the terminal when first started.  

### Test Valhalla
Valhalla should be running now and we're going to test that.  

If you used the example OSM extract you can just use the following command:

```bash
curl http://localhost:8002/route \
--data '{"locations":[
              {"lat":41.318818,"lon":19.461336},
              {"lat":41.321001,"lon":19.459598}
           ],
         "costing":"auto",
         "directions_options":{"units":"miles"}
        }' | jq '.'
```

-   `curl` will call to the server running at the `localhost` with the port `8002`.
-   `--data` is the switch to present the request data with `curl`.
-   `{"locations":...}` holds the data the Valhalla server will be queried with.
-   `jq '.'` will take the returned JSON response and print it nicely in the console.  
-   If you used another OSM extract replace the `lat` and `lon` variables from the curl command with ones inside your extract.

### Assess the response
The response of your Valhalla server should return something like the following structure, depending on your OSM extract and the used coordinates:
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
In case you get a `response` looking like this:
```json
{
"error_code": 171,
"error": "No suitable edges near location",
"status_code": 400,
"status": "Bad Request"
}
```
It is most likely that you didn't change the coordinates for the `curl request` to ones that are inside your chosen OSM extract. Consider adjusting them and running the `curl command` again.


## 5. Valhalla examples
Now that Valhalla is running successfully we can download and play around with the demo files, provided by Valhalla:

```bash
git clone --depth=1 --recurse-submodules --single-branch --branch=gh-pages https://github.com/valhalla/demos.git ~/valhalla_demos
cd ~/valhalla_demos
```  

-   This will download the demo files from Valhalla to our local folder `~/valhalla_demos` and change into it.

#### Demo: Route
```bash
firefox routing/index-internal.html &
```  

-   This will run `firefox` with the routing demo. Be sure to test it in the correct region that you build before.

#### Demo: Isochrone
```bash
firefox isochrone/index-internal.html &
```  

-   This will run `firefox` with the isochrone demo. Be sure to test it in the correct region that you build before.

---

# Troubleshooting
The configuration of Valhalla is tied to many different scopes and may yield some warnings or error messages that you may be concerned about. The following will try to examine some of them for you:
-   An error resulting from the `valhalla_build_admins` tool:  
```
[ERROR] sqlite3_step() error: NOT NULL constraint failed: admin_access.admin_id.  Ignore if not using a planet extract.
```   
This comes up if you build the admin areas on OSM extracts rather than the planet extract. It comes up whenever a relation crosses a border into areas that your OSM extract hasn't got any data.  

-   An error telling you that the `SpatiaLite-tool` couldn't `Vacuum` the database holding the time zone data:  
```bash
SQLite version: xxx
SpatiaLite version: xxx
Inserted xxx rows into 'tz_world' from './dist/combined-shapefile-with-oceans.shp'
1
Error: unknown database ANALYZE
VACUUM ANALYZE failed
```   
This seems to be a bug inside the Valhalla script but not a serious one. The only side effect is that the database will not be `vacuumed` and therefore a bit bigger. It shouldn't affect the building of the tiles. But to be sure keep an eye on the `valhalla_build_tiles` command running successfully.
