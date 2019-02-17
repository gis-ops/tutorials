# Building a React/Redux Leaflet Web(M)app from scratch

![HERE Isoline Routing in Istanbul](https://user-images.githubusercontent.com/10322094/51332346-df3b0f00-1a7b-11e9-82e6-abd7eb397545.png "HERE Isoline Routing in Istanbul")

In this tutorial you will learn how to use ReactJS, Redux and Leaflet to create a simple but powerful maps application which is capable of consuming the HERE Isoline Routing API.

So what are isochrone maps exactly good for? 

*An isochrone map (or chart/diagram) in geography and urban planning is a map showing areas related to isochrones between different points. An isochrone is defined as "a line drawn on a map connecting points at which something occurs or arrives at the same time". Such a map is sometimes termed simply an isochrone (iso = equal, chrone = time) [Wikipedia](https://en.wikipedia.org/wiki/Isochrone_map).*

This application consumes the useful HERE Maps Isoline Routing API to determine areas of reachability from a given point. As a user you have the possibilty to select a magnitude of travelling options, starting from the mode of travel to the specified range and intervals [HERE Maps Isoline Routing Options](https://developer.here.com/documentation/routing/topics/resources.html). 

**Note:** In order to use this application, please [register a freemium HERE Maps account](https://developer.here.com/?create=Freemium-Basic&keepState=true&step=account) and input your credentials in the app settings.

### Prerequisites

To follow this tutorial, you will need the following:

- Knowledge of JavaScript; in particular we will generally be using [ES2016](http://es6-features.org/#Constants) 
- A basic understanding of Single-Page-Applications, ReactJS, JSX, Redux and Leaflet. We recommend the following [basic tutorial](https://redux.js.org/introduction/getting-started) which will give you a decent understanding why and how to combine React and Redux.
- A shell environment with [Node.js](https://nodejs.org/en/download/) installed giving you the ability to use its package manager `npm` as well as an editor such as [Sublime Text](https://www.sublimetext.com/) 

## Step 1 - Setting up your app folder structure

Open your shell and create your working directory which will be used throughout this tutorial.

```sh
mkdir ~/react-redux-leaflet && cd $_
```

We will make use of the handy [create-react-app](https://github.com/facebook/create-react-app) which basically provides the skeleton for this tutorial. 
Within our working directory run the following command: 

```sh
npx create-react-app app
cd app 
```

This will create a new folder named `app`. 
Within you will find a folder `src` holding the source files. 
Fow now please delete all files within as we will replace them with our own.

```sh
rm -rf src/*
```

We will now add some further dependencies to our environment to be able to use Redux and Leaflet.

`npm i -S axios chroma-js leaflet prop-types react-edit-inline2 react-redux react-scripts react-semantic-ui-range redux redux-logger redux-thunk semantic-ui-css semantic-ui-react tachyons throttle-debounce`

And some development dependencies: 

`npm i -D redux-devtools-extension`

Some quick explanations what some of these packages are good for:

- (axios, a promise based HTTP client for the browser and node.js)[https://github.com/axios/axios]
- (chroma-js for beautiful color ranges)[https://github.com/gka/chroma.js]
- (leaflet for the map interaction)[https://github.com/Leaflet/Leaflet]
- (react edit inline to edit text in the browser)[https://github.com/kaivi/ReactInlineEdit#readme]
- (semantic ui for beautiful interfaces)[https://react.semantic-ui.com/]
- (tachyons helper css classes, just helpful)[https://tachyons.io/]
...


Furthermore we will need some additional folders to hold our actions and reducers for our Redux store.

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

## Step 2 - Let's create a map!

With the first steps in place, we can start getting our hands dirty with the code.
We will use our `src` folder which will hold the first couple of source files. 

### index.js

The parent javascript root from which our application will be started is `index.js`, so go ahead an create it already.


```sh
touch src/index.js
```


Let's open `index.js` and paste the following code.


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

This basically creates the entrypoint for the application. 
We import the required libraries which are needed, such as React and Redux. 
To make your life easy for debugging we also use the [redux-devtools-extension](https://github.com/zalmoxisus/redux-devtools-extension) which provides redux state information in the browser.
We also use the [Redux thunk library](https://github.com/reduxjs/redux-thunk) to make the dispatching of actions a little simpler (read more about thunks [on this stackoverflow thread](https://stackoverflow.com/questions/35411423/how-to-dispatch-a-redux-action-with-a-timeout/35415559#35415559)). 

Furthermore we initialize or Redux store within the const `store` which will hold our state and inject our reducer which will be created in the next step.

The `render` function calls our Redux Provider with the `App` constant as a child holding the logic and renders it in the root element with the id `root` which can be found in the `public/index.html`. 


### index.css

Our stylesheets will live in the same folder within `index.css`. 
So now go ahead and create the file itself with

```sh
touch src/index.js
```

Afterwards feel free to paste this css markup:

```css
@import "~semantic-ui-css/semantic.css";
@import "~leaflet/dist/leaflet.css";
@import "~tachyons/css/tachyons.css";

body {
  margin: 0;
  padding: 0;
}
```

As mentioned in the introduction we will make ue of [Semantic UI](https://semantic-ui.com/) because of their slick styles. 
Furthermore we will import leaflet's stylesheet for the map components as well as tachyons to adjust the layout with simple css classes. 
The html body doesn't need a margin or padding; we want the map to use it all.

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

So, we imported the `App` class in `index.js`. 
So go ahead an create the file which also lives in `src` folder.
You will need the following javascript snippet which does now for the first time consumes our Redux store.  
We make use of [prop-types](https://github.com/facebook/prop-types) which will guide us a little if we are working with incompatible data types; quite helpful!
The react component class has a `componentDidUpdate` function which will be called if the state changes. 
It also has the `render` function which returns a div holding the Map container. 
So we are almost there to get our first map component ready to show in the browser - bare with me!
Last but not least we connect this component with our App with the Redux store to make use of the `resultHandler` state which we will need to make the UX of our ajax calls a little slicker.  


```javascript
import React from 'react'
import PropTypes from 'prop-types'

import Map from './Map/Map'

class App extends React.Component {
  static propTypes = {
    resultHandler: PropTypes.object
  }

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

As the name suggests this component visualizes all of our interactions on the map.
Step by step we will add some logic to this component but let's first of all start with a basic map.
Looking at the code you will notice quite quickly that it looks quite similar to the `App.jsx` component we built above. 
We import all required react and react-redux modules, leaflet which we use as our mapping library (yes, we could also use openlayers or something similar) and a re-written (HereTileLayer class)[https://gitlab.com/IvanSanchez/Leaflet.TileLayer.HERE] to import any kind of map styles HERE Maps offers.
To understand the specific code blocks please the inline comments as we go forward.

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

// using the reduced.day map styles, have a look at the imported hereTileLayers for more
const hereReducedDay = HereTileLayer.here({
  appId: 'jKco7gLGf0WWlvS5n2fl',
  appCode: 'HQnCztY23zh2xiTPCFiTMA',
  scheme: 'reduced.day'
})

// for this app we create two leaflet layer groups to control, one for the isochrone centers and one for the isochrone contours
const markersLayer = L.layerGroup()
const isochronesLayer = L.layerGroup()

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
    isochronesControls: PropTypes.array.isRequired,
    mapEvents: PropTypes.object,
    hereConfig: PropTypes.object,
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
        '<a href="https://gis.ops.com" target="_blank"><div class="gis-ops-logo"></div></a>'
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
const mapStateToProps = (state, ownProps) => {
  const isochronesControls = state.isochronesControls.controls
  const mapEvents = state.mapEvents
  return {
    isochronesControls,
    //mapEvents,
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
│   │   └── hereTileLayers.js
│   ├── actions
│   ├── index.css
│   ├── index.js
│   ├── App.jsx
│   └── reducers
└── yarn.lock
```


### Hooking up our controls with actions and reducers

In all of our components so far you will have noticed that we are declaring a constant `mapStateToProps` which is used in the `react-redux connect` function which helps us inject the state into the specific components. 
Our "control center" of this app will be a little widget with configurable options hovering over the map which will take care of all of our isochrones settings, addresses and isolines we will receive from the HERE Maps API. 
To this end and to keep a good overview of everything we will add one object to our redux store; its state will be controlled by several actions.

Lets go ahead and create a empty file `actions.js` in the actions folder and a file `index.js` in the reducers folder holding our state object for the controls. 
The constant `initialIsochronesControlsState` is the initial state object used in `isochronesControls` which is initially loaded in `isochronesControls` and later changed depending on the specific action made by the user (which we will step by step add to our controls and redux actions).

```javascript
import { combineReducers } from 'redux'

// these are our initial isochrones settings
const initialIsochronesControlsState = {
    userInput: '',
    geocodeResults: [],
    isochrones: {
      receivedAt: null,
      results: []
    },
    isFetching: false,
    isFetchingIsochrones: false,
    settings : {
      range: {
        min: 1,
        max: 500,
        step: 1,
        value: 60
      },
      interval: {
        min: 1,
        max: 60,
        step: 1,
        value: 10
      },
      mode: 'car',
      rangetype: 'distance',
      direction: 'start',
      traffic: 'disabled'
    }
}

// our reducer constant returning an unchanged or updated state object depending on the users action
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
If you have followed the tutorial carefully so far, you will have noticed that `index.js` is trying to import the reducer we have just created to initiate the redux store.
The `App` which is being called inside inherently has access to this store and obviously all child components also.
The 2 child components of our app handling all the logic will be our controls (which thus far don't exist) and the map component which has to listen to state changes and accordingly visualize everything on the map.
And guess what, they are talking to each other through our redux store!

Before we go ahead, let's fire up the map with `npm start`; this is what you should see. 
If you are experiencing an error in your shell then please carefully go through the steps again as you may have missed something crucial.



# Step 3 - Controls!







