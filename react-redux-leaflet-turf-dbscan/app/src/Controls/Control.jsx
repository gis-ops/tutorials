import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import _ from 'lodash'

import { Slider } from 'react-semantic-ui-range'

import {
  Segment,
  Divider,
  Button,
  Header,
  Loader,
  Label,
  Popup
} from 'semantic-ui-react'

import {
  fetchHerePlaces,
  updateDbScanSettings,
  computeDbScan
} from '../actions/actions'

const segmentStyle = {
  zIndex: 999,
  position: 'absolute',
  width: '400px',
  top: '10px',
  left: '10px',
  //height: '100vh',
  maxHeight: 'calc(100vh - 3vw)',
  overflow: 'auto',
  padding: '20px'
}

const herePlaces = {
  0: { name: 'shopping', color: 'red' },
  1: { name: 'accommodation', color: 'orange' },
  2: { name: 'administrative-areas-buildings', color: 'yellow' },
  3: { name: 'airport', color: 'olive' },
  4: { name: 'atm-bank-exchange', color: 'green' },
  5: { name: 'coffee-tea', color: 'teal' },
  6: { name: 'eat-drink', color: 'blue' },
  7: { name: 'going-out', color: 'violet' },
  8: { name: 'hospital-health-care-facility', color: 'purple' },
  9: { name: 'leisure-outdoor', color: 'pink' },
  10: { name: 'natural-geographical', color: 'brown' },
  11: { name: 'petrol-station' },
  12: { name: 'restaurant', color: 'grey' },
  13: { name: 'snacks-fast-food', color: 'black' },
  14: { name: 'sights-museums', color: 'red' },
  16: { name: 'toilet-rest-area', color: 'yellow' },
  17: { name: 'transport', color: 'olive' }
}

class Control extends React.Component {
  static propTypes = {
    places: PropTypes.object,
    dbscanSettings: PropTypes.object,
    isCalculatingDbScan: PropTypes.bool,
    boundingbox: PropTypes.string,
    dispatch: PropTypes.func.isRequired
  }

  constructor(props) {
    super(props)
  }

  handleClick = (event, data) => {
    const { dispatch } = this.props
    this.setState({ value: data.name })
    dispatch(fetchHerePlaces({ category: data.name, color: data.color }))
  }

  handleClickDbscan = (event, data) => {
    const { dispatch } = this.props
    dispatch(computeDbScan())
  }

  render() {
    const {
      places,
      isCalculatingDbScan,
      boundingbox,
      dbscanSettings,
      dispatch
    } = this.props

    return (
      <div>
        <Segment style={segmentStyle}>
          <div>
            <span>
              <Header as="h4">DBScan with HERE Maps places and TurfJS</Header>
              <p>
                Density-based spatial clustering of applications with noise (
                <a
                  href="https://en.wikipedia.org/wiki/DBSCAN"
                  rel="noopener noreferrer"
                  target="_blank">
                  DBScan
                </a>
                ) is a data clustering algorithm. Given a set of points in some
                space, it groups together points that are closely packed
                together (points with many nearby neighbors), marking as
                outliers points that lie alone in low-density regions (whose
                nearest neighbors are too far away).
              </p>
              <p>
                This application consumes{' '}
                <a
                  href="https://developer.here.com/api-explorer/rest/places"
                  target="_blank"
                  rel="noopener noreferrer">
                  HERE Maps places API
                </a>{' '}
                for given categories as point input for the clustering algorithm
                which is implemented in
                <a
                  href="https://turfjs.org/docs/#clustersDbscan"
                  target="_blank"
                  rel="noopener noreferrer">
                  TurfJS
                </a>
                .
              </p>
            </span>
          </div>
          <Header as="h5">DBScan settings</Header>
          <div className="flex flex-row">
            <div className="w-50">
              <Slider
                discrete
                color="grey"
                value={dbscanSettings.maxDistance}
                settings={{
                  start: dbscanSettings.maxDistance,
                  min: 100,
                  max: 50000,
                  step: 50,
                  onChange: value => {
                    dispatch(
                      updateDbScanSettings({
                        setting: 'maxDistance',
                        value: value
                      })
                    )
                  }
                }}
              />
              <div className="mt2">
                <Popup
                  content="Maximum Distance ε between any point of the cluster to generate the clusters"
                  trigger={
                    <Label size="tiny">
                      {'Max. distance in meters: ' + dbscanSettings.maxDistance}
                    </Label>
                  }
                />
              </div>
            </div>
            <div className="w-50">
              <Slider
                discrete
                color="grey"
                value={dbscanSettings}
                settings={{
                  value: dbscanSettings.minPoints,
                  min: 3,
                  max: 20,
                  step: 1,
                  onChange: value => {
                    dispatch(
                      updateDbScanSettings({
                        setting: 'minPoints',
                        value: value
                      })
                    )
                  }
                }}
              />
              <div className="mt2">
                <Popup
                  content="Minimum number of points to generate a single cluster, points which do not meet this requirement will be classified as an 'edge' or 'noise'."
                  trigger={
                    <Label size="tiny">
                      {'Min. points: ' + dbscanSettings.minPoints}
                    </Label>
                  }
                />
              </div>
            </div>
            <div className="w-20">
              <Button
                circular
                icon="whmcs"
                disabled={_.isEmpty(places)}
                onClick={this.handleClickDbscan}
              />
            </div>
          </div>

          <Divider />
          <div>
            <Loader
              active={isCalculatingDbScan}
              style={{ right: 0, left: 'unset' }}
            />

            {Object.keys(herePlaces).map((key, index) => {
              let isDisabled = false
              if (places[herePlaces[key].name]) {
                if (boundingbox == places[herePlaces[key].name].boundingbox) {
                  isDisabled = true
                }
              }
              return (
                <div key={index} className="mt1 dib">
                  <Button
                    size="tiny"
                    disabled={isDisabled}
                    loading={
                      places[herePlaces[key].name]
                        ? places[herePlaces[key].name].isFetching
                        : ''
                    }
                    onClick={this.handleClick}
                    name={herePlaces[key].name}
                    color={herePlaces[key].color}>
                    {herePlaces[key].name}
                  </Button>
                </div>
              )
            })}
          </div>
        </Segment>
      </div>
    )
  }
}

const mapStateToProps = state => {
  const {
    places,
    isCalculatingDbScan,
    boundingbox,
    dbscanSettings
  } = state.placesControls

  return {
    places,
    boundingbox,
    isCalculatingDbScan,
    dbscanSettings
  }
}

export default connect(mapStateToProps)(Control)
