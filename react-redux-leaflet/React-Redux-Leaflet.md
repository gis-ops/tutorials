# Building a React/Redux/Leaflet Web(M)app from scratch

![HERE Isoline Routing in New York City](https://user-images.githubusercontent.com/10322094/53686533-95a33c80-3d28-11e9-9f8a-59951bcdfedd.png "HERE Isoline Routing in New York City")

In this tutorial you will learn how to use ReactJS, Redux and Leaflet to create a simple but powerful maps application which is capable of consuming the HERE Isoline Routing API.

Ummmh, so what are isochrone maps exactly good for? Let's have a look what wikipedia says.

*An isochrone map (or chart/diagram) in geography and urban planning is a map showing areas related to isochrones between different points. An isochrone is defined as "a line drawn on a map connecting points at which something occurs or arrives at the same time". Such a map is sometimes termed simply an isochrone (iso = equal, chrone = time) [Wikipedia](https://en.wikipedia.org/wiki/Isochrone_map).*  

This application does exactly this by consuming the useful **HERE Maps Isoline Routing API** to determine areas of reachability from a given point on the globe. 
As a user you have the possibilty to select a magnitude of travelling options, starting from the mode of travel to the specified range and intervals; 
Read moe about the options in the [HERE Maps Isoline Routing Documentation](https://developer.here.com/documentation/routing/topics/resources.html). 

**Note:** In order to use this application, please [register a freemium HERE Maps account](https://developer.here.com/?create=Freemium-Basic&keepState=true&step=account) and input your credentials in the app settings (we will show you where later).

## Prerequisites

To follow this tutorial, you will need the following:

- Knowledge of JavaScript; in particular we will generally be using [ES2016](http://es6-features.org/#Constants).
- A basic understanding of Single-Page-Applications, ReactJS, JSX, Redux and Leaflet. We recommend the following [basic tutorial](https://redux.js.org/introduction/getting-started) which will give you a decent introduction why and how to combine react with redux.
- A shell environment with preinstalled [Node.js](https://nodejs.org/en/download/) giving you the ability to use its package manager `npm` and `npx`.
- A simple text editor such as [Sublime Text](https://www.sublimetext.com/).

## Step 1 - Set up your app folder structure

Open your shell and create your working directory in your home folder (or wherever) which will be used throughout this tutorial.

```sh
mkdir ~/react-redux-leaflet && cd $_
```

We will make use of the handy [create-react-app](https://github.com/facebook/create-react-app) repository which basically provides the skeleton for this tutorial. 
Go ahead and run this command within our working directory: 

```sh
npx create-react-app app
cd app 
```

This will create a new folder named `app`. 
Within you will find a folder `src` holding the source files created for the `create-react-app` tutorial. 
No need for them, so for now please delete all source files as we will replace them with our own step by step.

```sh
rm -rf src/*
```

### Dependencies 

We will now add some dependencies for our app, for instance to be able to use redux and leaflet on top of react; please run the following commands in sequence.

`npm i -S axios chroma-js leaflet prop-types react-redux react-scripts react-semantic-ui-range redux redux-logger redux-thunk semantic-ui-css semantic-ui-react tachyons throttle-debounce`

And some development dependencies, too: 

`npm i -D redux-devtools-extension`

You might be wondering why we need these dependencies... TL;DR:

- (axios, a promise based HTTP client for the browser and node.js)[https://github.com/axios/axios]
- (chroma-js for beautiful color ranges for our polygons)[https://github.com/gka/chroma.js]
- (leaflet for the map & interaction)[https://github.com/Leaflet/Leaflet]
- (semantic ui for beautiful interfaces)[https://react.semantic-ui.com/]
- (tachyons helper css classes, just helpful)[https://tachyons.io/]
...

You might be asking yourself why we aren't using react-leaflet bindings and the reason is simple: you should learn how leaflet works in its very core!

Furthermore we will need some additional folders holding our components as well as actions/reducers for our redux store which will be created in the `src` folder.

```sh
mkdir -p -- src/reducers src/actions src/Map src/Controls
```

You folder structure should now have the following folder layout:

```sh
├── README.md
├── node_modules
│   ├── ...
│   ├── ...
├── package-lock.json
├── package.json
├── public
│   ├── favicon.ico
│   ├── index.html
│   └── manifest.json
├── src
│   ├── Controls
│   ├── Map
│   ├── actions
│   └── reducers
└── yarn.lock
```

We do not have to worry about the public folder but feel free to read more about webpack in general if you are interested how it bundles and builds the application. 

## Step 2 - Let's create a map!

With the first steps in place, we can start getting our hands dirty with the code of our first react components.
Navigate to our `src` folder which will comprise the first couple of javascript source files. 

### index.js

The parent javascript root file from which our application will be started is called `index.js`, so go ahead an create it:


```sh
cd src
touch index.js
```

Now please open `index.js` in your text editor and paste the following code:


```javascript
import React from 'react'
import { render } from 'react-dom'

import { createStore, applyMiddleware } from 'redux'
import { composeWithDevTools } from 'redux-devtools-extension'
import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
import { createLogger } from 'redux-logger'

import reducer from './reducers'
import App from './App'
import './index.css' // postCSS import of CSS module

const middleware = [thunk]

const store = createStore(
  reducer,
  composeWithDevTools(applyMiddleware(...middleware))
)

render(
  <Provider store={store}>
    {' '}
    <App />
  </Provider>,
  document.getElementById('root')
)

```

This file basically creates the entrypoint for the application. 
At the beginning we import the required libraries which are needed, such as react and redux. 
To make your life easy for debugging purposes we also use the [redux-devtools-extension](https://github.com/zalmoxisus/redux-devtools-extension) which provides redux state information in the browser.
We also use the [redux thunk library](https://github.com/reduxjs/redux-thunk) to make the dispatching of actions a little simpler (read more about thunks [on this stackoverflow thread](https://stackoverflow.com/questions/35411423/how-to-dispatch-a-redux-action-with-a-timeout/35415559#35415559)). 

Furthermore we initialize or redux store within the constant `store` which will hold our state and inject our reducer which will be created in the next steps.

The `render` function calls our redux provider with the `App` constant as a child holding the logic and renders it in the root element with the id `root` which can be found in the `public/index.html`. 

Don't be afraid, you will soon be able to connect the dots.

### index.css

Our stylesheets will live in the same folder `src` in a file we will name `index.css` (you can clearly see the import of this file in `index.js` above. 
Go ahead and create the file itself with:

```sh
touch index.css
```

Afterwards paste this css markup:

```css
@import "~semantic-ui-css/semantic.css";
@import "~leaflet/dist/leaflet.css";
@import "~tachyons/css/tachyons.css";

body {
  margin: 0;
  padding: 0;
}
```

As mentioned in the introduction we will make use of [Semantic UI](https://semantic-ui.com/) because of its slick css styles. 
Furthermore we will import leaflet's stylesheet for the map components as well as tachyons to adjust the layout with simple css classes. 
Last but not least: the html body doesn't need a margin or padding; we want the map to use it all.

This leaves us with the following folder structure:

```sh
├── README.md
├── node_modules
│   ├── ...
│   ├── ...
├── package-lock.json
├── package.json
├── public
│   ├── favicon.ico
│   ├── index.html
│   └── manifest.json
├── src
│   ├── Controls
│   ├── Map
│   ├── actions
│   ├── index.css
│   ├── index.js
│   └── reducers
└── yarn.lock
```


### App.jsx

In the previous step we imported the `App` component in `index.js` (if you have forgotton, please go ahead and reassure yourself).
This component however isn't around yet which is why we now have to create a new file which also lives in `src` folder.
This file is very basic and doesn't do much other than importing the map component for now.. which also doesn't exist yet! 
Let's create it now within our `src` folder.


```javascript
import React from 'react'
import Map from './Map/Map'

class App extends React.Component {
  
  render() {
    return (
      <div>
        <Map />
      </div>
    )
  }
}

export default App
``` 

With `App.jsx` in place our folder structure will look something like this:

```sh
├── README.md
├── node_modules
│   ├── ...
│   ├── ...
├── package-lock.json
├── package.json
├── public
│   ├── favicon.ico
│   ├── index.html
│   └── manifest.json
├── src
│   ├── Controls
│   ├── Map
│   ├── actions
│   ├── index.css
│   ├── index.js
│   ├── App.jsx
│   └── reducers
└── yarn.lock
```


### Map.jsx

As the name suggests this component will create our map and handle all of our interactions on it.
Step by step we will add some logic to this component but let's first of all start with basics.
Looking at the code you will notice quite quickly that it looks quite similar to the `App.jsx` component we built above with the major difference that it makes use of our redux store (remember, we will require state). 
We import all required react and react-redux modules as well as leaflet which we use as our mapping library (yes, we could have used openlayers or something similar) and a slighty adapted [HereTileLayer class](https://gitlab.com/IvanSanchez/Leaflet.TileLayer.HERE) to import any kind of map styles **HERE Maps** offers (please find the file in this same repository). 
`Map.jsx` lives in the `Map` folder.

To understand the specific code blocks please read the inline comments.

```javascript
import React from 'react'
import { connect } from 'react-redux'
import L from 'leaflet'
import PropTypes from 'prop-types'

import HereTileLayers from './hereTileLayers'

// defining the container styles the map sits in
const style = {
  width: '100%',
  height: '100vh'
}

// use these or add your own HERE Maps credentials
const hereAppCode = '0XXQyxbiCjVU7jN2URXuhg'
const hereAppId = 'yATlKFDZwdLtjHzyTeCK'

// using the reduced.day map styles, have a look at the imported hereTileLayers for more
const hereReducedDay = HereTileLayers.here({
  appId: hereAppId,
  appCode: hereAppCode,
  scheme: 'reduced.day'
})

// for this app we create two leaflet layer groups to control, one for the isochrone centers and one for the isochrone contours
const markersLayer = L.featureGroup()
const isochronesLayer = L.featureGroup()

// we define our bounds of the map
const southWest = L.latLng(-90, -180),
  northEast = L.latLng(90, 180),
  bounds = L.latLngBounds(southWest, northEast)

// a leaflet map consumes parameters, I'd say they are quite self-explanatory
const mapParams = {
  center: [25.95681, -35.729687],
  zoomControl: false,
  maxBounds: bounds,
  zoom: 2,
  layers: [markersLayer, isochronesLayer, hereReducedDay]
}

// this you have seen before, we define a react component
class Map extends React.Component {

  static propTypes = {
    isochronesControls: PropTypes.object.isRequired,
    mapEvents: PropTypes.object,
    dispatch: PropTypes.func.isRequired
  }
  
  // and once the component has mounted we add everything to it 
  componentDidMount() {

    // our map!
    this.map = L.map('map', mapParams)

    // we create a leaflet pane which will hold all isochrone polygons with a given opacity
    var isochronesPane = this.map.createPane('isochronesPane')
    isochronesPane.style.opacity = 0.9

    // our basemap and add it to the map
    const baseMaps = {
      'HERE reduced.day': hereReducedDay
    }
    L.control.layers(baseMaps).addTo(this.map)

    // we do want a zoom control
    L.control
      .zoom({
        position: 'topright'
      })
      .addTo(this.map)

    // and for the sake of advertising your company, you may add a logo to the map
    const brand = L.control({
      position: 'bottomright'
    })
    brand.onAdd = function(map) {
      var div = L.DomUtil.create('div', 'brand')
      div.innerHTML =
        '<a href="https://gis.ops.com" target="_blank"><img src="http://104.199.51.11:8083/wp-content/uploads/2018/11/gisops.png" width="150px"></img></a>'
      return div
    }
    this.map.addControl(brand)
  }

  // don't forget to render it :-)
  render() {
    return <div id="map" style={style} />
  }
}

// and we already map the redux store to properties which we will start soon
const mapStateToProps = (state) => {
  const isochronesControls = state.isochronesControls
  return {
    isochronesControls
  }
}

export default connect(mapStateToProps)(Map)
```

And to help you keep track of things, this is your new file structure:

```sh
├── README.md
├── node_modules
│   ├── ...
│   ├── ...
├── package-lock.json
├── package.json
├── public
│   ├── favicon.ico
│   ├── index.html
│   └── manifest.json
├── src
│   ├── Controls
│   ├── Map
│   │   ├── Map.jsx
│   │   └── hereTileLayers.js (don't forget to copy this file here)
│   ├── actions
│   ├── index.css
│   ├── index.js
│   ├── App.jsx
│   └── reducers
└── yarn.lock
```


### Creating our initial state

In our map component you will have noticed that we are declaring a constant `mapStateToProps` which is used in the `react-redux connect` function which helps us inject the state into a specific component. 
Our control center of this app will be a little widget with configurable options hovering over the map which will take care of all of our isochrones settings, addresses and isochrones which we will receive from the HERE Maps API. 

To keep a good overview of our state in this tutorial we will add one object to our redux store; its state will be controlled by several actions originating from our control component.

Lets go ahead and 

a) create a empty file `actions.js` in the `actions` folder and 
b) a file `index.js` in the reducers folder holding our state object for the controls. 

The constant `initialIsochronesControlsState` is the initial state object which is initially loaded in `isochronesControls` and later changed depending on the specific action made by the user from the controls and settings.

### reducers/index.js 

```javascript
import { combineReducers } from 'redux'

// these are our initial isochrones settings
const initialIsochronesControlsState = {
  userInput: "",
  geocodeResults: [],
  isochrones: {
    results: []
  },
  isFetching: false,
  isFetchingIsochrones: false,
  settings: {
    isochronesCenter: {},
    range: {
      max: 500,
      value: 60
    },
    interval: {
      max: 60,
      value: 10
    },
    mode: "car",
    rangetype: "distance",
    traffic: "disabled"
  }
}

// our reducer constant returning an unchanged or updated state object depending on the users action, many cases will follow
const isochronesControls = (state = initialIsochronesControlsState, action) => {
  switch (action.type) {
    default:
      return state
  }
}

// creates a root reducer and combines different reducers if needed
const rootReducer = combineReducers({
  isochronesControls
})

export default rootReducer
```

Let's quickly summarize what we have achieved so far. 
If you have followed the tutorial carefully you will have noticed that `src/index.js` is importing the reducer we have just created to initiate the redux store.
The `App` which is being called inside inherently has access to this store and obviously all child components also.
The 2 child components of our app handling all the logic will be our controls (which thus far don't exist) and the map component which has to listen to state changes and accordingly visualize everything on the map.
And guess what: they are talking to each other through our redux store!

Before we go ahead though with creating our controls, let's fire up the map with `npm start`; the following screenshot is what you should see (if you are experiencing an error in your shell then please carefully go through the steps again as you may have missed something crucial).

By the way, if you have installed the redux-devtools plugin in your browser you will be able to access the state object.

![The leaflet map](https://user-images.githubusercontent.com/10322094/52918368-0b051b00-32ee-11e9-97d1-827f3ce57523.png "The leaflet map")


## Step 3 - Let's add controls!

It's time to start with the fun stuff.
To be able to generate isochrones we will need to be able to *geocode* addresses from some input field and set some settings for ranges and intervals.
We will control this logic with a small settings component in the application; therefore please navigate to the `Controls` folder and create a file which we will name `Control.jsx`.

### Control.jsx

Our isochrones control has the following requirements:

1. The ability to input a freeform address
2. The ability to select a result from the found addresses by the HERE Maps API
3. The ability to fire isochrones given some preselected settings and address

This obviously requires some user interaction and as the name suggests we need some ACTIONS which will change our state saved in redux! So let's go ahead and start with the first requirement, namely adding an input field and it's specific actions.
Don't worry too much about the new bits and pieces inside this block of code, you will learn quite quickly what they are doing.
Please carefully go through the code line by line and read the inline comments with explanations.


```javascript
import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

// we are importing some of the beautiful semantic UI react components
import {
  Segment,
  Search,
  Divider,
  Button
} from "semantic-ui-react"

// here are our first two actions, we will be adding them in the next step, bare with me!
import {
  updateTextInput,
  fetchHereGeocode,
  updateCenter
} from "../actions/actions"

// to wait for the users input we will add debounce, this is especially useful for "postponing" the geocode requests 
import { debounce } from "throttle-debounce"

// some inline styles (we should move these to our index.css at one stage)
const segmentStyle = {
  zIndex: 999,
  position: "absolute",
  width: "400px",
  top: "10px",
  left: "10px",
  maxHeight: "calc(100vh - 5vw)",
  overflow: "auto",
  padding: "20px"
};

class Control extends React.Component {
  static propTypes = {
    userTextInput: PropTypes.string.isRequired,
    results: PropTypes.array.isRequired,
    isFetching: PropTypes.bool.isRequired,
    dispatch: PropTypes.func.isRequired,
  }

  constructor(props) {
    super(props)
    // binding this to the handleSearchChange method
    this.handleSearchChange = this.handleSearchChange.bind(this)
    // we are wrapping fetchGeocodeResults in a 1 second debounce
    this.fetchGeocodeResults = debounce(1000, this.fetchGeocodeResults)
  }

  // if the input has changed... fetch some results!
  handleSearchChange = event => {
    const { dispatch } = this.props;

    dispatch(
      updateTextInput({
        inputValue: event.target.value
      })
    )
    this.fetchGeocodeResults()
  }

  // if a user selects one of the geocode results update the input text field and set our center coordinates
  handleResultSelect = (e, { result }) => {
    const { dispatch } = this.props;

    dispatch(
      updateTextInput({
        inputValue: result.title
      })
    );

    dispatch(
      updateCenter({
        isochronesCenter: result.displayposition
      })
    );

  };

  // our method to fire a geocode request
  fetchGeocodeResults() {
    const { dispatch, userTextInput } = this.props
    // If the text input has more then 0 characters..
    if (userTextInput.length > 0) {

      dispatch(
        fetchHereGeocode({
          inputValue: userTextInput
        })
      )
    }
  }

  render() {
    // The following constants are used in our search input which is also a semanticUI react component <Search... />
    const {
      isFetching,
      userTextInput,
      results
    } = this.props

    return (
      <div>
        <Segment style={segmentStyle}>
          <div>
            <span>
              Isochrones powered by <strong>HERE Maps</strong>
            </span>
          </div>
          <Divider />
          {/* they are tachyons css classes by the way..*/}
          <div className="flex justify-between items-center mt3">
            {/* more about the props can be read here https://react.semantic-ui.com/modules/search the most important part to mention here are our objects being fed to it. When a user types text into the input handleSearchChange is called. When the geocode API is called the variable loading will be set true to show the spinner (coming from state). The results are shown in a dropdown list (also coming from the state) and the value shown in the input is userTextInput (..also from state). */}
            <Search
              onSearchChange={this.handleSearchChange}
              onResultSelect={this.handleResultSelect}
              type="text"
              fluid
              input={{ fluid: true }}
              loading={isFetching}
              className="flex-grow-1 mr2"
              results={results}
              value={userTextInput}
              placeholder="Find Address ..."
            />
          </div>
        </Segment>
      </div>
    )
  }
}

// 
const mapStateToProps = state => {
  const userTextInput = state.isochronesControls.userInput
  const results = state.isochronesControls.geocodeResults
  const isFetching = state.isochronesControls.isFetching

  return {
    userTextInput,
    results,
    isFetching
  }
}

export default connect(mapStateToProps)(Control)
```

We are dispatching 2 different events in this class.

1) First of all we want to update our state when the user inputs text.
2) Secondly we want to fire geocoding requests to the HERE Maps API.
3) We want to be able to select a result

Both are mapped to 2 actions which are imported at the beginning of the file - which don't exist yet.
So let's open `actions.js` in the actions folder and add the following code block:

### actions/actions.js

This is probably the most tricky part to wrap your head around, however depending on your prior knowledge of react and redux in general you should understand what is going on quite quickly.
As outline above the actions being called in `Control.jsx` are 

a) `updateTextInput` & 
b) `fetchHereGeocode` &
c) `updateCenter`

which you can all find within this piece of actions code.

The `updateTextInput` action simply forwards the input of the user to the reducer and the `fetchHereGeocode` calls a more complex cascade of events.
When an address is selected by the user, we obviously want to update our isochrones center for further action.

Please find more comprehensive details inline. 

```javascript
...

// use these or add your own credentials
const hereAppCode = '0XXQyxbiCjVU7jN2URXuhg'
const hereAppId = 'yATlKFDZwdLtjHzyTeCK'

export const UPDATE_TEXTINPUT = 'UPDATE_TEXTINPUT'
export const RECEIVE_GEOCODE_RESULTS = 'RECEIVE_GEOCODE_RESULTS'
export const REQUEST_GEOCODE_RESULTS = 'REQUEST_GEOCODE_RESULTS'
export const UPDATE_CENTER = 'UPDATE_CENTER'

export const fetchHereGeocode = payload => dispatch => {

  // It dispatches a further action to let our state know that requests are about to be made (loading spinner listens to this!)
  dispatch(requestGeocodeResults())

  // we define our url and parameters to be sent along
  let url = new URL('https://geocoder.api.here.com/6.2/geocode.json'),
    params = {
      app_id: hereAppId,
      app_code: hereAppCode,
      searchtext: payload.inputValue
    }

  url.search = new URLSearchParams(params)

  // we use the fetch API to call HERE Maps with our parameters
  return fetch(url)
    // when a response is returned we extract the json data
    .then(response => response.json())
    // and this data we dispatch for processing in processGeocodeResponse
    .then(data => dispatch(processGeocodeResponse(data)))
    .catch(error => console.error(error))
}

const parseGeocodeResponse = (json, latLng) => {
  // parsing the response, just a simple example, this could be much more complex as the response from HERE is fairly ritch
  if (json.Response && json.Response.View.length > 0) {
    let processedResults = []

    for (const address of json.Response.View[0].Result) {
      if (address.Location && address.Location.LocationType === 'point') {
        processedResults.push({
          title: address.Location.Address.Label,
          description: address.Location.Address.PostalCode,
          displayposition: {
            lat: address.Location.DisplayPosition.Latitude,
            lng: address.Location.DisplayPosition.Longitude
          }
        })
      }
    }
    return processedResults
  }
}

const processGeocodeResponse = (
  json
) => dispatch => {
  // parse the json file and dispatch the results to receiveGeocodeResults which will be reduced
  const results = parseGeocodeResponse(json)
  // let's let the loading spinner now that it doesn't have to spin anymore
  dispatch(receiveGeocodeResults(results))
}

export const receiveGeocodeResults = payload => ({
  type: RECEIVE_GEOCODE_RESULTS,
  results: payload
})

export const requestGeocodeResults = payload => ({
  type: REQUEST_GEOCODE_RESULTS,
  ...payload
})

export const updateTextInput = payload => ({
  type: UPDATE_TEXTINPUT,
  payload
})

export const updateCenter = payload => ({
   type: UPDATE_CENTER,
   ...payload
})

...
```

The actions are now in place which subsequently have to be reduced. 
To this end, please open your `index.js` in the reducer folder and import these actions right at the beginning of the file

### reducers/index.js

```javascript
...

import {
  UPDATE_TEXTINPUT,
  REQUEST_GEOCODE_RESULTS,
  RECEIVE_GEOCODE_RESULTS,
  UPDATE_CENTER
} from '../actions/actions' 

...
```

And please add the the following cases to our switch clause in order for the reducer to know what to reduce for which action:


```javascript
...

// when a user inputs text we update the userInput :) easy!
case UPDATE_TEXTINPUT:
  return {
    ...state,
    userInput: action.payload.inputValue
  }
// let the app know the request is being made (for our spinner)
case REQUEST_GEOCODE_RESULTS:
  return {
    ...state,
    isFetching: true
  }
// when results are returned by the API update the state with addresses and let the app know it is no longer fetching
case RECEIVE_GEOCODE_RESULTS:
  return {
    ...state,
    geocodeResults: action.results,
    isFetching: false
  }
// update the isochronesCenter we will use later from the coordinates of the selected address 
case UPDATE_CENTER:
  return {
    ...state,
    settings: {
      ...state.settings,
      isochronesCenter: action.isochronesCenter
    }
  }

...
```

To complete this step we have to import the controls to our application.

### App.jsx

a) import the controls with `import Controls from './Controls/Control'`. 
b) and render them with `<Controls />` inside our `<div>...</div>`.

With all the changes in place you browser should update itself automatically.
If it doesn't happen then run `npm start` again.
You will now be able to insert a string which will be geocoded into a list of addresses and once results are returned, you will be able to select one of them.
It should look something like this:

![Geocoded addresses](https://user-images.githubusercontent.com/10322094/53017377-b7a6e000-3447-11e9-850a-07e46bf5e929.png "Geocoded addresses")


## Step 4 - Settings for the user

We now want to provide a rich set of options for the user to control the input parameters for the isochrones.
Let's define some requirements:

1. Ability to select mode pedestrian or car
2. Ability to turn HERE Maps traffic settings on & off for the car profile
3. The range type should be able to handle time or distance
4. We want to set our maximum reachability and the intervals

With some beautiful semantic UI components and and some further actions to adapt the settings we could come up with something that looks like this. 
By the way, to keep this tutorial more or less content, this component is quite large; this being said, usually I would recommend to break this component up into smaller parts.
Please read the inline comments to understand what is going on in the logic.


### Controls/Settings.jsx

```javascript

import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"
import { Slider } from "react-semantic-ui-range"
import { Label, Button, Divider } from "semantic-ui-react"

// we need just one action in this component to update settings made
import { updateSettings } from "../actions/actions"

class Settings extends React.Component {
  
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    controls: PropTypes.object.isRequired
  }

  // dispatches the action
  updateSettings() {
    const { controls, dispatch } = this.props

    dispatch(
      updateSettings({
        settings: controls.settings
      })
    )
  }

  // we are making settings directly in the controls.settings object which is being passed on to the updateSettings() function up top
  handleSettings(settingName, setting) {
    const { controls } = this.props

    controls.settings[settingName] = setting

    this.updateSettings()
  }

  // this looks complex but it isn't, we basically want to make sure the the interval settings maximum can never be greater than the range maximum
  alignRangeInterval() {
    const { controls } = this.props

    if (
      controls.settings.range.value < controls.settings.interval.value ||
      controls.settings.interval.value == ""
    ) {
      controls.settings.interval.value = controls.settings.range.value
    }

    controls.settings.interval.max = controls.settings.range.value
  }

  render() {
    const { controls } = this.props

    // depending on what the user selected we obviously want to show the correct units
    const rangetype =
      controls.settings.rangetype === "time" ? " minutes" : " kilometers"

    // our settings which are needed for the range slider, read more here https://github.com/iozbeyli/react-semantic-ui-range
    const rangeSettings = {
      settings: {
        ...controls.settings.range,
        min: 1,
        step: 1,
        start: controls.settings.range.value,
        // when the slider is moved, we want to update our settings and make sure the maximums align
        onChange: value => {
          controls.settings.range.value = value

          this.alignRangeInterval()
          this.updateSettings()
        }
      }
    }
    // same as above, just for the interval slider this time
    const intervalSettings = {
      settings: {
        ...controls.settings.interval,
        min: 1,
        step: 1,
        start: controls.settings.interval.value,
        onChange: value => {
          controls.settings.interval.value = value
          this.updateSettings()
        }
      }
    }
    // we have different kinds of settings in here. The components should be quite self-explanatory. Whenever a button is clicked we call handleSettings() and this way pass on our setting through to our state.
    return (
      <div className="mt3">
        <Divider />
        <Label size="small">{"Mode of transport"}</Label>
        <div className="mt3">
          <Button.Group basic size="small">
            {Object.keys({ pedestrian: {}, car: {} }).map((key, i) => (
              <Button
                active={key === controls.settings.mode}
                key={i}
                mode={key}
                onClick={() => this.handleSettings("mode", key)}
              >
                {key}
              </Button>
            ))}
          </Button.Group>
          {controls.settings.mode === "car" && (
            <div>
              <Divider />
              <Label size="small">{"Traffic"}</Label>
              <div className="mt3">
                <Button.Group basic size="small">
                  {Object.keys({ enabled: {}, disabled: {} }).map((key, i) => (
                    <Button
                      active={key === controls.settings.traffic}
                      key={i}
                      mode={key}
                      onClick={() => this.handleSettings("traffic", key)}
                    >
                      {key}
                    </Button>
                  ))}
                </Button.Group>
              </div>
            </div>
          )}
        </div>
        <Divider />
        <Label size="small">{"Range type"}</Label>
        <div className="mt3">
          <Button.Group basic size="small">
            {Object.keys({ distance: {}, time: {} }).map((key, i) => (
              <Button
                active={key === controls.settings.rangetype}
                key={i}
                mode={key}
                onClick={() => this.handleSettings("rangetype", key)}
              >
                {key}
              </Button>
            ))}
          </Button.Group>
        </div>
        <Divider />
        <Label size="small">{"Maximum range"}</Label>
        <div className="mt3">
          <Slider
            discrete
            color="grey"
            value={controls.settings.range.value}
            inverted={false}
            settings={rangeSettings.settings}
          />
          <div className="mt2">
            <Label className="mt2" color="grey" size={"mini"}>
              {controls.settings.range.value + rangetype}
            </Label>
          </div>
        </div>
        <Divider />
        <Label size="small">{"Interval step"}</Label>
        <div className="mt3">
          <Slider
            discrete
            color="grey"
            value={controls.settings.interval.value}
            inverted={false}
            settings={intervalSettings.settings}
          />
          <div className="mt2">
            <Label className="mt2" color="grey" size={"mini"}>
              {controls.settings.interval.value + rangetype}
            </Label>
          </div>
        </div>
      </div>
    )
  }
}

const mapStateToProps = state => {
  const controls = state.isochronesControls
  return {
    controls
  }
}

export default connect(mapStateToProps)(Settings)

```

And as you can imagine, we have to now implement our action!

### actions.js

You probably get it by now; 
First of all we will export this action for our reducer..

```javascript

export const UPDATE_SETTINGS = 'UPDATE_SETTINGS'

```

and export it for our settings component to access:

```javascript
...

export const updateSettings = payload => ({
  type: UPDATE_SETTINGS,
  ...payload
})

...
```

Last but not least, we will update our reducer. 

### reducers/index.js

Go ahead and add this snippet:

```javascript
...

case UPDATE_SETTINGS:
  return {
    ...state,
    settings: action.settings
  }

...
```      

How easy? But please don't forget to import the action which by now should look something like this:

```javascript

import {
  UPDATE_TEXTINPUT,
  UPDATE_CENTER,
  REQUEST_GEOCODE_RESULTS,
  RECEIVE_GEOCODE_RESULTS,
  // new
  UPDATE_SETTINGS
} from '../actions/actions'
```
 
You probably are able to guess what comes next.
Import the settings component to our controls and call it, you decide where!

```javascript
import Settings from "./Settings"
```

& 

```javascript
...

<div className="mt2"><Settings /></div>

...
```


With everything in place, you should be able to see the settings component in action which are interactive and thus update the state when selecting them.

![Settings in action](https://user-images.githubusercontent.com/10322094/53034316-d4a0da80-346a-11e9-8c79-69b5ae76af59.png "Settings in action")


## Step 5 - Calling the isochrones API and ploting the result on our map

We are almost there. 
By now we can input an address and make some settings.
The next step is to query the HERE Maps API for some wonderful looking isochrones.
What now is missing is 

a) a button to call the isochrones and 
b) the action behind which ultimately holds some logic to plot the response on our map.


We will handle this logic in our control component.

### Control.jsx

We first of all we should add some new `propTypes` to our component.

```javascript
...
// new
isochronesCenter: PropTypes.object,
isFetchingIsochrones: PropTypes.bool.isRequired

...

```

Additionally we need an to import a new action `fetchHereIsochrones` which yet has to be defined:

```javascript
...

import {
  updateTextInput,
  fetchHereGeocode,
  updateCenter,
  // new
  fetchHereIsochrones
} from "../actions/actions";

...

```

Obviously this action has to be called from a button.. which has to be inserted directly beneath our Search component with a click listener bound to it.
Hence our render function of our controls will look something like this:

```javascript
...

render() {
  const {
    isFetching,
    userTextInput,
    results,
    // new
    settings,
    isFetchingIsochrones
  } = this.props;

  // if an address is selected we will return true to enable our button!
  const isResultSelected = () => {
    if (settings.isochronesCenter.lat && settings.isochronesCenter.lng) return false
    return true
  
  };

  return (
    <div>
      <Segment style={segmentStyle}>
        <div>
          <span>
            Isochrones powered by <strong>HERE Maps</strong>
          </span>
        </div>
        <Divider />
        <div className="flex justify-between items-center mt3">
          <Search
            onSearchChange={this.handleSearchChange}
            onResultSelect={this.handleResultSelect}
            type="text"
            fluid
            input={{ fluid: true }}
            loading={isFetching}
            className="flex-grow-1 mr2"
            results={results}
            value={userTextInput}
            placeholder="Find Address ..."
          />
          <Button
            circular
            loading={isFetchingIsochrones}
            disabled={isResultSelected()}
            color="purple"
            icon="globe"
            onClick={this.handleFetchIsochrones}
          />
        </div>
        <Container className="mt2"><Settings /></Container>
      </Segment>
    </div>
  );
}

```

And our button is calling `handleFetchIsochrones` which looks like:

```javascript
...

handleFetchIsochrones = () => {
  const { dispatch, settings} = this.props;
 
  if (settings.isochronesCenter.lat && settings.isochronesCenter.lng) {
    dispatch(
      fetchHereIsochrones({settings})
    );
  }
};

...

```

And finally don't forget to amend the missing state mappings..

```javascript
...

const mapStateToProps = state => {
  const userTextInput = state.isochronesControls.userInput
  const results = state.isochronesControls.geocodeResults
  const isFetching = state.isochronesControls.isFetching
  
  // new
  const settings = state.isochronesControls.settings
  // new
  const isFetchingIsochrones = state.isochronesControls.isFetchingIsochrones

  return {
    userTextInput,
    results,
    isFetching,
    // new
    settings,
    // new
    isFetchingIsochrones
  };
};

...

```

Clicking the button won't do much at the moment as the actions and reducers are missing.
Similarly to the geocode requests we implemented before, we are calling the HERE isochrones API.
Due to the amount of settings we have created one additional function to help us build the request which is named `processIsolineSettings`.
Read the inline comments for more information.

### actions/actions.js

We are exporting 2 new actions.

```javascript 
...

export const RECEIVE_ISOCHRONES_RESULTS = 'RECEIVE_ISOCHRONES_RESULTS'
export const REQUEST_ISOCHRONES_RESULTS = 'REQUEST_ISOCHRONES_RESULTS'

...
```

```javascript
...

export const fetchHereIsochrones = payload => dispatch => {

  // we let the app know that we are calling the isochrones API 
  dispatch(requestIsochronesResults())

  // we generate our GET parameters from the settigns
  const isolineParameters = processIsolineSettings(payload.settings)

  // as seen before :)
  let url = new URL(
      'https://isoline.route.api.here.com/routing/7.2/calculateisoline.json'
    ),
    params = {
      app_id: hereAppId,
      app_code: hereAppCode,
      ...isolineParameters
    }

  url.search = new URLSearchParams(params)

  return fetch(url)
    .then(response => response.json())
    .then(data =>
      dispatch(processIsochronesResponse(data))
    )
    .catch(error => console.error(error))
}


const parseIsochronesResponse = json => {
  if (json.response && json.response.isoline.length > 0) {
    const isolinesReversed = json.response.isoline.reverse()
    return isolinesReversed
  }
  return []
}

const processIsochronesResponse = (json) => dispatch => {
  // a small trick: we reverse the polygons that the largest comes first :-)
  const results = parseIsochronesResponse(json)

  // we have received our results
  dispatch(receiveIsochronesResults(results))
}


export const receiveIsochronesResults = results => ({
  type: RECEIVE_ISOCHRONES_RESULTS,
  results: results
})

const processIsolineSettings = (settings) => {
  let isolineParameters = {}

  // we prepare the GET parameters according to the HERE Maps Isochrones API docs
  isolineParameters.mode =
    'fastest;' + settings.mode + ';' + 'traffic:' + settings.traffic + ';'
  isolineParameters.rangetype = settings.rangetype

  isolineParameters.start = settings.isochronesCenter.lat + ',' + settings.isochronesCenter.lng

  // seconds
  const ranges = []
  if (settings.rangetype === 'time') {
    let rangeInSeconds = settings.range.value * 60
    const intervalInSeconds = settings.interval.value * 60

    // to generate ranges!
    while (rangeInSeconds > 0) {
      ranges.push(rangeInSeconds)
      rangeInSeconds -= intervalInSeconds
    }

    isolineParameters.range = ranges.join(',')

  // meters
  } else if (settings.rangetype === 'distance') {
    let rangeInMeters = settings.range.value * 1000
    const intervalInMeters = settings.interval.value * 1000

    // to generate ranges!
    while (rangeInMeters > 0) {
      ranges.push(rangeInMeters)
      rangeInMeters -= intervalInMeters
    }

    isolineParameters.range = ranges.join(',')
  }
  return isolineParameters
}

export const requestIsochronesResults = () => ({
  type: REQUEST_ISOCHRONES_RESULTS
})

...
```

To be reduced.

### reducers/index.js

Import the actions:

```javascript

import {
  UPDATE_TEXTINPUT,
  UPDATE_CENTER,
  REQUEST_GEOCODE_RESULTS,
  RECEIVE_GEOCODE_RESULTS,
  UPDATE_SETTINGS,
  // new
  REQUEST_ISOCHRONES_RESULTS,
  // new
  RECEIVE_ISOCHRONES_RESULTS,
} from "../actions/actions"

...
```

And add your reduce cases:

```javascript

...

case REQUEST_ISOCHRONES_RESULTS:
  return {
    ...state,
    isFetchingIsochrones: true
    
  }
case RECEIVE_ISOCHRONES_RESULTS:
  return {
    ...state,
    isFetchingIsochrones: false,
    isochrones: {
      results: action.results
    }
  }

...

``` 

Drum roll... 
Firing requests will now work, so we now merely have to make our map listen to changes in our redux store which will be updated once a response is returned by HERE Maps.


### Map.jsx

Ok, so whenever isochrone results are returned we want to update the map. 
With a handy function every react component can use we can let the map know when the state is updated.
Let's add this to our map component class.

```javascript

componentDidUpdate() {
  this.addIsochronesCenter();
  this.addIsochrones();
}

```

This is obviously calling 2 additional functions.
The first adds a marker to the map... which looks something like this:

```javascript

...

addIsochronesCenter() {
  
  // clear the markers layer beforehand
  markersLayer.clearLayers();

  const isochronesCenter = this.props.isochronesControls.settings
    .isochronesCenter;

  // does this object contain a latitude and longitude?
  if (isochronesCenter.lat && isochronesCenter.lng) {
    // we are creating a leaflet circle marker with a minimal tooltip
    L.circleMarker(isochronesCenter)
      .addTo(markersLayer)
      .bindTooltip(
        "latitude: " +
          isochronesCenter.lat +
          ", " +
          "longitude: " +
          isochronesCenter.lng,
        {
          permanent: false
        }
      )
      .openTooltip();

    // set the map view
    this.map.setView(isochronesCenter, 7);
  }
}

...

```

...and the second handles the visualization of isochrones.
This method uses chromajs which yet has to be imported with `import chroma from 'chroma-js'`.


```javascript
...

addIsochrones() {

  isochronesLayer.clearLayers();

  const isochrones = this.props.isochronesControls.isochrones.results;

  // if we have polygons in our response
  if (isochrones.length > 0) {
    let cnt = 0;

    // let's define a beautiful color range
    const scaleHsl = chroma
      .scale(["#f44242", "#f4be41", "#41f497"])
      .mode("hsl")
      .colors(isochrones.length);

    // looping through all polygons and adding them to the map
    for (const isochrone of isochrones) {
      for (const isochroneComponent of isochrone.component) {
        L.polygon(
          isochroneComponent.shape.map(function(coordString) {
            return coordString.split(",");
          }),
          {
            fillColor: scaleHsl[cnt],
            weight: 2,
            opacity: 1,
            color: "white",
            pane: "isochronesPane"
          }
        ).addTo(isochronesLayer);
      }
      cnt += 1;
    }

    this.map.fitBounds(isochronesLayer.getBounds())
  }
}

...

```

### Wrap-up

At this point you have managed to build a simple web-app based on react, redux and leaflet which fetches and consumes isochrones from HERE Maps, congratulations.
As you may have already gathered from the documentation, the HERE Maps Isochrones API is fairly feature rich and we haven't implemented all of the possible options and features yet.
To this end, if you are interested to enhance the code we built together in this tutorial with new features you might want to have a look at [https://gis-ops.github.io/reachability-analysis](https://gis-ops.github.io/reachability-analysis) which is using the code of this tutorial as a skeleton and building additional options on top. 

If you have ideas how to improve this tutorial or in case something didn't work as you expected please feel free to leave some lovely feedback on our [GitHub](https://github.com/gis-ops/tutorials/issues/new). 

Thanks for working through this tutorial - your GIS-OPS team.

![HERE Isochrones in Iceland](https://user-images.githubusercontent.com/10322094/53057271-9cb78880-34a6-11e9-9204-1dbfb4ad0809.png "HERE Isochrones in Iceland")



