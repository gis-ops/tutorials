import Stroke from "ol/style/Stroke"
import Style from "ol/style/Style"
import Circle from "ol/style/Circle"

export const pointStyle = new Style({
  image: new Circle({
    radius: 2,
    stroke: new Stroke({
      color: "#1442a3",
      width: 2,
    }),
  }),
})
