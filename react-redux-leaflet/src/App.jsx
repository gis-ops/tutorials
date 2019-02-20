import React from "react";
import Map from "./Map/Map";
import Controls from "./Controls/Control";

class App extends React.Component {
  render() {
    return (
      <div>
        <Map />
        <Controls />
      </div>
    );
  }
}

export default App;
