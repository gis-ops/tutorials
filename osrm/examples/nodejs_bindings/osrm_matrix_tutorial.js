// the nodejs bindings
const OSRM = require("osrm");
const async = require("async");
// importing random coordinates in Berlin used as sources and destinations
const randomCoordinates = require("./random_berlin_coordinates");

const coordinates = randomCoordinates.coordinates1000;

// teaching the bindings to use the osrm graph prepared in the previous step
const osrm = new OSRM("berlin-latest.osrm");

// a small function to create the osrm options
// https://github.com/Project-OSRM/osrm-backend/blob/master/docs/nodejs/api.md
const makeOsrmOptions = (coordinates, sources, destinations) => {
  return {
    coordinates: coordinates,
    sources: sources || [],
    destinations: destinations || [],
    annotations: ["distance", "duration"]
  }
}

console.time("osrmTableSingleRequest");
const osrmOptions = makeOsrmOptions(coordinates)
osrm.table(osrmOptions, (err, result) => {
  if (err) {
    console.log(err)
  }
  // console.log(result.durations, result.distances)
  console.timeEnd("osrmTableSingleRequest");
});


/** CHUNKED IMPLEMENTATION */

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

// How many requests to have in flight at once
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
