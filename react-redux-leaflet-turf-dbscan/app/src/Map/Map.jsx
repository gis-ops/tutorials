import React from 'react'
import { connect } from 'react-redux'
import L from 'leaflet'
//import _ from 'lodash'
import PropTypes from 'prop-types'
import {
  //nearest,
  clustersDbscan,
  concave,
  point,
  featureCollection
} from '@turf/turf'
import { doUpdateBoundingBox } from '../actions/actions'

import HereTileLayers from './hereTileLayers'

import chroma from 'chroma-js'

// defining the container styles the map sits in
const style = {
  width: '100%',
  height: '100vh'
}

// using the reduced.day map styles, have a look at the imported hereTileLayers for more
const hereReducedDay = HereTileLayers.here({
  appId: 'jKco7gLGf0WWlvS5n2fl',
  appCode: 'HQnCztY23zh2xiTPCFiTMA',
  scheme: 'reduced.day'
})

// for this app we create two leaflet layer groups to control, one for the isochrone centers and one for the isochrone contours
const placesLayer = L.featureGroup()
const clusterLayer = L.featureGroup()

// we define our bounds of the map
const southWest = L.latLng(-90, -180)

const northEast = L.latLng(90, 180)

const bounds = L.latLngBounds(southWest, northEast)

// a leaflet map consumes parameters, I'd say they are quite self-explanatory
const mapParams = {
  center: [40.7569, -73.9837],
  zoomControl: false,
  maxBounds: bounds,
  zoom: 13,
  layers: [placesLayer, clusterLayer, hereReducedDay]
}

// this you have seen before, we define a react component
class Map extends React.Component {
  static propTypes = {
    lastCall: PropTypes.number,
    lastCompute: PropTypes.number,
    dbscanSettings: PropTypes.object,
    dispatch: PropTypes.func.isRequired,
    places: PropTypes.array
  }

  // and once the component has mounted we add everything to it
  componentDidMount() {
    // our map!

    const { dispatch } = this.props

    this.map = L.map('map', mapParams)

    // we create a leaflet pane which will hold all isochrone polygons with a given opacity
    const clusterPane = this.map.createPane('clusterPane')
    clusterPane.style.opacity = 0.9

    // our basemap and add it to the map
    const baseMaps = {
      'HERE reduced.day': hereReducedDay
    }

    const overlayMaps = {
      'Points of interest': placesLayer,
      Clusters: clusterLayer
    }

    L.control.layers(baseMaps, overlayMaps).addTo(this.map)

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
      const div = L.DomUtil.create('div', 'brand')
      div.innerHTML =
        '<a href="https://gis.ops.com" target="_blank"><div class="gis-ops-logo"></a>'
      return div
    }
    const hereLogo = L.control({
      position: 'bottomright'
    })
    hereLogo.onAdd = function(map) {
      const div = L.DomUtil.create('div', 'brand')
      div.innerHTML =
        '<a href="https://developer.here.com/" target="_blank"><div class="here-logo"></div></a>'
      return div
    }
    this.map.addControl(hereLogo)
    this.map.addControl(brand)

    this.map.on('moveend', () => {
      dispatch(doUpdateBoundingBox(this.map.getBounds()))
    })

