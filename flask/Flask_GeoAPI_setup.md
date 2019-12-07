# Flask GeoAPI — Flask with geospatial super powers

This tutorial will give you an introduction on how to setup Flask as a lightweight WSGI web application framework, enable it with spatial capabilities and expose those functionalities via a REST API delivered by a customized Flask-RESTPlus.

**Note**, this tutorial is addressing developers with a basic understanding on Python and what spatial data is.
Knowledge in Flask is not required as you're going to learn exactly that together.

The final example can be found in the GIS-OPS [tutorials repository](https://github.com/gis-ops/tutorials/tree/master/flask/examples/base_api).   
You can find an explanation on how to set it up quickly, at the end of the file.

![Flask GeoAPI](https://raw.githubusercontent.com/gis-ops/tutorials/flask_tutorial/flask/static/img/overview.png)

In this tutorial you'll explore how easy it is with Flask to:

- setup your own spatially enabled REST API with FLASK and FLASK-RESTPlus
- structure the API logically
- implement 3 API endpoints that will retrieve and process spatial data
- documentation of the API endpoints

> **Disclaimer**
>
> Validity only confirmed for **Ubuntu 18.04** and **Flask <= v1.1.1**. Map projections might need adjustments, depending on your targeted location(s).

## Prerequisites

- Python >= 3.6
- virtualenv >= v16.7.7
- pip >= 19.2.3
- basic understanding of Linux and Python

In case you don't have python or virtualenv installed, head over to this nice and short [tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-ubuntu-18-04-quickstart) and do the steps 1-5.

## Step 1 — The general setup

First, set up the project folder and create a new virtual environment. This way you ensure that you're starting with the same setup:

```sh
mkdir flask-tutorial && cd flask_tutorial
virtualenv -p python3 ./venv
source ./venv/bin/activate
which python
```

This should output the location of the project-specific `python3` executable. This will be the environment we're referring to throughout the tutorial.

To be able to set up Flask and your API, you need some basic dependencies for Python. For that you're going to use `pip` and it's automatic requirements loader, to automatically install everything you need. First create a file named `requirements.txt` in your tutorials folder:

 ```sh
touch requirements.txt
```

And paste the following library content into it:

```bash
aniso8601==8.0.0
attrs==19.3.0
Click==7.0
Flask==1.1.1
Flask-CLI==0.4.0
Flask-Cors==3.0.8
flask-marshmallow==0.10.1
flask-restplus==0.13.0
geographiclib==1.50
geopy==1.20.0
importlib-metadata==1.1.0
itsdangerous==1.1.0
Jinja2==2.10.3
jsonschema==3.2.0
MarkupSafe==1.1.1
marshmallow==3.2.2
more-itertools==8.0.0
packaging==19.2
pluggy==0.13.1
py==1.8.0
pyparsing==2.4.5
pyproj==2.4.2.post1
pyrsistent==0.15.6
pytest==5.3.1
pytz==2019.3
Shapely==1.6.4.post2
six==1.13.0
wcwidth==0.1.7
Werkzeug==0.16.0
zipp==0.6.0
```

Next run:

```bash
pip3 install -r requirements.txt
```

If everything runs through, you're now ready and equipped with all you'll need.

## Step 2 — Setup the Flask structure

Next you'll set up the base Flask structure. All you're going to learn from here on, can be applied in the exact same way for every Flask project, as our approach is highly extendable through its modular design. The Flask | Flask-RESTPlus needs to have the following working structure, to work as expected by the end of this tutorial:

```
.
├── app
│   ├── __init__.py
│   └── modules
│       ├── api
│       │   └── __init__.py
│       ├── geoapi
│       │   ├── __init__.py
│       │   └── resources.py
│       └── __init__.py
├── config.py
├── requirements.txt
└── run.py
```

-   `app` will be the folder in which the Flask app and all of its functions are created.
-   `app/__init__.py` holds the actual Flask app initialization.
-   `app/modules/__init__.py` will be the module loader that is going to dynamically load all its defined modules at server startup.
-   `app/modules/api/__init__.py` hosts the Blueprint for your API. In this case `apiv1`. Here you can version your API.
-   `app/modules/geoapi/` will hold your first actual API endpoint that can consume and process spatial data as a module.
-   `app/modules/geoapi/__init__.py` is the initializer for the `geoapi` module.
-   `app/modules/geoapi/resources.py` will be the place to create your API resources that will eventually hold your API request routes.
-   `config.py` will hold the configuration information that the app needs to perform correctly.
-   `run.py` is the actual server startup script that loads everything in `app`.

Don't worry if it looks overwhelming, this is just for your orientation. You can either create these empty files and directories now or you'll create them throughout the tutorial.

### Create the Flask App

All the Flask related code will live in a subfolder called `app` and started through its `app/__init__.py` file, which will look like this:

```python
# encoding: utf-8
"""
Example RESTful API Server.
"""
from flask import Flask
from flask_restplus import Api

api_v1 = Api(
    version='1.0',
    title="FLASK | FLASK-RESTPlus GeoAPI",
    description=(
        "This is a FLASK-RESPlus powered API with geospatial super power.\n\n"
        "Checkout more at https://gis-ops.com or https://github.com/gis-ops\n"
    ),
)

def create_app(flask_config_name=None, **kwargs):
    """
    Entry point to the Flask RESTful Server application.
    """

    # Initialize the Flask-App
    app: Flask = Flask(__name__, **kwargs)

    # Load the config file
    app.config.from_object('config.DevelopmentConfig')

    # Initialize FLASK-RESTPlus
    api_v1.init_app(app)

    # Initialize the modules
    from . import modules
    modules.init_app(app)

    return app
```

This is the entry point to the API you're going to create in the next few steps. If you study the code, you'll quickly understand what's going on from the comments.

- first the basic Flask App is initialized, and the local config is loaded into the app (you'll see the what the config looks like very soon)
- then Flask-RESTPlus and the API modules are initialized with the `app` object.

[Flask-RESTPlus](https://flask-restplus.readthedocs.io/en/stable/) is one of the core parts of this API. It is an extension for Flask, which adds support for easily building REST APIs and encourages best practices with minimal setup. It'll give your server the possibility to not only automatically generate the API documentation (with Swagger) but also to serialize and de-serialize data objects. A more comprehensie tutorial on API documentation with Swagger is coming up soon.

Next, you'll implement the `modules` package, which we're already referencing above.

### Module importer

The following code will iterate over all modules that are located inside `app/modules/` and are active in the `ENABLED_MODULES` attribute of the `config.py`. Start by creating the `app/modules` package and fill its `__init__` file with

```python
# encoding: utf-8

def init_app(app, **kwargs):
    from importlib import import_module

    for module_name in app.config['ENABLED_MODULES']:
        import_module('.%s' % module_name, package=__name__).init_app(app, **kwargs)
```

Next, you'll see what exactly the `ENABLED_MODULES` attribute is.

### Set the config file

In the project root (i.e. `app/`), create the `config.py` and create the following config classes:

```python
# encoding: utf-8

class BaseConfig(object):
    ENABLED_MODULES = {
        'api',
    }

    SWAGGER_UI_JSONEDITOR = True


class DevelopmentConfig(BaseConfig):
    """config for DevelopmentConfig."""
    DEBUG = False
    DEVELOPMENT = True
```

You have a `BaseConfig` that serves as the basic config, holding all the information shared by all specific configs. The actual one used will be the `DevelopmentConfig`. You can also add your custom config below by just adding a new Class which inherits from the `BaseConfig`, e.g. a `ProductionConfig`. The `ENABLED_MODULES` is the place where you can activate and deactivate the API endpoints. `api` is your base API and loads the API documentation for your versioned API at `http://127.0.0.1:4000/api/v1/`. You'll see very shortly how that fits together.

### Integrate your Flask-RESTPlus API

You already initialized FLASK-RESTPlus and now you're going to set it up correctly. As the goal is to implement an API that can be easily scaled, the App will make use of [Blueprints](https://flask-restplus.readthedocs.io/en/stable/scaling.html). Blueprints give the possibility to split the API into multiple and therefore nicely separated namespaces.

Add a blueprint by pasting the following into `app/modules/api/__init__.py`:

```python
# encoding: utf-8
"""
Flask-RESTplus API registration module
======================================
"""

from flask import Blueprint

from app import api_v1

class ApiPaths(object):
    APIPath = "/api/v1"

# API endpoint initializer
def init_app(app, **kwargs):
    api_v1_blueprint = Blueprint('api', __name__, url_prefix=ApiPaths.APIPath)
    api_v1.init_app(api_v1_blueprint)
    app.register_blueprint(api_v1_blueprint)
```

This defines the basic API with Flask-RESTPlus at the `/api` API route and will be the URL to use your API. As you might have noticed, this file contains an `init_app` function. This is the function which is called in `app/modules/__init__.py` for all modules active in `config.py`'s `ENABLED_MODULES`. The name of the modules in `ENABLED_MODULES` is in fact the name of the package you use to structure your endpoints, so in this case it comes from the `api` in `app/modules/`**`api`**`/__init__.py`.

### Create the run file

Now is the time you can actually start the API for the first time, even though without any content. In order to actually start the app you created in `app/__init__.py`, you need a runner routine named `run.py` in your project's root folder:

```sh
touch run.py
```

And add the following content into it:

```python
from app.__init__ import create_app


def run(host='127.0.0.1', port=4000):
    """
    Run RESTful API Server.
    """

    # Create the Flask app
    app = create_app()

    # Return the app to the runner state so it gets actually loaded.
    return app.run(host=host, port=port)

if __name__ == '__main__':
    run()
```

From reading the comments you might guess what's happening here. The code is creating the app and running it on `127.0.0.1:4000`.

###  Test the basic API

If you followed the instructions you should now be able to spin up the API. It won't show you much besides the bare Swagger UI frontend.

```bash
python run.py
```

Then call `http://127.0.0.1:4000/api/v1` to get to the actual Swagger UI. If this works for you, good, if not, please go back a few steps and check you followed all steps correctly.

## Step 3 — GeoAPI

Now, that your basic API is ready, you can fill it with life. So, you're going to implement functionality with 3 simple geospatial capable api routes with the following capabilities, respectively:

- calculate the length of a GeoJSON LineString that is POSTed to the API
- calculate the distance between two Points which will be passed in the query string
- calculate the area of a GeoJSON Polygon that gets POSTed to the API

The goal is to give you a broader example and insight on a few variances of how to get geospatial data into your server, parse it, process it and return the results back to the user.   

Mind for the following: no matter what new endpoint you will add on your own after this tutorial, the process will always be the same from here on. You'll be able to just add as many modules as you like and initialize it automatically through the module loader.

First create your first real API endpoint module:

```sh
mkdir app/modules/geoapi
touch app/modules/geoapi/__init__.py
touch app/modules/geoapi/resources.py
```

Add the following content to `app/modules/geoapi/__init__.py`:

```python
# encoding: utf-8

from app import api_v1


class GeoApiNamespace:
    namespace = "geoapi"
    description = "GeoAPI"


def init_app(app, **kwargs):
    """
    Init the GeoAPI module.
    """

    # Load the underlying module
    from . import resources

    api_v1.add_namespace(resources.api)
```

This will initialize your new GeoAPI and load the API routes from `geoapi/resources` into the namespace of the API.

In order to create the first routes, add the `geoapi` namespace to `app/modules/geoapi/resources.py` at the top of the file:

```python
# encoding: utf-8

"""
RESTful API GeoAPI resources
--------------------------
"""

import geopy.distance
import pyproj
from app.modules.geoapi import GeoApiNamespace
from flask import request
from flask_restplus import Namespace, Resource, abort
from flask_restplus import fields
from functools import partial
from geopy import Point as GeopyPoint, distance
from http import HTTPStatus
from shapely.geometry import Polygon, LineString
from shapely.ops import transform

api = Namespace('geoapi', description=GeoApiNamespace.description)
```

This adds the GeoAPI as a namespace object. `api` is imported and called by `modules/geoapi/__init__.py` which is loaded by `app/modules/__init__.py`. Sounds complicated at first, but it will make sense the more you will understand the basic modular structure of this project.

Your API is now equipped with its first namespace. Before trying it out, you'll have to add the name of your new namespace `geoapi` into the `ENABLED_MODULES` in your `config.py` so it'll look like this:

```python
     ENABLED_MODULES = {
        'api',
        'geoapi',
    }
```

Even though the first namespace of your first module exists, there will be no functionality attached to it. This is going to change in the next few lines. You start by first adding the basic geospatial data models to `app/modules/geoapi/resources.py` at the very bottom:

```python
bounding_box = api.model('BoundingBox', {
    'x_lat': fields.Float(),
    'y_lat': fields.Float(),
    'x_lng': fields.Float(),
    'y_lng': fields.Float(),
})

polygon = api.model('PolygonGeometry', {
    'type': fields.String(required=True, default="Polygon"),
    'coordinates': fields.List(
        fields.List(fields.Float, required=True, type="Array"),
        required=True, type="Array",
        default=[[13.4197998046875, 52.52624809700062],
                 [13.387527465820312, 52.53084314728766],
                 [13.366928100585938, 52.50535544522142],
                 [13.419113159179688, 52.501175722709434],
                 [13.4197998046875, 52.52624809700062]]
     )
})

polygon_feature = api.model('PolygonFeature', {
    'type': fields.String(default="Feature", require=True),
    'geometry': fields.Nested(polygon, required=True)
})

linestring = api.model('LineStringGeometry', {
    'type': fields.String(required=True, default="LineString"),
    'coordinates': fields.List(
        fields.List(fields.Float, required=True, type="Array"),
        required=True,
        type="Array",
        default=[[13.420143127441406, 52.515594085869914],
                 [13.421173095703125, 52.50535544522142],
                 [13.421173095703125, 52.49532344352079]]
     )
})

linestring_feature = api.model('LineStringFeature', {
    'type': fields.String(default="Feature", require=True),
    'geometry': fields.Nested(linestring, required=True)
})

point = api.model('PointGeometry', {
    'type': fields.String(required=True, default="Point"),
    'coordinates': fields.List(
        fields.List(fields.Float, required=True, type="Array"),
        required=True,
        type="Array",
        default=[13.421173095703125, 52.49532344352079]
     )
})

point_feature = api.model('PointFeature', {
    'type': fields.String(default="Feature", require=True),
    'geometry': fields.Nested(point, required=True)
})
```

Just take a moment and understand how the models are generated. You'll use the Polygon and LineString features in this tutorial. The remaining models are just exemplary and should provide you a base on which you can later build (hopefully) your own implementations on.

### Calculate the area of a polygon

As the first GeoAPI request, you'll implement a simple calculation to get the area of a Polygon into `app/modules/geoapi/resources.py`. The function is going to accept a GeoJSON object via a POST endpoint, deserialize it following the `PolygonFeature` model you provided above, calculate its area in the [Robinson projection](https://spatialreference.org/ref/esri/world-robinson/) and return the value.

Now go ahead and implement your first endpoint function and paste this code below the models:

```python
@api.route('/polygon/area/')
class PolygonArea(Resource):
    """
    Return the area of a polygon in m²
    """

    @api.expect(polygon_feature, validate=True)
    @api.doc(id='polygon_area')
    def post(self):
        """
         Return the area of a polygon in m²
        """

        try:
            projection = partial(
                pyproj.transform,
                pyproj.Proj(init='epsg:4326'),
                pyproj.Proj(init='epsg:3035')
            )

            return transform(
              projection,
              Polygon(request.json['geometry']['coordinates'])
            ).area
        except Exception as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, message="The GeoJSON polygon couldn't be processed.", error=err)
```
- `@api.route` decorator makes the endpoint accessible via `/polygon/area/` and provides a POST request method
- `@api.expect` gives RESTPlus the information against what data model the incoming data should be serialized against, in this case the `polygon_feature` model. `validate=True` forces RESTPlus to check that the post Input is actually the same as the api model.
- `transform` transforms the input WGS84 coordinates of the GeoJSON to the more appropriate `ETRS89 / LAEA Europe` projection (EPSG 3035). It takes a `pyproj` transformation definition and applies it on all coordintates via shapely's `transform` function
- the final return value is the transformed polygon's `area` in square meters

Go ahead, try it out! (Re-)-Start the server and browse to `http://127.0.0.1:4000/api/v1`. There you should see the new API by the name of `GeoAPI` and if you open it you'll see the first POST function.

In order to test it, expand the POST function and hit `TRY IT OUT!`. This will open an editor. Paste the following GeoJSON Polygon into it:

```json
{
   "type":"Feature",
   "geometry":{
      "type":"Polygon",
      "coordinates":[
         [
            13.4197998046875,
            52.52624809700062
         ],
         [
            13.387527465820312,
            52.53084314728766
         ],
         [
            13.366928100585938,
            52.50535544522142
         ],
         [
            13.419113159179688,
            52.501175722709434
         ],
         [
            13.4197998046875,
            52.52624809700062
         ]
      ]
   }
}
```

Now hit `Execute`. The result should be ~ `22689812`. Besides, the functionality, the Swagger UI provides you with all the information and tools you need to make valid API calls: A sophisticated JSON-Editor, and an automatically constructed `cURL` query as well as Example values on the right side.

### Geodesic distance from point to point

Your second API endpoint will take two coordinates as query string parameters, convert them to valid Python constructs and calculate the distance between them. So please go ahead and paste this content below the last endpoint to the bottom of the file `app/modules/geoapi/resources.py`:

```python
@api.route('/point/distance/')
@api.param('start_lat', 'Latitude of the start point e.g. 52.52624809700062', _in="query")
@api.param('start_lng', 'Longitude of the start point e.g. 13.4197998046875', _in="query")
@api.param('end_lat', 'Latitude of the end point e.g. 52.50535544522142', _in="query")
@api.param('end_lng', 'Longitude of the end point e.g. 13.366928100585938', _in="query")
class PointToPointDistance(Resource):
    """
    Return the distance in kilometers between two points.
    """

    @api.doc(id='point_to_point_distance')
    def get(self):
        """
        Return the distance in kilometers between two points.
        """
        if request.args.get('start_lat', '') and request.args.get('start_lng', '') and \
                request.args.get('end_lat', '') and request.args.get('end_lng', ''):
            try:
                return geopy.distance.distance(
                    GeopyPoint(
                        longitude=request.args.get('start_lng', type=float),
                        latitude=request.args.get('start_lat', type=float)
                    ),
                    GeopyPoint(
                        longitude=request.args.get('end_lng', type=float),
                        latitude=request.args.get('end_lat', type=float)
                    )
                 ).km
            except Exception:
                pass

        abort(HTTPStatus.BAD_REQUEST,
              message="Please provide a valid query e.g. with the following url arguments: "
                      "http://127.0.0.1:4000/api/geoapi/point/distance/?start_lng=8.83546&start_lat=53.071124&end_lng=10.006168&end_lat=53.549926")
```

The `@api.param` serves RESTPlus to be able to show the query parameters in the Swagger UI. The actual arguments are accessed via `request.args.get()` and then converted to GeoPy points with which the distance is calculated in km.

(Re)-Start your Server now. You'll notice how the Swagger UI is adapting to the new input variant and how nicely it's usable through the web app.

### Length of a linestring

The last API endpoint will consume a GeoJSON LineString object and return the length of it. This is straight-forward and similar to the first endpoint, just expecting a LineString object instead of a Polygon:

```python
@api.route('/linestring/length/')
class LinestringLength(Resource):
    """
    Return if the length in meter of a given GeoJSON LineString
    """

    @api.expect(linestring_feature, validate=True)
    @api.doc(id='linestring_length')
    def post(self):
        """
        Return if the length in meter of a given GeoJSON LineString
        """
        try:
            line_coordinates = request.json['geometry']['coordinates']
            length = 0
            for idx in range(len(line_coordinates) - 1):
                length += distance.distance(
                    line_coordinates[idx], line_coordinates[idx + 1]
                ).meters
            return meters
        except Exception as err:
            pass
        abort(HTTPStatus.BAD_REQUEST,
              message="Please provide a valid POST GeoJSON and valid query with the following url arguments.")
```

As you can see, this function expects the `linestring_feature` model this time. The function calculates the geodesic distance between all points in the LineString and sums them up to return the overall length of the LineString.

Again, restart the server and head over to the Swagger UI and test the function by pasting the following GeoJSON:
```json
{
   "type":"Feature",
   "geometry":{
      "type":"LineString",
      "coordinates":[
         [
            13.420143127441406,
            52.515594085869914
         ],
         [
            13.421173095703125,
            52.50535544522142
         ],
         [
            13.421173095703125,
            52.49532344352079
         ]
      ]
   }
}
```

This time the result will be wrapped in a JSON object:

```bash
{
  "distance_in_km": 5548811.897527216
}
```

## tl;dr

In case you skipped the tutorial but still want to test the API locally, get it from the GIS • OPS [tutorials repository](https://github.com/gis-ops/tutorials/tree/master/flask/examples/base_api):

```shell script
git clone https://github.com/gis-ops/tutorials.git
cd tutorials/flask/examples/base_api/
```

It's covering the basic functionality of the tutorial, but the Swagger-UI is highly customized. You like it and want to do it by yourself? Stay tuned, this topic of `how to customize Swagger-UI` together with Flask-RESTPlus will be covered in the next tutorials.   

Once you have entered the `base_api/` folder, create a `venv` and install the requirements with:

```bash
virtualenv -p python3 ./venv
source ./venv/bin/activate
pip -r requirements.txt
```

For explanations on how to set up `virtualenv` or `python3`, please read the first part of the tutorial.   

You should be able to run the api now with:
```python
python run.py
```

Access the API at:
```bash
http://127.0.0.1:4000/api/v1
```

### References:
-   [Flask](https://www.palletsprojects.com/p/flask/)   
-   [Flask-RESTPlus](https://flask-restplus.readthedocs.io/en/stable/)   
-   [Swagger UI](https://swagger.io/tools/swagger-ui/)   
