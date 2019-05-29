### Valhalla Tutorials
This Tutorial is part of our Valhalla tutorial series:

-   [Valhalla Docker: How to setup and run Valhalla on Ubuntu 18.04 with Docker](https://gis-ops.com/valhalla-how-to-run-with-docker/)
-   [Valhalla local [Part1]: How to build and install Valhalla on Ubuntu 18.04](https://gis-ops.com/valhalla-how-to-build-and-install-on-ubuntu-18-04/)
-   [Valhalla local [Part2]: How to configure and run Valhalla locally on Ubuntu 18.04](https://gis-ops.com/valhalla-how-to-run-on-ubuntu-18-04/)
-   [Valhalla local [Part3]: How to build Valhalla with elevation support on Ubuntu](https://gis-ops.com/valhalla-how-to-build-with-elevation-ubuntu/)  

---

# How to configure and run Valhalla with elevation support on Ubuntu

## Introduction

[Valhalla](https://github.com/valhalla) is a high-performance open source routing software (MIT license) written in C++ and mainly designed to consume OpenStreetMap data.

Through its hardware near design, Valhalla offers a wide range of scalable and stable features, e.g.:

-   **Turn-by-turn directions**: Routes from point to point for a given profile with a wide range of options.
-   **Time/distance matrices**: Rapidly calculate many-to-many / one-to-many or many-to-one distances and times between locations.
-   **Optimized routes**: What is the shortest route to visit a set of locations (traveling salesman).
-   **Isochrones/isolines to determine reachability**: Compute the reachability of how far one can travel in a given time from a given location.
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

-   Learn how to set up Valhalla with elevation support on Ubuntu
-   And as usual some new things about how to use Ubuntu and Linux ;)...  


 > **Disclaimer**  
 > Validity only confirmed for **Ubuntu 18.04** and **Valhalla 3.0.2**.  
 > Building and installing software from scratch is always a difficult and unforeseeable task that may render your running system or the software unusable. You may continue this tutorial at your own responsibility.

**Basic vocabulary**
-   `bounding box` is the smallest enclosing box around a geographical feature e.g. the digital representation of a country.

---

## Prerequisites

### Hard prerequisites
-   A running Ubuntu with an installed Version of Valhalla or in best case completed our tutorial [How to build and install Valhalla on Ubuntu 18.04](https://gis-ops.com/how-to-install-and-use-docker-on-ubuntu-18-04/) and be ready to configure your Valhalla setup on Ubuntu 18.04.
-   You definitely need all the dependencies from the previous tutorial installed.

### Recommendations
**Build virtually**: If you're new to building software, **don't try this tutorial on a setup you depend on**. Every system is unique and even if you follow each step correctly in this tutorial, building software from scratch is always bonded to system sensitive tasks and can easily mess around with your live system.  
Alternatively we recommend you to directly use the elevation setup from our Valhalla tutorial [How to setup and run Valhalla on Ubuntu 18.04 in Docker](https://gis-ops.com/valhalla-how-to-run-with-docker/) or run this tutorial in a freshly installed [Ubuntu 18.04 with Virtual Box](https://linuxhint.com/install_ubuntu_18-04_virtualbox/).

---

If you have read to this line I assume you're interested in building and installing **Valhalla with elevation support**.
The following steps will guide you through the whole process and should cover all necessary details.

## 1. Preparations
-   Again, be sure to have a running Ubuntu OS with the latest version of Valhalla and/or completed our tutorial [How to build and install Valhalla on Ubuntu 18.04](https://gis-ops.com/how-to-install-and-use-docker-on-ubuntu-18-04/) 
-   I expect you to have all the dependencies from the previous tutorial installed. You're going to need them! 

As a first step towards the elevation support, we need to install a vital dependency that wasn't part of the previous tutorial:
```bash
sudo apt-get update
sudo apt-get install -y parallel
```
-   `apt-get update` will update your ubuntu repositories and give you access to the latest software sorces.
-   `parallel` is a shell tool that let's you execute multiple tasks at the same time and is used by Valhalla to efficiently build the elevation tiles on multiple cores at the same time.

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
If something isn't working as expected, please rebuild/reinstall Valhalla using our tutorial [How to build and install Valhalla on Ubuntu 18.04](https://gis-ops.com/how-to-install-and-use-docker-on-ubuntu-18-04/).

### Starting fresh: Create your new temporary folders
Now you're going to clean your temporary folder from the previous tutorial and create a fresh one:

```bash
rm -rf ~/valhalla
mkdir ~/valhalla && cd $_
mkdir valhalla_tiles && mkdir conf
```
-   `rm -rf ~/valhalla` recursively deletes our old temporary valhalla folder with all of its content if it exists.
-   `mkdir ~/valhalla` creates the new temporary folder in your home folder `~/`.
-   `cd $_` changes the terminal path directly to the newly created folder. `$_` is a system variable and holds the output of the last command line call. In this case the path to the newly created folder.
-   `valhalla_tiles` will hold your processed Valhalla files.
-   `conf` will hold your Valhalla config file.


### Download the script files
Stay in the same folder and run the following commands to download and prepare the needed scripts:

```bash
git clone https://github.com/valhalla/valhalla.git ~/valhalla_git/
cp -r ~/valhalla_git/scripts/ ~/valhalla/scripts
rm -rf ~/valhalla_git
```

-   `git clone` will give you access to the latest Valhalla code.
-   `rp -R` will recursively copy the needed scripts to our script folder.
-   `rm -rf` will recursively delete the valhalla_git. It's not needed anymore.  

### Download the desired OSM extract
In order to build tiles for Valhalla you need an OSM extract. You can download your desired region from [Geofabrik](https://download.geofabrik.de). Just copy the `*.osm.pbf` link to the extract of your choice. 
In this tutorial we will once again download Albania. Not only to keep things small, but also because Albania is a really beautiful country ;):

```bash
curl -o ~/valhalla/albania-latest.osm.pbf https://download.geofabrik.de/europe/albania-latest.osm.pbf
```
-   This will download the `albania-latest.osm.pbf` OSM extract to our temporary folder.  

## 2. Build the elevation tiles
Now we're going to build the elevation tiles for our OSM extract of Albania from Geofabrik:
```bash
cd ~/valhalla/
valhalla_build_elevation 18 38 22 43 ${PWD}/elevation_tiles
```
-   `cd ~/valhalla/` will change the working directory to our temporary folder.
-   `valhalla_build_elevation 18 38 22 43 ${PWD}/elevation_tiles` will download and construct the elevation data into the folder `elevation_tiles` for the extend of `Albania's bounding box`.

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
Important are the last two lines `checking all files exist` and `checking file sizes`.
They should look exactly the same as in the example above. They are the only hint that the build was successful.

**Note**:
If you're using a different OSM extract please adjust the bounding box accordingly. 
If your're looking for a good source for bounding boxes head over to [boundingbox.klokantech.com/](https://boundingbox.klokantech.com/).
In the `search field` just search for your desired country or manually adjust the bounding box on the map.
Once the bounding box is set, change the value of `Copy & Paste` at the bottom of the page to `TSV`.
E.g. for Albania it would be `19.12	39.64 21.06	42.66` in this exact order. 
As a next step you should `remove the decimal parts` and `round the first two values down and the last two up`.
That way we can ensure that decimal numbers won't break things as well as we have enough buffer at the edges of our elevation data, covering all of the OSM extract when we cut the decimals.
After that just use the values in the same order as an alternative input for `valhalla_build_elevation`.  

**World Bounding Box**
If you're about to build with the OSM world file, you can use the following bounding box:
```bash
valhalla_build_elevation -180 -90 180 90 ${PWD}/elevation_tiles
```
But be careful, this will take some time to build and consume around 1.6TB (Yes, Terabyte!) of your space.

## 3. Prepare the config files
### Build your config file
The config file is the core part of the Valhalla setup and will hold all necessary file paths, so Valhalla knows where to look for and where to store data. Be sure to follow the instructions strictly.
This time we additionally have to add our newly generated elevation data:

```bash
cd ~/valhalla
valhalla_build_config --mjolnir-tile-dir ${PWD}/valhalla_tiles --mjolnir-tile-extract ${PWD}/valhalla_tiles.tar --mjolnir-timezone ${PWD}/valhalla_tiles/timezones.sqlite --mjolnir-admin ${PWD}/valhalla_tiles/admins.sqlite --additional-data-elevation ${PWD}/elevation_tiles > conf/valhalla.json

```
-   `cd ~/valhalla` changes our working path to our temporary valhalla folder.
-   `${PWD}` is the system variable for the current working directory.
-   `valhalla_build_config` is the Valhalla tool to build the needed config file.
-   `--mjolnir-tile-dir` defines the folder where the Valhalla tiles will be processed.
-   `--mjolnir-tile-extract` defines the file where the tarred Valhalla tiles will be stored.
-   `--mjolnir-timezone` defines the folder where the SQLite file holding the time zone areas will be stored.
-   `--mjolnir-admin` defines the path where the SQLite file holding the admin areas will be stored.
-   `--additional-data-elevation ${PWD}/elevation_tiles` defines the path where we created our elevation tiles in the step before.
-   `> conf/valhalla.json` is the output file path for the config file.

### Build admin areas
The admin areas are used by Valhalla to process calculations whenever they cross administrative areas. As long as you're building a single country it is not necessary. Be sure to include them when you use sub-regions with multiple countries in it:

```bash
valhalla_build_admins --config conf/valhalla.json albania-latest.osm.pbf
```

-   `valhalla_build_admins` is the designated tool to build the admin areas.
-   `--config conf/valhalla.json` defines the path to the config file.
-   `albania-latest.osm.pbf` defines the OSM extract to be used. Change this according to your individual OSM extract.

### Build time zones
The time zone areas are used by Valhalla to calculate departure and arrival times:

```bash
./scripts/valhalla_build_timezones conf/valhalla.json
```

-   This command will execute the designated script from the downloaded script files. It is important that you run `valhalla_build_timezones` in the `script` folder!

## 4. Build your tiles with elevation
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

## 5. Run and test Valhalla
### Run Valhalla
First we need to run Valhalla:

```bash
valhalla_service ~/valhalla/conf/valhalla.json 1
```

-   `valhalla_service` will start Valhalla with the correct config file `valhalla.json`.
-   `1` defines how many messages Valhalla will yield into the terminal when first started.  

### Test Valhalla
Valhalla should be running now and we're going to test if the integration of the elevation data was successful.  

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

-   `curl -X POST http://localhost:8002/height` will call to the server running at `localhost` with the port `8002` using the `POST` protocol.
-   `  -H 'Content-Type: application/json'` tells our local server what format our `POST body` will look like. In this case a `JSON`.
-   `  -H 'cache-control: no-cache'` tells the server to deliver live data instead of returning an old `cached` value.
-   `range` if `true`  the server will add distance data to the return value. The distance is always calculated based on the first coordinate.
-   `shape` holds the coordinates the Valhalla server will be queried with.
-   `jq '.'` will take the returned JSON response and print it nicely in the console.  
-   If you used another OSM extract replace the `lat` and `lon` variables from the curl command with ones inside your extract.

### Assess the response
The response of your Valhalla server should return something like the following structure, depending on your OSM extract and the used coordinates:
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
-   `shape` represents the original coordinates you queried the service with.
-   `range_height` represents in the same order as the coordinates in `shape` the calculated values. 
The first value is the distance to the first coordinate. 
Therefore the first value from the first result block is 0. 
The second value defines the `height` of the queried coordinate. 
If the second value states `NULL` the coordinate lies either outside the `bounding box` you generated the elevation tiles for, or something went wrong while building the graph or generating the elevation tiles.

---

# Next steps:
Now that Valhalla is successfully running with elevation, head over to our Tutorial [How to setup and run Valhalla on Ubuntu 18.04 in Docker](https://gis-ops.com/valhalla-how-to-run-with-docker/) and see how easy it can be to set up an All-In-One solution of Valhalla with Docker.

# Troubleshooting
-   `Height` value is returned `NULL`. Please check the order of the provided bounding box carefully. It's most commonly the problem.

# Citation:
-   O. Tange (2011): GNU Parallel - The Command-Line Power Tool,
  ;login: The USENIX Magazine, February 2011:42-47.
-   [Terrain Tiles](https://registry.opendata.aws/terrain-tiles/)
-   [Elevation coverage](https://github.com/tilezen/joerd/blob/master/docs/data-sources.md#footprints-database) 