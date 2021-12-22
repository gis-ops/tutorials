# Making OSRM Matrix Computations with its NodeJS Bindings

In this tutorial we would like to demonstrate the power of [Open Source Routing Machine](https://github.com/Project-OSRM/osrm-backend) utilizing its [NodeJS bindings](https://www.npmjs.com/package/osrm) without any overhead of running a service. 
If it's the first time you have heard of bindings, just imagine them as an application programming interface (API) that provides glue code specifically made to allow a programming language to use a foreign library which is not native to that language.
In this scenario our foreign library is OSRM written in C++ which is being consumed by JavaScript.
Additionally, we would like to give you a small taste of how you could optimize for performance when requesting large square matrices.

## Introduction

[Open Source Routing Machine](https://github.com/Project-OSRM/osrm-backend) is a high performance open source routing software (BSD-2-Clause License) written in C++ and mainly designed to consume OpenStreetMap data. 

For a comprehensive feature list and a more general overview of FOSS routing engines, read our [article](https://gis-ops.com/open-source-routing-engines-and-algorithms-an-overview/).

While we are interested in the matrix (table) capabilities, you also have the option to use its other services, too.

- [routing](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/nodejs/api.md#route)
- [matrix](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/nodejs/api.md#table)
- [nearest points](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/nodejs/api.md#nearest)
- [map tiles](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/nodejs/api.md#tile)
- [map matching](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/nodejs/api.md#match)
- [traveling salesman problem](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/nodejs/api.md#trip)

 > **Disclaimer**  
 > Validity only confirmed for **Ubuntu 20.04** / **Mac OSX 10.15.6** and **[OSRM 5.26.0](https://www.npmjs.com/package/osrm)**.

### Recommended

-  A basic understanding of Javascript, NodeJS and npm
-  The awareness that a red printed terminal line doesn't necessarily mean, it's an error ;)...

This tutorial will guide you through the process of how to configure and run the NodeJS bindings for OSRM. 

So let's go, `open your terminal!`

## 1. Preparations

### Test your NodeJS & npm installation

Test whether your environment already has NodeJS installed.

```bash
node -v
```

Similarly test if your environment has Node's package manager npm installed.

```bash
npm -v
```

If either output is similar to this:

```bash
command not found: ...
```

You will have to **install nodejs and/or npm first**. 
To do this have a look at the [How To Install Node.js on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-20-04) or if you are running OSX head over to [Install Node.js and npm using Homebrew on OSX and macOS](https://changelog.com/posts/install-node-js-with-homebrew-on-os-x).


### Create your Working Directory and get NPM ready

First create a working directory:
```bash
mkdir ~/gisops_osrm_nodejs && cd $_
```   

In order to install the required dependencies for this tutorial you will need to copy and paste the following snippet into your [package.json](https://docs.npmjs.com/cli/v8/configuring-npm/package-json) file. 

```bash
{
  "name": "osrm node bindings gis-ops tutorial",
  "version": "0.1",
  "dependencies": {
    "async": "^3.2.2",
    "osrm": "^5.26.0"
  }
}
```

We are making use of 2 libraries [osrm](https://www.npmjs.com/package/osrm) and [async](https://www.npmjs.com/package/async) which will allow us to use the OSRM nodejs bindings in a multithreaded fashion.
With the following command you instruct npm to install these dependencies which will read the `package.json` file sitting in the same folder.

```bash
npm install
```

If you check the contents of your folder you will notice a new folder named `node_modules`. In there you'll find both of these libraries including their dependencies.


## 2. Prepare the OSRM Graph

### Extract & Contract your OSM File

For this demo, we are going to use the OpenStreetMap data of [Berlin](https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf) which you can simply download into your working directory.

`wget https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf`

Afterwards we have to extract the OSM data which is required by OSRM to generate the topology and afterwards contract it which boosts the  performance. 
More can be read [here](https://github.com/Project-OSRM/osrm-backend/wiki/Running-OSRM).
We are using the OSM extract which we just downloaded and using the default `car.lua` file residing in the dependency folder. 
You obviously have the option to change to a different profile or tailor the lua file for your needs. 
Some examples can be found [here](https://github.com/Project-OSRM/osrm-backend/tree/master/profiles).

a. `node_modules/osrm/lib/binding/osrm-extract berlin-latest.osm.pbf -p node_modules/osrm/profiles/car.lua`

b. `node_modules/osrm/lib/binding/osrm-contract berlin-latest.osrm`


## 3. Compute Matrices

### Create a Single OSRM Matrix Request 

Moving forward we will create a small script which will use the NodeJS bindings and prepare a matrix request.
The OSRM method is the main constructor for creating an OSRM instance which requires a `.osrm` dataset.
Afterwards we can construct a request which will be sent to the the `osrm.table` function.  
For the sake of this example we are using a square matrix of 1.000 random coordinates in and around Berlin. 
We ask OSRM for durations and distances and expect a many-to-many response. 

```javascript
// the nodejs bindings
const OSRM = require("osrm");

// importing random coordinates in Berlin used as sources and destinations
const randomCoordinates = require("./random_berlin_coordinates");
const coordinates = randomCoordinates.coordinates1000;

// teaching the bindings to use the osrm graph prepared in the previous step
const osrm = new OSRM("berlin-latest.osrm");

// a small function to create the osrm options
// https://github.com/Project-OSRM/osrm-backend/blob/master/docs/nodejs/api.md
const makeOsrmOptions = (sources, destinations) => {
  return {
    coordinates: coordinates,
    sources: sources || [],
    destinations: destinations || [],
    annotations: ["distance", "duration"]
  }
}

console.time("osrmTableSingleRequest");
const osrmOptions = makeOsrmOptions()
osrm.table(osrmOptions, (err, result) => {
  if (err) {
    console.log(err)
  }
  // console.log(result.durations, result.distances)
  console.timeEnd("osrmTableSingleRequest");
});
```

Depending on the hardware computing this request it will take approximately 1-1.5 seconds to return the matrix result of *1.000.000 pairs*.


### Optimizing your Single Matrix Request

If you want to be a little more adventurous, you can break your large matrix request into bins which will yield a little speed up. 
We can do this with some handy utility functions which we will add to our script moving forward.
The `chunkSize` variable determines how large your sub-matrices should be - we call them bins.
These are created by the `makeBins` function which does nothing other than loops over your many-to-many matrix and sticks ranges into bins. 
With our settings we are creating exactly 4 bins of many-to-many matrices, i.e. `[0-500]` to `[0-500]`, `[0-500]` to `[501-1000]`, `[501-1000]` to `[0-500]` and `[501-1000]` to `[501-1000]`.

```javascript

const chunkSize = 500

const range = (start, end) => {
  return Array(end - start + 1).fill().map((_, idx) => start + idx)
}

const makeBins = (coordinates, chunkSize) => {
  const bins = []
  for (let x=0; x < coordinates.length; x += chunkSize) {
    let endX = x + chunkSize - 1;
    if (endX > coordinates.length - 1) {
      endX = coordinates.length - 1;
    }
    for (let y=0; y < coordinates.length; y += chunkSize) {
        let endY = y + chunkSize - 1;
        if (endY > coordinates.length - 1) {
          endY = coordinates.length - 1;
        }
        bins.push({ sources: range(x, endX), destinations: range(y, endY) })
    }
  }
  return bins;
}

const bins = makeBins(coordinates, chunkSize)
```

At this point we are ready to send off our bins of coordinates. 
We could do this sequentially which wouldn't yield much benefit, however we could also make heavy use of OSRM's powerful architecture of distributing requests across multiple cores.
By default it uses 4 but you have the option to give it more to work with.
There exists a handy NodeJS library called [async](https://www.npmjs.com/package/async) which will help us achieve what we need, namely sending multiple requests to OSRM at once, waiting for all computations to finish and ultimately stitching them back together again.
Specifically we are using one of its core functions [mapLimit](https://caolan.github.io/async/v3/docs.html#mapLimit) to do this. 
We give it all of our bins and a limit parameter (which we call parallelism because it sounds more fancy) governing the maximum number of async operations at a time.
Once all callbacks have been successfully invoked, we can optionally loop over all results and stitch them back together again.


```javascript
/** 
... existing header
 */

const async = require("async");

/** 
... existing code 
 */


// as the name suggestes, it stitches the results back together!
const stitchResults = (results) => {
  // make empty lists which will be filled up
  const durations = Array.from({ length: coordinates.length }).fill().map(item => ([]))
  const distances = Array.from({ length: coordinates.length }).fill().map(item => ([]))
  for (const matrix of results) {
    const minSourceIdx = Math.min(...matrix.sources)
    const minDestIdx = Math.min(...matrix.destinations)
    for (const sourceIdx of matrix.sources) {
      for (const destinationIdx of matrix.destinations ) {
        durations[sourceIdx][destinationIdx] = matrix.durations[sourceIdx - minSourceIdx][destinationIdx - minDestIdx];
        distances[sourceIdx][destinationIdx] = matrix.distances[sourceIdx - minSourceIdx][destinationIdx - minDestIdx];
      }
    }
  }
  return { durations, distances }  
}


// how many requests to have in flight at once
const parallelism = 4

console.time("osrmTableParallel");
async.mapLimit(
  bins,
  parallelism,
  (bin, callback) => {
    // pass in coordinates again but limit osrm.table to compute only sources and destinations of the bin
    const osrmOptions = makeOsrmOptions(coordinates, bin.sources, bin.destinations)

    osrm.table(osrmOptions, (err, result) => {
      if (err) {
        callback(null, result);
      }
      callback(null, { ...result, sources: bin.sources, destinations: bin.destinations } );
    });
  },
  (err, results) => {
    if (err) throw err;
    // if you want to stitch your OSRM computations back together again
    const fullMatrix = stitchResults(results)
    console.timeEnd("osrmTableParallel");
  }
);

```

Depending on your hardware, you will notice that this approach averages around 700-900ms, so approximately 30-50% faster than the single 1.000 x 1.000 request which we started off with. 


