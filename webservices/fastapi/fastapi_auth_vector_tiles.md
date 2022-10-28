# Restricted Vector Tile access with FastAPI & PostGIS

So you have a huge table of geodata that you want to share via the web. [MapBox Vector Tiles](https://docs.mapbox.com/data/tilesets/guides/vector-tiles-introduction/) offer a modern and fast way to accomplish that goal: the data gets encoded to small-sized protocol buffers, and then get decoded on the client. This is way faster than simply serving huge GeoJSON objects over the web that need to be deserialized by the client (which is [even slower than you might think](https://www.youtube.com/watch?v=dE2ObbhEXKQ)). But it's lacking that dynamic aspect of GeoJSON, where you can generate responses on the fly, based on the user's request. **Or is it?**

Well, as it turns out, good old XYZ tiles have established the idea of tiles being the exact opposite of dynamic: they need to be built by some software package before serving, and that tile image generation takes time. But vector tiles are not like that at all: in fact, there is even [a handy web server](https://github.com/developmentseed/timvt) that generates vector tiles from your PostGIS data _on the fly_. 

In this tutorial, we're taking that idea of on-the-fly vector tile serving a little further. The use case: build an application where users have access to geodata on a _need-to-know basis_, for example if your clients need to see only a small subset of your geodata. 

In this tutorial, you will learn

- how to create MapBox Vector Tiles from PostGIS,
- how to serve these Vector Tiles over the web in a standardized manner,
- and, most importantly: how to restrict access to the data being served

## Prerequisites

- Python >= 3.10
- PostGIS >= 3.0 (we recommend [Kartoza's](https://gis-ops.com/postgrest-tutorial-installation-and-setup/) docker image, see our tutorial [here](https://gis-ops.com/postgrest-tutorial-installation-and-setup/))
- gdal >= 3.5
- npm (optional, if you want to follow the web map part as well) 
    
 > Disclaimer: This tutorial was developed on Manjaro Linux 22.0.0.

Good to have is some experience with:

- [FastAPI](fastapi.tiangolo.com)/HTTP API
- SQL ORM libraries (`SQLAlchemy` or similar)
- (Postgre)SQL/PostGIS
    
If you want to follow along building the web app to display the vector tiles in the browser, JavaScript knowledge is highly recommended as well.

## Step 1: Get some data

For our example, we'll be serving address data from the city of Berlin. Head [here](https://opendata-esri-de.opendata.arcgis.com/maps/273bf4ae7f6a460fbf3000d73f7b2f76) to download the geojson file. We'll then pass it to PostGIS using gdal's `ogr2ogr`: 

```sh
ogr2ogr -f "PostgreSQL" PG:"dbname='gis' user='tutorial' password='tutorial' port='5432' host='localhost'" "Adressen_-_Berlin.geojson" -nln addresses
```

Next, we will create a table called `users`, where we store information about the users that are allowed to access parts of our address data. For this example, we'll keep it simple: each user has access to address data within one postal code zone.

```sql
CREATE TABLE users(id SERIAL PRIMARY KEY , username varchar, plz varchar, password text);
INSERT INTO users(username, plz, password)
SELECT concat('user_', plz) as username, plz, crypt('123', gen_salt('bf', 8)) as password FROM (SELECT DISTINCT plz FROM adresses)s;
```

This is not a tutorial on web security, but we do want to make use of some good security practices here, so we use Postgres' `pgcrypto` extension to hash our users' passwords using the SHA256 algorithm and even use a [salt](https://auth0.com/blog/adding-salt-to-hashing-a-better-way-to-store-passwords/). To use this function, you might need to run

```sql
CREATE EXTENSION pgcrypto;
```

## Step 2: Spin up FastAPI

Now that we have our database set up, let's create a small REST API to let users interact with it. We need to install some packages for this first, so let's go ahead and create a virtual environment in Python and pip install our dependencies:

```sh
python -m venv .venv

source .venv/bin/activate

pip install fastapi pyjwt sqlmodel psycopg2-binary buildpg asyncpg uvicorn morecantile
```

Before we create our main application, we need to create some user authentication logic. In this tutorial, we will be using JSON Web Tokens (read more about it [here](https://jwt.io/introduction)). We already installed `pyjwt` to create and validate these tokens, so we can simply create a small function that neatly wraps the decoding logic. Create `jwtoken.py` and in it, create the function `create_token`:

```python
from datetime import datetime, timedelta

import jwt


def create_token(user: str, refresh: bool = False) -> str:
    minutes = (
        30
        if not refresh
        else 60 * 24
    )
    expires_delta = datetime.utcnow() + timedelta(minutes=minutes)

    to_encode = {"exp": expires_delta, "sub": user}
    encoded_jwt = jwt.encode(to_encode, "SUPER_SECRET_KEY", algorithm="HS256")

    return encoded_jwt

```

Okay, we'll get to create our actual application soon, but first, let's define a user model for that endpoint. Go ahead and create `models.py`, and in it, create two classes: one for the login request body, and one for the database (thanks for that convenience `SQLModel`!).

```python

from typing import Optional
from sqlmodel import Field, SQLModel


class UsersReq(SQLModel):
    username: str
    password: str


class Users(UsersReq, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plz: Optional[str]


```

Finally, just specify how the app will access our database. Create `engine.py` and paste the following:

```python

from sqlmodel import create_engine

DATABASE_URL = "postgresql://<user>:<password>@localhost:5432/gis"

engine = create_engine(DATABASE_URL, echo=True)

```

Okay, on to our first endpoint: head back to `main.py` and create a `/login` route:

```python
import morecantile
from buildpg import asyncpg
from fastapi import FastAPI, Path, HTTPException, Depends
from morecantile import Tile
from sqlalchemy import func
from sqlmodel import Session, select
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from engine import DATABASE_URL, engine
from models import Users, UsersReq
from jwtoken import create_token

origins = [
    "http://localhost",
    "http://localhost:5173",
]

vectortile_app = FastAPI()

vectortile_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@vectortile_app.post("/login")
def login(data: UsersReq):
    with Session(engine) as session:
        result = session.exec(
            select(Users).where(
                Users.username == data.username,
                Users.password == func.public.crypt(data.password, Users.password),
            )
        ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong username or password.",
        )

    return {"token": create_token(result.username)}



```

The logic is simple: we expect a JSON object containing a user and a password property, and we see if it matches with an entry in our database. If it does, we'll send back a token that the user can use to access other endpoints. 

> **Note:** usually, a JWT auth scheme would consist of a refresh and an access token. We are just going to use the access token for the sake of simplicity

Now, before creating our tile serving endpoint, we need to have logic in place that authenticates our users and authorizes them to see certain parts of our data. Go on and create `auth.py`. In it, we will use a subclass of FastAPI's `HTTPBearer`, which will be used as a dependency injection in our protected endpoint (if you want to know more about this architectural pattern, take a look at the [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/dependencies/)). 

```python
from functools import lru_cache

import jwt
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlmodel import Session, select
from starlette.requests import Request

from engine import engine
from models import Users


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class Authorizer(HTTPBearer):
    def __init__(self, auto_error=True):
        super(Authorizer, self).__init__(auto_error=auto_error)
        self.user = None

    async def __call__(self, request: Request):
        creds: HTTPAuthorizationCredentials = await super(Authorizer, self).__call__(request)
        if not creds or not creds.scheme == "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

        if not (token := self.verify_jwt(creds.credentials)):
            raise HTTPException(status_code=403, detail="Invalid token or expired token.")

        self.user = token.sub
        return self

    @staticmethod
    def verify_jwt(jwtoken):
        try:
            payload = jwt.decode(
                jwtoken,
                "SUPER_SECRET_KEY",
                algorithms=["HS256"],
            )
            return TokenPayload(**payload)
        except Exception:
            return False

    def get_user_info(self):
        return get_user_info(self.user)


@lru_cache
def get_user_info(username):
    with Session(engine) as session:
        postal_code = session.exec(
            select(Users.plz).where(Users.username == username)
        ).first()

        return postal_code

```

At each request, we will verify the sent token. Then, we create a method that gets the assigned postal code of the authenticated user, since this will be used to select the subset of addresses that user will be allowed to see. Note that we use Python's built in caching so that once a user has logged in, we do not need to constantly get that information from the database with every tile request.

Now, we finally get to the juicy part of this tutorial: the **tile serving**. Let's head back to our `main.py`, and create a new endpoint:

```python
# import our new Authorizer class at the top

from auth import Authorizer

# ..other imports


# get the tile parameters from the path
def tile_params(
    z: int = Path(..., ge=0, le=25,),
    x: int = Path(...),
    y: int = Path(...),
) -> Tile:
    """Tile parameters."""
    return Tile(x, y, z)

# add an asychronous db session pool for tile serving
@vectortile_app.on_event("startup")
async def startup_event():
    vectortile_app.state.pool = await asyncpg.create_pool_b(
        DATABASE_URL,
    )


# ...

@vectortile_app.get("/adresses/{z}/{x}/{y}/")
async def get_tile(
        request: Request,
        auth_info: Authorizer = Depends(Authorizer()),
        tile: Tile = Depends(tile_params),  # FastAPI magic: receives x/y/z
):
    tms = morecantile.tms.get("WebMercatorQuad")
    bbox = tms.xy_bounds(tile)
    p = {
        "xmin": bbox.left,
        "ymin": bbox.bottom,
        "xmax": bbox.right,
        "ymax": bbox.top,
        "epsg": tms.crs.to_epsg(),
    }

    plz = auth_info.get_user_info()  # here, we're fetching what the user is allowed to see

    q = """
    SELECT ST_AsMVT(mvtgeom.*) FROM (
        SELECT ST_asmvtgeom(ST_Transform(t.geom, 3857), bounds.geom) AS geom, t.objectid
            FROM ( SELECT objectid, wkb_geometry as geom FROM public.adresses WHERE plz = '{plz}') t,
                 (SELECT ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, :epsg) as geom) bounds
            WHERE ST_Intersects(t.geom, ST_Transform(bounds.geom, 4326))
         ) mvtgeom;  
    """.format(plz=plz)

    pool = request.app.state.pool
    async with pool.acquire() as conn:
        content = await conn.fetchval_b(q, **p)

    return Response(bytes(content), media_type="application/x-protobuf")

```

Note that we use a different engine to access PostGIS asynchronously for faster tile serving (we stick with the synchronous way to get the user details for easier caching).

Let's disect a bit what's happening in the endpoint function: we use `morecantile` to calculate the requested tile's bounding box, and then pass it to our SQL query. You might wonder how short this query is, given it does so much: it gets the address points from our user's assigned postal code, that lie within the tile's bounds and packages it as a protobuf binary (MVT). Thanks to the power of PostGIS, we can simply call two functions that do all the heavy lifting of vector tile conversion: `ST_AsMVTGeom` to convert the geometries, and `ST_AsMVT` to convert a record (i.e. the geometry including all the wanted properties).

Finally, let's test our application. Run the API with `uvicorn main:vectortile_app --reload --port 8001
`. We can use `cURL` to try out the log in logic:

```sh
curl --request POST \
  --url http://localhost:8001/login \
  --header 'Content-Type: application/json' \
  --data '{
	"username": "user_10365",
	"password": "123"
}'
```

In the response, you should get a token that starts with "ey" and consists of numbers and letters. If this works, we can proceed to the second part of this tutorial: _serving our vector tiles in the browser_.

## Step 3 - Restricted Vector Tiles in a web application

For this, we will be using OpenLayers, which has some pretty advanced Vector Tile serving capabilities. Create a new foler called `webapp` and in it, create the following `package.json`:

```json
{
  "name": "webapp",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "start": "vite",
    "build": "vite build"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "ol": "7.1.0"
  },
  "devDependencies": {
    "vite": "^3.0.3",
    "@babel/core": "latest"
  }
}

```

Then, run `npm install`, and proceed to create the following `index.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="stylesheet" href="node_modules/ol/ol.css" />
    <title>GIS-OPS: Authed Vector Tiles</title>
    <style>
      body,
      html {
        margin: 0;
        font-family: Helvetica, Arial, Sans-Serif;
      }
      .map {
        width: 100vw;
        height: 100vh;
      }

      #login {
        position: absolute;
        display: block;
        top: 25px;
        right: 25px;
        z-index: 9999;
      }

      .form {
        background-color: rgba(220, 220, 220, 0.723);
        padding: 10px;
      }
      button {
        margin: 0 auto;
        display: block;
      }
      input {
        margin-bottom: 5px;
      }
    </style>
  </head>
  <body>
    <div id="map" class="map"></div>
    <div id="login"></div>
    <script type="module" src="main.js"></script>
  </body>
</html>

```

Finally, we create `main.js`, where our core mapping application will live:


```javascript
// we'll need these in a bit
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

```

We import everything we will need later on, create a simple map with an OSM slippy map. Now to the crucial part: OpenLayers by default does not support authorization headers in vector tile requests, **but** it does let us pass our own tile loading function. So let's go ahead and do that:

```javascript
// imports and map initiation...

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

```
This is simply the example function provided from the OpenLayers documentation, but we added a wrapper function that we can pass our token into, plus modified headers that will hold the token.

Next, we need a style for our vector tiles. Go ahead and create `style.js` and create a neat style for our point layer. Feel free to unleash your inner cartographer, but we're gonna keep it simple for now:

```javascript
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

```

Finally, we want some login UI and logic. For this we will simply create a new custom `ol/Control` subclass that holds a simple login form. If the user has successfully logged in, we create a new `VectorTileSource` (with our custom function in the options) and add a `VectorTileLayer` to the  map:


```javascript
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

```

Finally, we also mimick some logout logic, where we delete the vector tile layer and source. Now, you should be able to start the app with `npm run start`. Go to `http://localhost:5173` (note that `127.0.01` will not work due to our backend's CORS settings) and see it in action:

![GIF Showing the resulting mapping application](https://github.com/gis-ops/tutorials/blob/master/webservices/fastapi/mvt.gif?raw=true)

From the browser, you're requesting the same endpoint, but with a different authorization header each time, and each time you log on as a different user, the same vector tile source recceives a distinct subset of features from the server. _"But what about loading times?"_ you might be asking yourself. Sure, checking the user token at each request comes at a cost, but a negligible one: using my browser's dev tools, I can see that the first request (where our FastAPI app actually needs to get the postal code from the database) clocks in at a bit more than 400ms, but that time drops once that result is cached, with response times easily dropping below 100ms! Now, that server is running on my local machine, but it's a good indication that this logic is performant enough to be used in a production environment, especially taking into consideration the alternative: sending huge chunks of GeoJSON. 

## Wrap-up

In this tutorial, we showed you how to implement restricted access to geodata served as vector tiles using FastAPI and PostGIS. In case you had trouble following along, you can check out the full example applications (both frontend and backend) [here](https://github.com/gis-ops/tutorials/tree/master/webservices/fastapi/examples/restricted_mvt).

Please feel free to get in touch with us at enquiry[at]gis-ops.com if you have any further questions, need support or have ideas on how to make this tutorial better!