    // this.map.on('mousemove', e => {
    //   if (placesLayer.getLayers().length > 0) {
    //     // thanks to https://codepen.io/lknarf/pen/JXybxX
    //     const closestPoints = this.getClosestPoints(e)
    //     this.styleMarkers(closestPoints)
    //   }
    // })
    const bbox = this.map.getBounds()
    dispatch(doUpdateBoundingBox(bbox))
  }

  // styleMarkers = closestPoints => {
  //   const poiIds = closestPoints.map(pointFeature => {
  //     return pointFeature.id
  //   })
  //   _.each(placesLayer._layers, (layer, index) => {
  //     if (poiIds.includes(layer.options.id)) {
  //       layer.setStyle({ color: '#65958C', radius: 20 })
  //     } else {
  //       layer.setStyle({ color: layer.options.orig_color, radius: 5 })
  //     }
  //   })
  // }

  // getClosestPoints = e => {
  //   let allJson = _.clone(placesLayer.toGeoJSON())
  //   allJson.features = allJson.features.map((feature, index) => ({
  //     ...feature,
  //     id: index
  //   }))
  //   const currentPoint = {
  //     type: 'Feature',
  //     geometry: {
  //       type: 'Point',
  //       coordinates: [e.latlng.lng, e.latlng.lat]
  //     }
  //   }
  //   const closest = []
  //   for (let i = 1; i < 10; i++) {
  //     const near = nearest(currentPoint, allJson)
  //     closest.push(near)
  //     _.remove(allJson.features, feature => {
  //       return feature.id === near.id
  //     })

  //     allJson = {
  //       type: 'FeatureCollection',
  //       features: _.without(allJson.features, near)
  //     }
  //   }
  //   return closest
  // }

  processClusters(data) {
    const clusters = {}

    for (const feature of data.features) {
      if (
        feature.properties.dbscan == 'noise' ||
        feature.properties.dbscan == 'edge'
      ) {
        if (clusters.hasOwnProperty(feature.properties.dbscan)) {
          clusters[feature.properties.dbscan].push(
            point(feature.geometry.coordinates)
          )
        } else {
          clusters[feature.properties.dbscan] = []
        }
      } else if (feature.properties.dbscan == 'core') {
        if (clusters.hasOwnProperty(feature.properties.cluster)) {
          clusters[feature.properties.cluster].push(
            point(feature.geometry.coordinates)
          )
        } else {
          clusters[feature.properties.cluster] = []
        }
      }
    }

    const scaleHsl = chroma
      .scale(['#919098', '#FFCFD2', '#A3C4BC', '#DCEED1', '#A8D4AD'])
      .mode('hsl')
      .colors(Object.keys(clusters).length)

    let cnt = 0
    for (const clusterObj in clusters) {
      if (clusterObj !== 'noise' && clusterObj !== 'edge') {
        const hull = concave(
          featureCollection(clusters[clusterObj]) /*options*/
        )

        L.geoJSON(hull, {
          style: {
            fillColor: scaleHsl[cnt],
            weight: 2,
            opacity: 1,
            color: scaleHsl[cnt],
            pane: 'clusterPane'
          }
        })
          .addTo(clusterLayer)
          .bindTooltip(
            '<strong>Cluster number:</strong> ' +
              (parseInt(clusterObj) + 1) +
              '<br/> ' +
              '<strong>Amount of points in cluster:</strong> ' +
              clusters[clusterObj].length,
            {
              permanent: false,
              sticky: true
            }
          )
          .openTooltip()
        clusterLayer.bringToBack()
      }
    }
    cnt += 1
  }

  componentDidUpdate(prevProps) {
    const { lastCall, lastCompute, dbscanSettings } = this.props
    if (lastCall > prevProps.lastCall) {
      this.addPlaces()
    }

    if (lastCompute > prevProps.lastCompute) {
      const inputPoints = placesLayer.toGeoJSON()
      const maxDistance = dbscanSettings.maxDistance / 1000
      const minPoints = dbscanSettings.minPoints
      // console.log(points)
      const clustered = clustersDbscan(inputPoints, maxDistance, {
        minPoints: minPoints
      })
      this.processClusters(clustered)
    }
  }

  addPlaces() {
    placesLayer.clearLayers()

    const { places } = this.props

    let cnt = 0
    for (const place in places) {
      if (
        places[place].hasOwnProperty('data') &&
        places[place].data.length > 0
      ) {
        for (const placeObj of places[place].data) {
          L.circleMarker([placeObj.position[0], placeObj.position[1]], {
            color: places[place].color,
            orig_color: places[place].color,
            radius: 5,
            id: cnt,
            weight: 1
          })
            .addTo(placesLayer)
            .bindTooltip(placeObj.title)
          cnt += 1
        }
      }
    }
  }

  render() {
    return <div id="map" style={style} />
  }
}

const mapStateToProps = state => {
  const { places, lastCall, lastCompute, dbscanSettings } = state.placesControls
  return {
    places,
    lastCall,
    lastCompute,
    dbscanSettings
  }
}

export default connect(mapStateToProps)(Map)
