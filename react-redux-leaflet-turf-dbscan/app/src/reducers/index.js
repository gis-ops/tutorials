import { combineReducers } from 'redux'
import {
  REQUEST_PLACES_RESULTS,
  RECEIVE_PLACES_RESULTS,
  UPDATE_BBOX,
  UPDATE_DBSCAN_SETTINGS,
  COMPUTE_DBSCAN
} from '../actions/actions'

const initialPlacesState = {
  boundingbox: '',
  lastCall: Date.now(),
  places: {},
  dbscanSettings: {
    minPoints: 10,
    maxDistance: 500
  },
  lastCompute: ''
}

const placesControls = (state = initialPlacesState, action) => {
  switch (action.type) {
    case COMPUTE_DBSCAN:
      return {
        ...state,
        lastCompute: Date.now()
      }

    case UPDATE_DBSCAN_SETTINGS:
      return {
        ...state,
        dbscanSettings: {
          ...state.dbscanSettings,
          [action.payload.setting]: action.payload.value
        }
      }

    case UPDATE_BBOX:
      return {
        ...state,
        boundingbox: action.payload
      }
    case REQUEST_PLACES_RESULTS:
      return {
        ...state,
        places: {
          ...state.places,
          [action.payload.category]: {
            ...state.places[action.payload.category],
            isFetching: true
          }
        }
      }

    case RECEIVE_PLACES_RESULTS:
      return {
        ...state,
        lastCall: Date.now(),
        places: {
          ...state.places,
          [action.payload.category]: {
            ...state.places[action.payload.category],
            data: state.places[action.payload.category].hasOwnProperty('data')
              ? [
                  ...state.places[action.payload.category].data,
                  ...action.payload.data
                ]
              : action.payload.data,
            boundingbox: action.payload.boundingbox,
            color: action.payload.color,
            isFetching: false
          }
        }
      }

    default:
      return state
  }
}

const rootReducer = combineReducers({
  placesControls
})

export default rootReducer
