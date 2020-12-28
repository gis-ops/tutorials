### Valhalla Tutorials

This tutorial is part of our Valhalla tutorial series:

-   [Valhalla Docker: How to setup and run Valhalla on Ubuntu with Docker](https://gis-ops.com/valhalla-how-to-run-with-docker/)
-   [Valhalla local [Part1]: How to build and install Valhalla on Ubuntu](https://gis-ops.com/valhalla-part-1-how-to-install-on-ubuntu/)
-   [Valhalla local [Part2]: How to configure and run Valhalla locally on Ubuntu](https://gis-ops.com/valhalla-part-2-how-to-run-valhalla-on-ubuntu/)
-   [Valhalla local [Part3]: How to build Valhalla with elevation support on Ubuntu](https://gis-ops.com/valhalla-part-3-how-to-build-with-elevation-support-on-ubuntu/)  

---

# How to build and install Valhalla on Ubuntu 20.04

Learn how to build and install Valhalla from source on Ubuntu 20.04.

## Introduction

[Valhalla](https://github.com/valhalla) is a high-performance open source routing software (MIT license) written in C++ and mainly designed to consume OpenStreetMap data. The core engineers work for [Mapbox](https://www.mapbox.com/) and one of the most prestigious companies using Valhalla is [Tesla](https://tesla.com) as their in-car navigation system.

For a comprehensive feature list and a more general overview of FOSS routing engines, read our [article](https://gis-ops.com/open-source-routing-engines-and-algorithms-an-overview/).

 > **Disclaimer**  
 > Validity only confirmed for **Ubuntu 20.04** and **Valhalla 3.0.9**.

## Recommendations

**Build virtually**: If you're new to building software, **don't try this tutorial on a setup you depend on**. Every system is unique and even if you follow each step correctly in this tutorial, building software from scratch is always bonded to system sensitive tasks and can easily mess around with your live system. Alternatively we recommend you to directly use our [How to setup and run Valhalla on Ubuntu 20.04 in Docker](https://gis-ops.com/valhalla-how-to-run-with-docker/) or run this tutorial in a freshly installed [Ubuntu 18.04 with Virtual Box](https://linuxhint.com/install_ubuntu_18-04_virtualbox/).

**After the tutorial**: If you already have a running version of Valhalla and want to learn more, head over to our tutorial on [How to configure and run Valhalla on Ubuntu](https://gis-ops.com/valhalla-how-to-build-and-install-on-ubuntu/).

## 1. Preparations

In order to build Valhalla on Ubuntu 20.04 you will need to prepare your system with some vital packages.

### Update the system  

First update your systems packages with:

```bash
sudo apt-get update
```

This will give you access to the latest available Ubuntu packages through `apt-get`.

### Install some basic tools

Then you need to install some basic packages. Those packages should be present on a freshly installed Ubuntu 20.04 but just in case they aren't, run the command:

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

-   `cmake` is needed to configure C/C++ projects (supporting CMake like Valhalla) correctly
-   `g++` is the actual c++ compiler you'll use to build Valhalla.
-   `build-essential` holds all the packages needed to build Debian/Ubuntu packages. It serves as the basic package to build from source in Ubuntu.

### Install the remaining dependencies

Then install the rest of the needed dependencies for building the `prime_server` and Valhalla:

```bash
sudo apt-get install -y libsqlite3-mod-spatialite libsqlite3-dev libspatialite-dev \
                        autoconf libtool pkg-config libczmq-dev libzmq5 \
                        libcurl4-openssl-dev zlib1g-dev jq libgeos-dev liblz4-dev \
                        libgeos++-dev libprotobuf-dev protobuf-compiler \
                        libboost-all-dev libluajit-5.1-dev spatialite-bin unzip

```

-   `libsqlite3-mod-spatialite`, `libsqlite3-dev` and `libspatialite-dev` are needed for Valhallas spatial processes to work.
-   `autoconf` and `libtool` hold tools to configure source packages and is needed for Valhalla and `prime_server`.
-   `pkg-config` manages compile and link flags for libraries while building from source. If packages are missing, this one will give you extensive insight into what is missing.
-   `libczmq-dev` and `libzmq5` belong to ZeroMQ and are needed for the building process of the `prime_server`.  
-   `libcurl4-openssl-dev` will be needed to build Valhalla and `prime_server` correctly with curl/ssl capabilities.
-   `zlib1g-dev` is a compression library and is needed by Valhalla.
-   `jq` is a CLI tool to deal with JSON structures.
-   `libgeos-dev`, `libgeos++-dev` belong to a geometry engine for vector operations in C++.
-   `libprotobuf-dev` brings protocol buffer support for C++ and is used for high performance (de-)serialization.
-   `protobuf-compiler` is the compiler for `protobuf` functions and works together with `libprotobuf-dev`.
-   `libboost-all-dev` is a universal C++ library
-   `libluajit-dev` is needed by the build setup to run script files written in Lua.
-   `spatialite-bin` for the spatialite support of Valhalla for building timezone and admin areas.
-   `unzip` for unzipping files. It is used internally by Valhalla.

## 2. Build the `prime_server` dependency

Valhalla, more precisely Kevin Kreiser and colleagues, developed a load-balancing web server to deal with the highly heterogeneous work loads of routing engine APIs, where classic load-balancing would fail.

### Clone the repository

First clone the repository and change inside the newly created directory. Then you should checkout all submodules in order to retrieve linked subgits:

```bash
git clone https://github.com/kevinkreiser/prime_server.git
cd prime_server
git submodule update --init --recursive
```

### Configure the build setup
After that you will stay inside the directory and just run `autogen.sh` and configure the build:

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
-   `make test` runs the tests once the compilation is done, to check if everything compiled correctly.
-   `make install` installs the `prime_server` to the `/usr` directory.
-   The `-j` switch allows you to run the compilation and the tests with as many cores as desired. `-j$(nproc)` uses the system variable to determine the amount of all available cores.
- `-k` tells `make` to keep going even if one (or more) target(s) failed

## 3. Build and install Valhalla

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

This will give us the up-to-date versions of all needed and included submodules. Those are all so-called header-only libraries. They don't need to be compiled, which makes them highly portable and can be included in projects for convenience (some libraries are harder to install on some OSes).

### Finally: Build and install Valhalla
If you reached this point without errors, you're good to go to build Valhalla. Make sure you set `DENABLE_NODE_BINDINGS` to `On` if you want Valhalla to build with Node support:

```bash
mkdir build
cd $_
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/usr \
  -DENABLE_TOOLS=OFF \
  -DENABLE_TESTS=OFF \
  -DENABLE_BENCHMARKS=OFF
```
-   `cmake ..` configures the build for `make` (writes some config files)
-   `-DCMAKE_BUILD_TYPE=Release ` will make the compiler compile the Release version.
-   `-DCMAKE_INSTALL_PREFIX=/usr ` makes sure Valhalla is installed to the `/usr` path.
- the `-DENABLE_XY` configs tell CMake to skip some modules mostly required for Valhalla development/testing

If you made it to this point... **Congratulations!** You're ready to insert the last commands to build and install Valhalla:

```bash
cd build
make -j$(nproc)
# make -j$(nproc) check
make install
```

-   `make -j$(nproc)` compiles Valhalla with all available cores
-   `make -j$(nproc) check` runs the Valhalla tests with all available cores. This is optional and takes a lot more time than the simple `make` step. If Valhalla configured and built without errors, you can assume the runtime is fine too, so you can skip this check.
-   `make install` installs Valhalla to your system (`/usr` directory you configured with CMake)

## Next steps:

Now that Valhalla is successfully running in Ubuntu 20.04, head over to our Tutorial [*How to configure and run Valhalla on Ubuntu 20.04*](https://gis-ops.com/valhalla-how-to-run-on-ubuntu-20-04/).
