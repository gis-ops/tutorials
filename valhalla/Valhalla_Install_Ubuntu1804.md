### Valhalla Tutorials
This Tutorial is part of our [Valhalla tutorial series](https://github.com/gis-ops/tutorials/tree/master/valhalla):

-   [How to build and install Valhalla on Ubuntu 18.04](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_Install_Ubuntu1804.md)
-   [How to configure and run Valhalla locally on Ubuntu 18.04](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_configure_use_local.md)
-   [How to setup and run Valhalla on Ubuntu 18.04 in Docker](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_setup_run_docker.md)

---

# How to build and install Valhalla on Ubuntu 18.04

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

-   get familiar with building software on Ubuntu 18.04
-   learn how to build and install Valhalla correctly
-   some new things about how to use Ubuntu and Linux in general ;)...  


 > **Disclaimer**  
 > Validity only confirmed for **Ubuntu 18.04** and **Valhalla 3.0.2**.  
 > Building and installing software from scratch is always a difficult and unforeseeable task that may render your running system or the software unusable. You may continue this tutorial at your own responsibility.

**Basic vocabulary**
-   `cli` means `command line interface` and refers to tools that can be controlled through commands that you type into your terminal.
-   `OS` means `Operating System` and refers to the system you will run the following steps in.

---

## Prerequisites

### Hard prerequisites
-   A basic understanding of Ubuntu
-   That's it (and remember: a red printed terminal line doesn't necessarily mean, it's an error ;))

### Recommendations

