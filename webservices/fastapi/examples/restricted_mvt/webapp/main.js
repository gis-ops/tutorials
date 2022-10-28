import Map from "ol/Map"
import OSM from "ol/source/OSM"
import TileLayer from "ol/layer/Tile"
import MVT from "ol/format/MVT"
import View from "ol/View"
import Control from "ol/control/Control"
import VectorTile from "ol/source/VectorTile"
import { pointStyle } from "./style"
import VectorTileLayer from "ol/layer/VectorTile"
import { Feature } from "ol"
import { fromLonLat } from "ol/proj"

const map = new Map({
  layers: [
    new TileLayer({
      source: new OSM(),
    }),
  ],
  target: "map",
  view: new View({
    center: fromLonLat([13.38, 52.5]),
    zoom: 12,
  }),
})

const getTileLoader = (token) => {
  return function authTileLoad(tile, url) {
    tile.setLoader(function (extent, resolution, projection) {
      fetch(url, {
        method: "GET",
        headers: { // we're adding auth header here
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }).then(function (response) {
        response.arrayBuffer().then(function (data) {
          const format = tile.getFormat() // ol/format/MVT configured as source format
          const features = format.readFeatures(data, {
            extent: extent,
            featureProjection: projection,
          })
          tile.setFeatures(features)
        })
      })
    })
  }
}

/**
 * We subclass ol/Control to create
 * a new UI component on top of our map
 */
class Login extends Control {
  constructor(opt_options) {
    const options = opt_options || {}

    const form = document.createElement("form")
    const userdiv = document.createElement("div")
    const user = document.createElement("input")
    userdiv.appendChild(user)
    user.type = "text"
    user.name = "username"
    user.placeholder = "username"
    user.autocomplete = "off"
    const password = document.createElement("input")
    const passworddiv = document.createElement("div")
    passworddiv.appendChild(password)
    password.type = "password"
    password.placeholder = "password"
    password.name = "password"
    const button = document.createElement("button")
    button.type = "submit"
    button.innerHTML = "Log in"
    form.appendChild(userdiv)
    form.appendChild(passworddiv)
    form.appendChild(button)

    const element = document.createElement("div")
    element.className = "form"
    element.appendChild(form)

    super({
      element: element,
      target: options.target,
    })

    element.addEventListener("submit", this.handleSubmit)
  }

  handleSubmit(e) {
    e.preventDefault()
    const data = new FormData(e.target)
    const username = data.get("username")
    const password = data.get("password")

    this.user = username
    fetch("http://localhost:8001/login", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      mode: "cors",
      body: JSON.stringify({
        username,
        password,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.token) {
          // if the server replies with a token, we can use it to get the vector tiles
          const tileSource = new VectorTile({
            format: new MVT({ featureClass: Feature }),
            url: "http://localhost:8001/adresses/{z}/{x}/{y}",
            tileLoadFunction: getTileLoader(data.token),
          })

          const tileLayer = new VectorTileLayer({
            source: tileSource,
            style: pointStyle,
            renderMode: "vector",
            properties: {
              name: "authedTile",
            },
          })

          map.addLayer(tileLayer)

          // we show the user that they're logged in
          const p = document.createElement("p")
          p.classList = "welcome"
          p.textContent = `Welcome ${this.user}!`

          // ...and create a logout button
          const element = document.querySelector(".form")
          const form = document.querySelector("form")
          const logoutBtn = document.createElement("button")
          logoutBtn.addEventListener(
            "click",
            (e) => {
              // once the user is logged out, we
              // restore the original login form
              logoutBtn.style.display = "none"
              p.style.display = "none"
              form.style.display = ""

              // we delete our MVT layer
              map.getLayers().forEach((layer) => {
                if (layer.get("name") === "authedTile") {
                  map.removeLayer(layer)
                }
              })
            },
            { once: true }
          )
          logoutBtn.innerHTML = "Log out"
          logoutBtn.className = "logout"
          form.style.display = "none"
          element.appendChild(p)
          element.appendChild(logoutBtn)
        }
      })
  }
}

map.addControl(new Login({ target: "login" }))
