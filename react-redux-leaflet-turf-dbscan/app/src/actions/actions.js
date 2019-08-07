const hereAppCode = '0XXQyxbiCjVU7jN2URXuhg'
const hereAppId = 'yATlKFDZwdLtjHzyTeCK'

export const RECEIVE_PLACES_RESULTS = 'RECEIVE_PLACES_RESULTS'
export const REQUEST_PLACES_RESULTS = 'REQUEST_PLACES_RESULTS'
export const UPDATE_BBOX = 'UPDATE_BBOX'
export const UPDATE_DBSCAN_SETTINGS = 'UPDATE_DBSCAN_SETTINGS'
export const COMPUTE_DBSCAN = 'COMPUTE_DBSCAN'

export const fetchHerePlaces = payload => (dispatch, getState) => {
  dispatch(requestPlacesResults({ category: payload.category }))

  const { boundingbox } = getState().placesControls

  const url = new URL(
    'https://places.demo.api.here.com/places/v1/discover/explore'
  )
  const params = {
    app_id: hereAppId,
    app_code: hereAppCode,
    //west longitude, south latitude, east longitude, north latitude.
    in: boundingbox,
    size: 500,
    cat: payload.category
  }

  url.search = new URLSearchParams(params)

  return fetch(url)
    .then(response => response.json())
    .then(data =>
      dispatch(
        processPlacesResponse(
          data,
          payload.category,
          boundingbox,
          payload.color
        )
      )
    )
    .catch(error => console.error(error)) //eslint-disable-line
}

export const doUpdateBoundingBox = boundingbox => dispatch => {
  const bbox = [
    boundingbox._southWest.lng,
    boundingbox._southWest.lat,
    boundingbox._northEast.lng,
    boundingbox._northEast.lat
  ].join(',')

  dispatch(updateBoundingBox(bbox))
}

const updateBoundingBox = bbox => ({
  type: UPDATE_BBOX,
  payload: bbox
})

export const computeDbScan = () => ({
  type: COMPUTE_DBSCAN
})

export const updateDbScanSettings = settings => ({
  type: UPDATE_DBSCAN_SETTINGS,
  payload: { ...settings }
})

const parsePlacesResponse = json => {
  if (json.results && json.results.items.length > 0) {
    return json.results.items
  }
  return []
}

const processPlacesResponse = (json, category, bbox, color) => dispatch => {
  const results = parsePlacesResponse(json)
  dispatch(
    receivePlacesResults({
      data: results,
      category: category,
      boundingbox: bbox,
      color: color
    })
  )
}

export const receivePlacesResults = places => ({
  type: RECEIVE_PLACES_RESULTS,
  payload: places
})

export const requestPlacesResults = category => ({
  type: REQUEST_PLACES_RESULTS,
  payload: category
})
