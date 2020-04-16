### Valhalla Tutorials
This Tutorial is part of our Valhalla tutorial series:

-   [Valhalla Docker: How to setup and run Valhalla on Ubuntu 18.04 with Docker](https://gis-ops.com/valhalla-how-to-run-with-docker/)
-   [Valhalla local [Part1]: How to build and install Valhalla on Ubuntu 18.04](https://gis-ops.com/valhalla-part-1-how-to-install-on-ubuntu-18-04/)
-   [Valhalla local [Part2]: How to configure and run Valhalla locally on Ubuntu 18.04](https://gis-ops.com/valhalla-how-to-run-with-docker-on-ubuntu-18-04/)
-   [Valhalla local [Part3]: How to build Valhalla with elevation support on Ubuntu](https://gis-ops.com/valhalla-part-3-how-to-build-with-elevation-support-on-ubuntu/)  

---

# How to setup and run Valhalla on Ubuntu 18.04 in Docker

## Introduction

[Valhalla](https://github.com/valhalla) is a high-performance open source routing software (MIT license) written in C++ and mainly designed to consume OpenStreetMap data.
The core engineers work for [Mapbox](https://www.mapbox.com/) and one of the most prestigious companies using Valhalla is [Tesla](https://tesla.com) (Electric cars). 
It offers different scalable and highly customizable API services such as turn-by-turn directions, optimised routes, detailed isochrones to determine reachability, time-distance matrices and map matching. 

Similarly to digital web maps and their specific zoom levels, Valhalla generates and exposes its routing graph as street network tiles which have a relationship to each other in different hierarchies which makes it very resource friendly compared to other routing frameworks. 
Using [OpenStreetMap](https://openstreetmap.org) data as its source Valhalla provides different traveling profiles to route with and gives enough flexibility to add additional custom profiles with the generic dynamic costing modules within the framework.

The Valhalla code and more details can be found at their [GitHub repository](https://github.com/valhalla) which is maintained by [many contributors](https://github.com/valhalla/valhalla/graphs/contributors).

**Goals of this tutorials**:

-   get familiar with setting up and using Valhalla with Docker
-   dive more into the use of the Ubuntu terminal and on running commands in it
-   learn how to use the basic Ubuntu tools like git, curl etc.
-   some new things about how to use Ubuntu and Linux in general ;)...  

 > **Disclaimer**  
 > Validity only confirmed for **Ubuntu 18.04** and **Valhalla 3.0.2**.  
 > The tutorials' aim is to be exact and to give precise information on how the software needs to be configured and used. But due to the individuality of every setup, configuring and using software is always an unforeseeable task, that may render your running system or the software unusable. You may continue this tutorial at your own responsibility.

---

## Prerequisites
Let's start with the basic things.
The **prerequisites** section is **made for you** to give you an overview of what you need and what you should be capable of or at least read about, before you start this tutorial.

### Hard prerequisites
-   A basic understanding of Ubuntu
-   Knowledge of running commands in the Ubuntu terminal
-   A running Ubuntu 18.04 with the latest `docker` and `docker-compose` version.
-   Some basic Knowledge on how to use Docker
-   The awareness that a red printed terminal line doesn't necessarily mean, it's an error ;)...

### Recommendations


---

This tutorial will guide you through the process of how to configure and run Valhalla inside of Docker on an Ubuntu OS. You can follow this tutorial (please read our `Disclaimer`) analogous on any Linux distribution with a running docker environment.  
So let's go, `open your terminal!`

## 1. Preparations

### Test your docker installation

Depending on your local user rights, test whether you need to run `docker` commands as `sudo` or not by typing:
```bash
docker run hello-world
```   
If you get an ouput similar to this:

```
Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```
You're good to go and can just copy and paste the commands from this tutorial.  

If the output is telling you, that `you don't have enough permissions` to run the command, you need to `add your user to the docker group` or add `sudo` before every `docker command` in this tutorial.   

If the output is similar to this:
```
command not found: ...
```
You should `install docker first`. For a good tutorial have a look at the [How To Install and Use Docker on Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04).
For installing `docker-compose` have a look at [How To Install and Use Docker on Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04).

### Create a temporary folder
First you should create a temporary folder in your home folder to clone the needed docker files to:
```bash
mkdir ~/gisops_docker && cd $_
```   
-   `mkdir` is the command to create a new folder
-   `mkdir ~/gisops_docker` creates our workdir folder in your home folder `~/`.
-   `cd $_` changes the terminal path directly to the newly created folder. `$_` is a system variable and holds the output of the last command line call. In this case the path to the newly created folder.   

### Create the docker-compose.yml
In order to run Valhalla you need to create a `docker-compose.yml` file in your current directory and pass the following content:
```bash
version: '3.0'
services:
  valhalla:
    image: gisops/valhalla:latest
    ports:
      - "8002:8002"
    volumes:
      - ./custom_files/:/custom_files
    environment:
      # The tile_file must be located in the `custom_files` folder.
      # The tile_file has priority and is used when valid.
      # If the tile_file doesn't exist, the url is used instead.
      # Don't blank out tile_url when you use tile_file and vice versa.
      - tile_urls=https://download.geofabrik.de/europe/andorra-latest.osm.pbf https://download.geofabrik.de/europe/albania-latest.osm.pbf
      # Get correct bounding box from e.g. https://boundingbox.klokantech.com/
      - min_x=18 # -> Albania | -180 -> World
      - min_y=38 # -> Albania | -90  -> World
      - max_x=22 # -> Albania |  180 -> World
      - max_y=43 # -> Albania |  90  -> World
      - use_tiles_ignore_pbf=True
      - force_rebuild=False
      - force_rebuild_elevation=False
      - build_elevation=True
      - build_admins=True
      - build_time_zones=True
```
-   `volumes` is mounting a local folder called `custom_files` into the docker container. This is the place where the Valhalla container shares its data and also the place where changes to the running instance can be made.
-   `tile_urls` will be downloaded by Valhalla and build if their file hashes don't match with the existing build tiles. It's possible to add as many urls as desired with a space delimeter. 
-   `min_*` defines the bounding box so Valhalla can download the correct elevation tiles. This is only required if `build_elevation` is set to `True`.
-   `use_tiles_ignore_pbf` will let Valhalla know, that it should prioritize tiles that were already built and not overwrite it.
-   `force_rebuild` will force Valhalla to rebuild the tiles in all cases except for `force_rebuild_elevation`.
-   `force_rebuild_elevation` will always skip rebuilding the elevation data if `False`. That way downloading and processing huge amounts of elevation data can be omitted.
-   `build_*` will let Valhalla know what to build in detail. All of them are optional for a functioning Valhalla instance.


## 2. Run docker-compose.yml


Now let `docker-compose` build Valhalla by typing:
```bash
docker-compose up --build
```
Docker will now pull the latest Valhalla image from the [GIS • OPS Dockerhub](https://hub.docker.com/repository/docker/gisops/valhalla) and build it with the osm file of Albania and Andorra.   

If you check the content of your folder you will notice a new folder named `custom_files`. In there you'll find all the files Valhalla requires to properly run or rebuild any of its data. You can copy, compress, move the folder even to a different system and as long as you use the same `docker-compose.yml`, Valhalla will be able to immediately start with your data.

**Note**: The `build time` can be `more than 15 minutes`, depending on your hardware. To decrease the build time, be aware that `the build process will use all of your available cores`. 
For error messages or warnings see the `Important Notes` section at the end of the tutorial.

## 3. Test Valhalla
### Check the Valhalla docker instance
After Valhalla has been built and started, it should be directly ready to be used. Let's try.
First we're going to verify that Valhalla is running by typing:
```bash
docker ps -a
```   
This will give us an overview of the running docker containers:
```
CONTAINER ID   IMAGE              COMMAND                  CREATED        STATUS        PORTS                    NAMES
370161c6bea7   valhalla_valhalla  "/scripts/run.sh /co…"   9 seconds ago  Up 8 seconds  0.0.0.0:8002->8002/tcp   valhalla_valhalla_1
```   
-   `STATUS` tells us if the service runs successfully if it shows something like `Up x Seconds/Minutes/etc.`.
-   `PORTS` gives us the necessary information to connect to our container. In this case we can connect to Valhalla using the address `0.0.0.0` and the port `8002`.   

If your output includes Valhalla like the example, `you're good to go` to test Valhalla.

### Test Valhalla
Valhalla should be running correctly now, and we're going to test that.  
Open a new terminal and paste the following command:
```bash
curl http://localhost:8002/route --data '{"locations":[{"lat":41.318818,"lon":19.461336},{"lat":41.321001,"lon":19.459598}],"costing":"auto","directions_options":{"units":"miles"}}' | jq '.'
```
-   `curl` will call to the server running at the `localhost` with the port `8002`.
-   `--data` is the switch to present the request data with `curl`.
-   `{"locations":...}` holds the data the Valhalla server will be queried with.
-   `jq '.'` will take the returned JSON response and print it nicely in the console.  
-   If you used another OSM extract replace the `lat` and `lon` variables from the curl command with ones inside your extract.


### Assess the response
The response of your Valhalla server should return something like the following JSON structure, depending on your OSM extract and the used coordinates.
You should change the coordinates to ones that are inside your chosen OSM extract.   
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

---

# Important Notes:
The configuration of Valhalla is tied to many different scopes and may yield some warnings or error messages that you may be concerned about. The following will try to examine some of them for you:   

-   An error resulting off the `valhalla_build_admins` tool:  
```bash
[ERROR] sqlite3_step() error: NOT NULL constraint failed: admin_access.admin_id.  Ignore if not using a planet extract.
```   
This comes up if you build the admin areas on OSM extracts rather than the planet extract. It comes up whenever a relation crosses a border into areas that your OSM extract hasn't got any data. And as the error is telling you, you can safely ignore that.

-   An error telling you that the `SpatiaLite-tool` couldn't `Vacuum` the database holding the time zone data:  
```bash
SQLite version: xxx
SpatiaLite version: xxx
Inserted xxx rows into 'tz_world' from './dist/combined-shapefile-with-oceans.shp'
1
Error: unknown database ANALYZE
VACUUM ANALYZE failed
```   
This seems to be a bug inside the Valhalla script but not a serious one. The only side effect is, that the database will not be `vacuumed` and therefore a bit bigger. It shouldn't affect the building of the tiles. But to be sure keep an eye on the `valhalla_build_tiles` command running successfully.
