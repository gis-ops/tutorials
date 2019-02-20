import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";

// we are importing some of the beautiful semantic UI react components
import { Segment, Search, Divider, Button } from "semantic-ui-react";

// here are our first two actions, we will be adding them in the next step, bare with me!
import {
  updateTextInput,
  fetchHereGeocode,
  updateCenter,
  fetchHereIsochrones
} from "../actions/actions";

import Settings from "./Settings";

// to wait for the users input we will add debounce, this is especially useful for "postponing" the geocode requests
import { debounce } from "throttle-debounce";

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
    isochronesCenter: PropTypes.object,
    isFetchingIsochrones: PropTypes.bool.isRequired
  };

  constructor(props) {
    super(props);
    // binding this to the handleSearchChange method
    this.handleSearchChange = this.handleSearchChange.bind(this);
    // we are wrapping fetchGeocodeResults in a 1 second debounce
    this.fetchGeocodeResults = debounce(1000, this.fetchGeocodeResults);
  }

  // if the input has changed... fetch some results!
  handleSearchChange = event => {
    const { dispatch } = this.props;

    dispatch(
      updateTextInput({
        inputValue: event.target.value
      })
    );
    this.fetchGeocodeResults();
  };

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
    const { dispatch, userTextInput } = this.props;
    // If the text input has more then 0 characters..
    if (userTextInput.length > 0) {
      dispatch(
        fetchHereGeocode({
          inputValue: userTextInput
        })
      );
    }
  }

  handleFetchIsochrones = () => {
    const { dispatch, settings } = this.props;

    if (settings.isochronesCenter.lat && settings.isochronesCenter.lng) {
      dispatch(fetchHereIsochrones({ settings }));
    }
  };

  render() {
    // The following constants are used in our search input which is also a semanticUI react component <Search... />
    const {
      isFetching,
      userTextInput,
      results,
      settings,
      isFetchingIsochrones
    } = this.props;

    // if an address is selected we will return true to enable our button!
    const isResultSelected = () => {
      if (settings.isochronesCenter.lat && settings.isochronesCenter.lng)
        return false;
      return true;
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
            <Button
              circular
              loading={isFetchingIsochrones}
              disabled={isResultSelected()}
              color="purple"
              icon="globe"
              onClick={this.handleFetchIsochrones}
            />
          </div>
          <div className="mt2">
            <Settings />
          </div>
        </Segment>
      </div>
    );
  }
}

//
const mapStateToProps = state => {
  const userTextInput = state.isochronesControls.userInput;
  const results = state.isochronesControls.geocodeResults;
  const isFetching = state.isochronesControls.isFetching;

  // new
  const settings = state.isochronesControls.settings;
  // new
  const isFetchingIsochrones = state.isochronesControls.isFetchingIsochrones;

  return {
    userTextInput,
    results,
    isFetching,
    settings,
    isFetchingIsochrones
  };
};

export default connect(mapStateToProps)(Control);
