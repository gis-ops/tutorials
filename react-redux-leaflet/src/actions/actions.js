const hereAppCode = "0XXQyxbiCjVU7jN2URXuhg";
const hereAppId = "yATlKFDZwdLtjHzyTeCK";

export const UPDATE_TEXTINPUT = "UPDATE_TEXTINPUT";
export const RECEIVE_GEOCODE_RESULTS = "RECEIVE_GEOCODE_RESULTS";
export const REQUEST_GEOCODE_RESULTS = "REQUEST_GEOCODE_RESULTS";
export const UPDATE_CENTER = "UPDATE_CENTER";

export const UPDATE_SETTINGS = "UPDATE_SETTINGS";

export const RECEIVE_ISOCHRONES_RESULTS = "RECEIVE_ISOCHRONES_RESULTS";
export const REQUEST_ISOCHRONES_RESULTS = "REQUEST_ISOCHRONES_RESULTS";

export const fetchHereGeocode = payload => dispatch => {
  // It dispatches a further action to let our state know that requests are about to be made
  dispatch(requestGeocodeResults());

  // we define our url and parameters to be sent along
  let url = new URL("https://geocoder.api.here.com/6.2/geocode.json"),
    params = {
      app_id: hereAppId,
      app_code: hereAppCode,
      searchtext: payload.inputValue
    };

  url.search = new URLSearchParams(params);

  // we use the fetch API to call HERE MAps with our parameters
  return (
    fetch(url)
      // when a response is returned we extract the json data
      .then(response => response.json())
      // and this data we dispatch for processing in processGeocodeResponse
      .then(data => dispatch(processGeocodeResponse(data)))
      .catch(error => console.error(error))
  );
};

const parseGeocodeResponse = (json, latLng) => {
  // parsing the response, just a simple example
  if (json.Response && json.Response.View.length > 0) {
    let processedResults = [];

    for (const address of json.Response.View[0].Result) {
      if (address.Location && address.Location.LocationType === "point") {
        processedResults.push({
          title: address.Location.Address.Label,
          description: address.Location.Address.PostalCode,
          displayposition: {
            lat: address.Location.DisplayPosition.Latitude,
            lng: address.Location.DisplayPosition.Longitude
          }
        });
      }
    }
    return processedResults;
  }
};

const processGeocodeResponse = json => dispatch => {
  // parse the json file and dispatch the results to receiveGeocodeResults which will be reduced
  const results = parseGeocodeResponse(json);
  dispatch(receiveGeocodeResults(results));
};

export const receiveGeocodeResults = payload => ({
  type: RECEIVE_GEOCODE_RESULTS,
  results: payload
});

export const requestGeocodeResults = payload => ({
  type: REQUEST_GEOCODE_RESULTS,
  ...payload
});

export const updateTextInput = payload => ({
  type: UPDATE_TEXTINPUT,
  payload
});

export const updateCenter = payload => ({
  type: UPDATE_CENTER,
  ...payload
});

export const updateSettings = payload => ({
  type: UPDATE_SETTINGS,
  ...payload
});

export const fetchHereIsochrones = payload => dispatch => {
  // we let the app know that we are calling the isochrones API
  dispatch(requestIsochronesResults());

  // we generate our GET parameters from the settigns
  const isolineParameters = processIsolineSettings(payload.settings);

  // as seen before :)
  let url = new URL(
      "https://isoline.route.api.here.com/routing/7.2/calculateisoline.json"
    ),
    params = {
      app_id: hereAppId,
      app_code: hereAppCode,
      ...isolineParameters
    };

  url.search = new URLSearchParams(params);

  return fetch(url)
    .then(response => response.json())
    .then(data => dispatch(processIsochronesResponse(data)))
    .catch(error => console.error(error));
};

const parseIsochronesResponse = json => {
  if (json.response && json.response.isoline.length > 0) {
    const isolinesReversed = json.response.isoline.reverse();
    return isolinesReversed;
  }
  return [];
};

const processIsochronesResponse = json => dispatch => {
  // a small trick: we reverse the polygons that the largest comes first :-)
  const results = parseIsochronesResponse(json);

  // we have received our results
  dispatch(receiveIsochronesResults(results));
};

export const receiveIsochronesResults = results => ({
  type: RECEIVE_ISOCHRONES_RESULTS,
  results: results
});

const processIsolineSettings = settings => {
  let isolineParameters = {};

  // we prepare the GET parameters according to the HERE Maps Isochrones API docs
  isolineParameters.mode =
    "fastest;" + settings.mode + ";" + "traffic:" + settings.traffic + ";";
  isolineParameters.rangetype = settings.rangetype;

  isolineParameters.start =
    settings.isochronesCenter.lat + "," + settings.isochronesCenter.lng;

  // seconds
  const ranges = [];
  if (settings.rangetype === "time") {
    let rangeInSeconds = settings.range.value * 60;
    const intervalInSeconds = settings.interval.value * 60;

    // to generate ranges!
    while (rangeInSeconds > 0) {
      ranges.push(rangeInSeconds);
      rangeInSeconds -= intervalInSeconds;
    }

    isolineParameters.range = ranges.join(",");

    // meters
  } else if (settings.rangetype === "distance") {
    let rangeInMeters = settings.range.value * 1000;
    const intervalInMeters = settings.interval.value * 1000;

    // to generate ranges!
    while (rangeInMeters > 0) {
      ranges.push(rangeInMeters);
      rangeInMeters -= intervalInMeters;
    }

    isolineParameters.range = ranges.join(",");
  }
  return isolineParameters;
};

export const requestIsochronesResults = () => ({
  type: REQUEST_ISOCHRONES_RESULTS
});