**Build virtually**: If you're new to building software, **don't try this tutorial on a setup you depend on**. Every system is unique and even if you follow each step correctly in this tutorial, building software from scratch is always bonded to system sensitive tasks and can easily mess around with your live system.  
Alternatively we recommend you to directly use our [How to setup and run Valhalla on Ubuntu 18.04 in Docker](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_setup_run_docker.md) or run this tutorial in a freshly installed [Ubuntu 18.04 with Virtual Box](https://linuxhint.com/install_ubuntu_18-04_virtualbox/).

### After the tutorial:
If you already have a running version of Valhalla and want to learn more, head over to our tutorial on [How to configure and run Valhalla on Ubuntu 18.04](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_configure_use_local.md).

---

If you have read to this line I assume you're interested in building and installing Valhalla.
The following steps will guide you through the whole process and should cover all necessary details.
In order to build Valhalla on Ubuntu 18.04, you will also need to build an extra dependency called `prime_server` besides Valhalla itself. So don't be confused ;).

## 1. Create a temporary folder
First you should create a temporary folder, where all the magic will happen:
```bash
mkdir ~/building_valhalla && cd $_
```  
-   `mkdir ~/building_valhalla` is the command to create the folder called `building_valhalla` in our home folder `~/`.
-   `cd $_` changes the terminal path directly to the newly created folder. `$_` is a system variable and holds the output of the last command line call. In this case the path to the newly created folder.

## 2. Preparations
In order to build Valhalla on Ubuntu 18.04 you will need to prepare your system with some vital packages:

### Update the system  
First update your systems packages with:
```bash
sudo apt-get update
```
This will give you access to the latest available Ubuntu packages through `apt-get`.

### Install some basic tools
Then you need to install some basic packages. Those packages should be present on a freshly installed Ubuntu 18.04 but just in case they aren't, run the command:

```bash
sudo apt-get install -y git wget curl ca-certificates gnupg2
```

-   `git` in order to clone repositories from GitHub.
-   `wget` and `curl` are handy tools to download nearly anything from any source through the cli.  
-   `ca-certificates` and `gnupg2` gives you the tools needed to load and verify packages from third-party sources.

### Install the C++ toolchain
Now you need to install the C++ toolchain. This will give us the basic tools to successfully build and install software, written in C++:

```bash
sudo apt-get install -y cmake build-essential
```

-   `cmake` is needed to configure cmake projects correctly, in this case Valhalla.
-   `g++` is the actual c++ compiler and will be needed to build Valhalla.
-   `build-essential` holds all the packages needed to build Debian/Ubuntu packages. It serves as the basic package to build from source in Ubuntu.

### Install the remaining dependencies
Then install the rest of the needed dependencies for building the `prime_server` and Valhalla:

```bash
sudo apt-get install -y libsqlite3-mod-spatialite libsqlite3-dev libspatialite-dev \
                        autoconf libtool pkg-config libczmq-dev libzmq5 \
                        libcurl4-openssl-dev zlib1g-dev jq libgeos-dev \
                        libgeos++-dev libprotobuf-dev protobuf-compiler \
                        libboost-all-dev liblua5.2-dev spatialite-bin unzip

```

-   `libsqlite3-mod-spatialite`, `libsqlite3-dev` and `libspatialite-dev` are needed for Valhallas spatial processes to work.
-   `autoconf` and `libtool` hold tools to configure source packages and is needed for Valhalla and `prime_server`.
-   `pkg-config` manages compile and link flags for libraries while building from source. If packages are missing, this one will give you extensive insight into what is missing.
-   `libczmq-dev` and `libzmq5` belong to the `ZeroMQ` package and are needed for the building process of the `prime_server`.  
-   `libcurl4-openssl-dev` will be needed to build the `prime_server` correctly with curl/ssl capabilities.
-   `zlib1g-dev` is a compression library and is needed by Valhalla.
-   `jq` is a cli tool to deal with JSON structures.
-   `libgeos-dev`, `libgeos++-dev` belong to a geometry engine for GIS operations in C++.
-   `libprotobuf-dev` brings protocol buffer support for C++ and is used for high performance communication.
-   `protobuf-compiler` is the compiler for `protobuf` functions and works together with `libprotobuf-dev`.
-   `libboost-all-dev` is needed by Valhalla to deal with graph and storage related tasks.
-   `liblua5.2-dev` is needed by the build setup to run script files written in Lua.
-   `spatialite-bin` for the spatialite support of Valhalla for building timezone and admin areas.
-   `unzip` for unzipping files. It is used internally by Valhalla.

## 3. Fix the Ubuntu 18.04 exclusive `sqlite3-mod-spatialite` bug
Ubuntu 18.04 has a bug of not linking `sqlite3-mod-spatialite` to the folder where Valhalla will look for it.
In order to let Valhalla see this extension, you need to create a symbolic link to the correct folder:

```bash
sudo ln -s /usr/lib/x86_64-linux-gnu/mod_spatialite.so /usr/lib/mod_spatialite
```

Now Valhalla should be able to correctly resolve the `sqlite3-mod-spatialite` extensions location once it is building.

## 4. Build the `prime_server` dependency
### Needed dependencies
In order to correctly build the `prime_server` make sure you have installed the `libczmq-dev` and `libzmq5` packages!

### Clone the repository
First clone the repository and change inside the newly created directory. Then you should checkout all submodules in order to retrieve linked subgits:

```bash
git clone https://github.com/kevinkreiser/prime_server.git
cd prime_server
git submodule update --init --recursive
```

### Configure the build setup
After that you will stay inside the directory and just run autogen.sh and configure the build:

```bash
./autogen.sh
./configure --prefix=/usr LIBS="-lpthread"
```

-   `autogen.sh` will generate the source code to a compilable data source.
-   `configure` will check if the ready-to-compile data set is suitable for the current system and if all dependencies are fulfilled.
-   `--prefix=/usr` and `LIBS="-lpthread"` will make sure that the `prime_server` is installed to the user directory and that the dependency `lpthread` is correctly linked to the build files.

### Build and install the `prime_server`
If the configure command finishes without any errors, you are ready to build the `prime_server`. Again, you will stay inside the same directory and just call the following commands to finally build and install the `prime_server`:
```bash
make all -j$(nproc)
make -j$(nproc) -k test
make install
cd ../
```
-   `make all` compiles everything that is inside the current folder.
-   `make -k test` runs the tests once the compilation is done, to check if everything compiled correctly.
-   `make install` installs the `prime_server` to the `/usr` directory.
-   `cd ../` changes one directory level up to our default folder.
-   The `-j` switch allows you to run the compilation and the tests with as many cores as desired.
In the example I added a `-j$(nproc)` to use all available cores. The `$(nproc)` system variable automatically returns all the available cores for your CPU.
If you want to change that for some reason, you can easily set it to a different number.
The number shouldn't be higher than the maximum number of cores your CPU has.
E.g. for a quad core processor don't go higher than `-j4`...

## 5. Build and install Valhalla
If everything worked without error until this point, you're good to go to finally build Valhalla.

### Clone the repository and update the submodules
Now you need to clone the Valhalla repository from GitHub and `cd` into the newly created folder:

```bash
git clone https://github.com/valhalla/valhalla
cd valhalla
```   

After that, sync and update the submodules:
```bash
git submodule sync
git submodule update --init --recursive
```
This will give us the up-to-date versions of all needed and included submodules, `OSM-binary`, `OSMLR`, `date`, `dirent` and `rapidjson`.

### Optional: Install node for Valhalla node support
If you want to enable the experimental node support in Valhalla you need to setup Node first:

```bash
curl -o- curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[[ -s "$NVM_DIR/nvm.sh" ]] && \. "$NVM_DIR/nvm.sh"
nvm install 10.15.0 && nvm use 10.15.0
npm install --ignore-scripts --unsafe-perm=true
ln -s ~/.nvm/versions/node/v10.15.0/include/node/node.h /usr/include/node.h
ln -s ~/.nvm/versions/node/v10.15.0/include/node/uv.h /usr/include/uv.h
ln -s ~/.nvm/versions/node/v10.15.0/include/node/v8.h /usr/include/v8.h

```

-   `curl -o- ... | bash` will download and execute the `nvm` installation
-   `export NVM_DIR="$HOME/.nvm"` will give your cli access to the `nvm` commands
-   `[[ -s "$NVM_DIR/nvm.sh" ]] && \. "$NVM_DIR/nvm.sh" ` will activate `nvm`
-   `nvm install 10 && nvm use 10` will install node 10 and change it to the standard node version
-   `npm install --ignore-scripts --unsafe-perm=true` will install the Valhalla Node bindings. `--unsafe-perm=true` is set to avoid problems executing as a non root user
-   `ln -s ...` will link the node modules to the `/usr/include/` folder where Valhalla is going to look for them.

### Finally: Build and install Valhalla
If you reached this point without errors, you're good to go to build Valhalla. Make sure you set `DENABLE_NODE_BINDINGS` to `On` if you want Valhalla to build with Node support:

```bash
mkdir build
cmake . -Bbuild \
  -DCMAKE_C_FLAGS:STRING="${CFLAGS}" \
  -DCMAKE_CXX_FLAGS:STRING="${CXXFLAGS}" \
  -DCMAKE_EXE_LINKER_FLAGS:STRING="${LDFLAGS}" \
  -DCMAKE_INSTALL_LIBDIR=lib \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/usr \
  -DENABLE_DATA_TOOLS=On \
  -DENABLE_PYTHON_BINDINGS=On \
  -DENABLE_NODE_BINDINGS=Off \
  -DENABLE_SERVICES=On \
  -DENABLE_HTTP=On
```

-   `mkdir build` creates a new folder where the build files will be written to.  
-   `cmake . -Bbuild` calls to cmake to build `-Bbuild` in the current folder `.`.
-   `DCMAKE_C_FLAGS:STRING="${CFLAGS}" ` sets the default options for c compiler.
-   `DCMAKE_CXX_FLAGS:STRING="${CXXFLAGS}" ` sets the default options for C++.
-   `DCMAKE_EXE_LINKER_FLAGS:STRING="${LDFLAGS}" ` makes sure all internal C links are correctly resolved and set.
-   `DCMAKE_INSTALL_LIBDIR=lib ` makes sure libraries are installed to the correct library folder. `lib` is standard in UNIX.
-   `DCMAKE_BUILD_TYPE=Release ` will make the compiler compile the Release version.
-   `DCMAKE_INSTALL_PREFIX=/usr ` makes sure Valhalla is installed to the `usr` path.
-   `DENABLE_DATA_TOOLS=On ` installs all Valhalla data preprocessing tools: `valhalla_build_statistics`, `valhalla_ways_to_edges`, `valhalla_validate_transit`, `valhalla_benchmark_admins`, `valhalla_build_connectivity`, `valhalla_build_tiles`, `valhalla_build_admins`, `valhalla_convert_transit`.
-   `DENABLE_PYTHON_BINDINGS=On ` builds the Python bindings.
-   `DENABLE_NODE_BINDINGS=Off ` builds the NodeJs bindings. Make sure you turned it to **`On`** if you want Node support and installed the optional node modules!
-   `DENABLE_SERVICES=On ` installs the services: `valhalla_loki_worker`, `valhalla_odin_worker` and `valhalla_thor_worker`.
-   `DENABLE_HTTP=On ` enables downloads with the download tool `curl`.

If you made it to this point... **Congratulations!** You're ready to insert the last commands to build and install Valhalla:

```bash
cd build
make -j$(nproc)
make -j$(nproc) check
make install
```

-   `cd build` changes the path to the `build` directory
-   `make -j$(nproc)` compiles Valhalla with all available cores
-   `make -j$(nproc) check` runs the Valhalla tests with all available cores. **Keep a close eye to the successful run of all tests!**
-   `make install` installs Valhalla to your system  

---

## Next steps:
Now that Valhalla is successfully running in Ubuntu 18.04, head over to our Tutorial [*How to configure and run Valhalla on Ubuntu 18.04*](https://github.com/gis-ops/tutorials/blob/master/valhalla/Valhalla_configure_use_local.md).

## Troubleshooting
The release of Ubuntu 18.04 has changed a few system side things. Thankfully Valhalla is a well programmed and designed piece of software and will deal with the most differences and will keep the user informed.

Here is a list of possible warnings and information that you may encounter:

-   The compiler might scream around about not finding the node module at
first:
```
ERROR - node.h not found
ERROR - v8.h not found
ERROR - uv.h not found
-- Could NOT find Nodejs (missing: NODEJS_INCLUDE_DIRS) (found version "8.11.2")
-- Found v8: V8_ROOT_DIR-NOTFOUND/v8.h (found version "6.2.414.54")
-- Configuring done
-- Generating done
...
```
You should recheck if you linked the node modules correctly in the section [Optional: Install node for Valhalla node support](#optional-install-node-for-valhalla-node-support).
Anyway, you should **have an extra eye** on the `make check` running successfully
and showing you:
```
[PASS] nodeinfo
[ 95%] Built target run-nodeinfo
```  

-   While building `prime_server` you may encounter a line telling you:
```bash
u modifier ignored since D is the default (see U)
```
This comes from the fact that `prime_server` uses a deprecated compilation flag when calling the library `libtool`. This is okay because `libtool` automatically links to the new flag and is just warning about it  

-   Another possible warning could come from libprotobuf:
```
[libprotobuf WARNING google/protobuf/compiler/parser.cc:547]
No syntax specified for the proto file: fileformat.proto.
Please use 'syntax = "proto2";' or 'syntax = "proto3";'
to specify a syntax version. (Defaulted to proto2 syntax.)
```
That is a simple information telling you that one file isn't correctly importing the `protobuf` settings parameter and that `protobuf` defaulted to a specific setting. That is fine and will not affect the build and install process, so ignore it.
**But again, keep a close eye on the tests.**
