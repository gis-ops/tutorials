import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { Slider } from "react-semantic-ui-range";
import { Label, Button, Divider } from "semantic-ui-react";

// we need just one action in this component to update settings made
import { updateSettings } from "../actions/actions";

class Settings extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    controls: PropTypes.object.isRequired
  };

  // dispatches the action
  updateSettings() {
    const { controls, dispatch } = this.props;

    dispatch(
      updateSettings({
        settings: controls.settings
      })
    );
  }

  // we are making settings directly in the controls.settings object which is being passed on to the updateSettings() function up top
  handleSettings(settingName, setting) {
    const { controls } = this.props;

    controls.settings[settingName] = setting;

    this.updateSettings();
  }

  // this looks complex but it isn't, we basically want to make sure the the interval settings maximum can never be greater than the range maximum
  alignRangeInterval() {
    const { controls } = this.props;

    if (
      controls.settings.range.value < controls.settings.interval.value ||
      controls.settings.interval.value == ""
    ) {
      controls.settings.interval.value = controls.settings.range.value;
    }

    controls.settings.interval.max = controls.settings.range.value;
  }

  render() {
    const { controls } = this.props;

    // depending on what the user selected we obviously want to show the correct units
    const rangetype =
      controls.settings.rangetype === "time" ? " minutes" : " kilometers";

    // our settings which are needed for the range slider, read more here https://github.com/iozbeyli/react-semantic-ui-range
    const rangeSettings = {
      settings: {
        ...controls.settings.range,
        min: 1,
        step: 1,
        start: controls.settings.range.value,
        // when the slider is moved, we want to update our settings and make sure the maximums align
        onChange: value => {
          controls.settings.range.value = value;

          this.alignRangeInterval();
          this.updateSettings();
        }
      }
    };
    // same as above, just for the interval slider this time
    const intervalSettings = {
      settings: {
        ...controls.settings.interval,
        min: 1,
        step: 1,
        start: controls.settings.interval.value,
        onChange: value => {
          controls.settings.interval.value = value;
          this.updateSettings();
        }
      }
    };
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
    );
  }
}

const mapStateToProps = state => {
  const controls = state.isochronesControls;
  return {
    controls
  };
};

export default connect(mapStateToProps)(Settings);
