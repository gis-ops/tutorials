# Flask GeoAPI — Flask with geospatial super powers

This tutorial will give an introduction on how to setup Flask, enable it with spatial capabilities and expose those functionalities via a REST API delivered by a customized Flask-RESTPlus.


**Note**, this tutorial is addressing developers with a basic understanding on Python and what spatial data is. Knowledge in Flask is not required as we're going to learn exactly that together ;).

The final example can be found in our [tutorial repository](https://github.com/gis-ops/tutorials/tree/master/flask/examples/simple_flask_setup).

![Flask GeoAPI](https://raw.githubusercontent.com/gis-ops/tutorials/flask_tutorial/flask/static/img/overview_geoapi_complete.png)


### Motivation
Spatial and geotagged data has become an important form data is stored and processed. The variety in which those data occurs is really great,
it can be tracked routes from self-driving cars, locations of your favourite POIs or just the spatial shape of your house.  
The cool thing about spatial data is, that more or less everything on the surface of this world can be tracked, stored and visualized,
the not so cool thing about all these possibilities is, programmers dealing with it have to handle a vast amount of data formats, structures, transmission protocols...

In this tutorial you'll explore how nice and easy it is with Flask to:
 -   setup your own spatially enabled REST API,
 -   structure the API logically,
 -   write three API endpoints that will retrieve and process spatial data
 -   make it accessible via an API,
 -   document your API, so it's understandable and
 -   give users the possibility to actually use it.

Why do we use Flask?
- Flask is a so called `microframework`. A piece of software that scores with its slim and lightweight core. There is nothing clunky in Flask, no big libraries that make it slow or inflexible.
Just a web server with tons of additions, that expand the functionality how you like.


**Goals**:

- Get familiar with the [Flask framework](https://palletsprojects.com/p/flask/)
- Create a Flask server from scratch
- Write and document your own REST API with Flask-RESTPlus
- Extend your API with (for now) three basic geospatial capabilities

> **Disclaimer**
>
> Validity only confirmed for **Ubuntu 18.04** and **Flask <= v1.1.1**

## Prerequisites

- Python >= 3.6
- virtualenv >= v16.7.7
- pip >= 19.2.3
- Basic understanding of Linux and Python

## 1 General setup
First checkout our latest tutorial git from github:
```bash
git clone https://github.com/gis-ops/tutorials.git gis-ops_tutorials
cd gis-ops_tutorials/flask/custom
```
This is going to be our working directory for this tutorial, so stay in there ;)…   

The first thing we're going to do now, is to create a new virtual environment. This way we ensure that we're starting on the same level:
```bash
virtualenv -p python3 ./venv
source ./venv/bin/activate
which python
```
You should now have a newly created virtual environment in your working directory with python3 as the base interpreter.
If the last command shows you that the basic python interpreter is like `/gis_ops_tutorials/flask/venv/bin/python`, then you're good to go.

To be able to set up Flask and your API, we need some basic dependencies for python. Everything you need, is collected already in `requirements.txt`. So just run:
```bash
pip install-r requirements.txt
```
-   Flask==1.1.1: This installs Flask with the version 1.1.1.   


## 2 Setup the Flask structure
We're going to set up the basic Flask structure now. During the setup it'll hopefully become clear, why we do it the way we do it.
The modular App structure will allow you to easily extend the API with new endpoints.
The first thing you should do is, to ensure the structure in /custom is as followed:
```
├──custom
   ├──config.py
   ├──run.py
   ├──static/*
   ├──app/templates/*
   ├──app/extensions/*
   ├──app/__init__.py
   ├──app/modules/api/__ini__.py
   ├──app/modules/geoapi/__init__.py
   ├──app/modules/geoapi/resources.py
   └──app/modules/__init__.py
```
As you can see the custom folder already contains some basic folders: `static` `app/extensions`, and `app/templates`. 
Those files are needed as a base for your API and to correctly serve the customized Swagger-UI. Feel free to explore them, but it won't be part of this tutorial.

### Create the Flask App
The base of every Flask Serer App is the `create_app` function. Without it, nothing will work. So go on and paste the following code into `app/__init__.py`:
```python
# encoding: utf-8
"""
Example RESTful API Server.
"""
from flask import Flask


def create_app(flask_config_name=None, **kwargs):
    """
    Entry point to the Flask RESTful Server application.
    """

    # Initialize the Flas-App
    app: Flask = Flask(__name__, **kwargs)

    # Load the config file
    app.config.from_object('config.DevelopmentConfig')

    # Initialize the API extensions
    from . import extensions
    extensions.init_app(app)

    # Initialize the actual API routes
    from . import modules
    modules.init_app(app)

    return app
```
This is going to be our Flask App.This is the entry point to the API we're going to create in the next steps.
If you study the code, you'll quickly understand what's going on from the comments. First the basic Flask App is initialized.
Then the local config is loaded, the API extensions get implemented and the actual routes added to the app.
The loaded extensions are making sure, that we can actually load our custom Swagger-UI from `static` and `app/templates` but are not
part of this tutorial. Just use them and be happy ;).  

### Integrate your custom Flask-RESTPlus API
The core part of the API is Flask-RESTPlus. It'll give your server the possibility to not only automatically generate a swagger-ui for us,
that is generated from the annotations and data models in our code but also to serialize and de-serialize data objects.
So, please paste the following into `app/modules/api/__init__.py`:
```python
# encoding: utf-8
"""
Flask-RESTplus API registration module
======================================
"""

from flask import Blueprint

from app.extensions.api import api_v1


class ApiPaths(object):
    APIPath = "/api"

# API endpoint initializer
def init_app(app, **kwargs):
    api_v1_blueprint = Blueprint('api', __name__, url_prefix=ApiPaths.APIPath)
    api_v1.init_app(api_v1_blueprint)
    app.register_blueprint(api_v1_blueprint)

```
This defines the basic API with Flask-RESTPlus at the `/api` API route and will be the url we later use, to access the Swagger-UI.
With `from app.extensions.api import api_v1` we're loading a customized version of the Swagger-UI. Just follow into the code if you're
interested in what is behind.
As you might have noticed, this file contains a `init_app` function, that gives us the possibility to load it with our Flask App.
The function itself integrates our API blueprint that we can later access to reach the Swagger-UI.


### Module importer
Now let's integrate the actual module importer, that gets called from our Application at `app/__init__.py`.
This will iterate over all modules that are located inside `app/modules/__init__.py` and are activated in the `ENABLED_MODULES` in the `config.py`.
So you already start seeing the modularity, right? :). If you don't want to spin up a certain endpoint, just deactivate it and it won't be accessible or shown in Swagger-UI.
For the import routine paste into `app/modules/__init__.py` the following code:

```python
def init_app(app, **kwargs):
    from importlib import import_module

    for module_name in app.config['ENABLED_MODULES']:
        import_module('.%s' % module_name, package=__name__).init_app(app, **kwargs)
```


### Set the config file
So, we just heard about the `config.py` and obviously our Flask App needs one. 
Let's set it up!    
Please create the `config.py` file in the base folder and paste the following content:
```python
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
You have a BaseConfig that serves as the basic object, holding all the information that's getting reused in every config.
The actual one used will be the DevelopmentConfig. You easily can add your custom Config here.
The `enabled_modules` is the place where you can activate and deactivate the API endpoints. For now only the `api` is present and 
that is the only endpoint that always needs to be loaded within the config file.

### Create the run file
In order to actually start the app we created in `app/__init__.py`, we need a runner routine names `run.py`. 
You should create that file in your base folder, next your `config.py`. So, paste the following into `run.py`:

```python
from app.__init__ import create_app


def run(
        host='127.0.0.1',
        port=4000,
):
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

From reading the comments you might already guess what's happening here. Creating the app and running it on `127.0.0.1:4000`

###  Test the basic API
If you followed the instructions you should now be able to spin up the API. It won't show you much besides the bare Swagger-UI frontend.

```bash
python run.py
```
Then call `http://127.0.0.1:4000/api/` to get to the actual Swagger-UI. If this works for you, good, if not, please go back a few steps and check you added everything correctly.


## 3. GeoAPI
Now, that our basic API is ready, let's fill it with life. First we're going to implement functionality with three simple geospatial capable api routes.
One will calculate the length of a GeoJSON LineString that is posted to the API, another the distance between two Points that we paste with the URL and 
the third the area of a GeoJSON Polygon that gets posted to the API like the LineString.   
The goal is to give you a broader example and insight on as much possible variances of how to get geospatial data into your server, parse it, process it and return the results back to the user.   

Mind for the following: No matter what new endpoint you will add on your own after this tutorial, the process will always be the same from here on.
And that is the beauty of that setup. You'll be able to just add as many modules as you like and initialize it automatically through the module loader. 
Please add the following content to `app/modules/geoapi/__init__.py`:
```python
# encoding: utf-8

from app.extensions.api import api_v1


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
This will initialize our new GeoAPI and load our API routes from `resources` into the namespace of the API.

In order to create the first routes, add the namespace to `app/modules/geoapi/resources.py` to the top of the file:

```python
# encoding: utf-8
# pylint: disable=bad-continuation
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
The `api =` part adds our GeoAPI as a namespace object. This is called by `modules/geoapi/__init__.py` which is loaded by `app/modules/__init__.py`. 
Sounds complicated first, but will make sense the more you will understand the basic modular structure of this project.

In order to work with geospatial GeoJSON Objects, we need to add new data models to the api namespace. In order to do so, add the following below the `api = ` part.

```python
bounding_box = api.model('BoundingBox', {
    'x_lat': fields.Float(),
    'y_lat': fields.Float(),
    'x_lng': fields.Float(),
    'y_lng': fields.Float(),
})

polygon = api.model('PolygonGeometry', {
    'type': fields.String(required=True, default="Polygon"),
    'coordinates': fields.List(fields.List(fields.Float, required=True, type="Array"),
                               required=True, type="Array", default=[[13.4197998046875, 52.52624809700062],
                                                                     [13.387527465820312, 52.53084314728766],
                                                                     [13.366928100585938, 52.50535544522142],
                                                                     [13.419113159179688, 52.501175722709434],
                                                                     [13.4197998046875, 52.52624809700062]])
})
polygon_feature = api.model('PolygonFeature', {
    'type': fields.String(default="Feature", require=True),
    'geometry': fields.Nested(polygon, required=True)
})

linestring = api.model('LineStringGeometry', {
    'type': fields.String(required=True, default="LineString"),
    'coordinates': fields.List(fields.List(fields.Float, required=True, type="Array"),
                               required=True, type="Array", default=[[13.420143127441406, 52.515594085869914],
                                                                     [13.421173095703125, 52.50535544522142],
                                                                     [13.421173095703125, 52.49532344352079]])
})

linestring_feature = api.model('LineStringFeature', {
    'type': fields.String(default="Feature", require=True),
    'geometry': fields.Nested(linestring, required=True)
})

point = api.model('PointGeometry', {
    'type': fields.String(required=True, default="Point"),
    'coordinates': fields.List(fields.List(fields.Float, required=True, type="Array"),
                               required=True, type="Array", default=[13.421173095703125, 52.49532344352079])
})

point_feature = api.model('PointFeature', {
    'type': fields.String(default="Feature", require=True),
    'geometry': fields.Nested(point, required=True)
})
```
You should take a moment and try to understand what is done with the api models. We'll use the polygon and linestring features in this tutorial,
the remaining models are just exemplaric and should provide you a base you can later continue (hopefully) your own implementations with.

### PolygonArea
As the first GeoAPI endpoint we'll implement a simple calculation to get the area of a Polygon provided by a POST request into `app/modules/geoapi/resources.py`.  
We're going to process GeoJSON data, that will get deserialized automatically by Flask-RESTPlus with the help of the namespace models.
Now let's integrate the actual first endpoint function and paste this code below the api models:

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
            return transform(pyproj.Proj(init='epsg:3857'), Polygon(request.json['geometry']['coordinates'])).area
        except Exception as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, message="The GeoJSON polygon couldn't be processed.", error=err)

```
Add this directly below the models. `@api.route` makes the endpoint accessible via `/polygon/area/` and provides a POST request method. 
`@api.expect` gives RESTPlus the information against what data model the incoming data should be serialized against, in this case the `polygon_feature`. 
The `validate=True` forces Flask-RESTPlus to check that the post Input is actually the same as the Api model.
Inside the try|catch routine the POST input GeoJSON is transformed with `EPSG:3857` before the area can be calculated.
The reason for that EPSG is, that the example geojson coordinates are taken from a projected coordinate system. 
`Transform`, together with the coordinates, constructs a valid Polygon for us. The `area` function called in the end just returns the area of that polygon in m² back to the client that made the request to the endpoint.   

Enough of the code. Let's try it out. Start the server and go to `http://127.0.0.1:4000/api`. There you should see the new API by the name of `GeoAPI`. If you open it you'll see the POST function.

In order to test it, expand the POST function and hit `TRY IT OUT!`. The result should be ~ `22689812`.
Besides the functionality the Swagger-UI serves you with all the information and tools you need to make valid API calls. 
A sophisticated JSON-Editor and an automatically constructed cURL query below as well as Example values on the right side.

### PointToPointDistance
Our second API endpoint will take two coordinates as query parameters, convert them to valid python constructs and calculate the distance between them.
So please go ahead and paste this content below our last ednpoint to the bottom of the file:
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
                return geopy.distance.distance(GeopyPoint(longitude=request.args.get('start_lng', type=float),
                                                          latitude=request.args.get('start_lat', type=float)),
                                               GeopyPoint(longitude=request.args.get('end_lng', type=float),
                                                          latitude=request.args.get('end_lat', type=float))).km
            except Exception:
                pass

        abort(HTTPStatus.BAD_REQUEST,
              message="Please provide a valid query e.g. with the following url arguments: "
                      "http://127.0.0.1:4000/api/geoapi/point/distance/?start_lng=8.83546&start_lat=53.071124&end_lng=10.006168&end_lat=53.549926")
```
The `@api.param` is new here and is part of the documentation. With them Flask-RESTPlus will be able to show the query parameters in the Swagger-UI.
In the actual try|catch the arguments are accessed via `request.args.get()` and then converted to Geopy Points with which the distance is calculated in km.   

(Re)-Start your Server now and start playing around with the new endpoint. You'll see very nicely, 
how the Swagger-UI is adapting to the new input variant and how nicely it's usable through the web App.

### LinestringLength
Our third and last API endpoint for this tutorial will take a GeoJSON LineString object and return the length of it.
This is straight forward and similar to the first endpoint, just expecting a LineString object instead of a Polygon:

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
            distance.VincentyDistance.ELLIPSOID = 'WGS-84'
            linestring = LineString(request.json['geometry']['coordinates'])
            return {"distance_in_m": distance.distance(linestring.xy[0], linestring.xy[1]).meters}
        except Exception as err:
            pass
        abort(HTTPStatus.BAD_REQUEST,
              message="Please provide a valid post GeoJSON and valid query with the following url arguments.")

```

As you can see, this function expects the `linestring_feature` this time, which is pretty similar to `PolygonArea`.
The function converts the parsed LineString to a Shapely LineString and calculates the distance by using an Ellipsoidal projection for the calculation.
Again, restart the server and head over to the Swagger-UI and test the function.

This time the result will be wrapped in a JSON construct:

```bash
{
  "distance_in_km": 5548811.897527216
}
```


## tl;dr

You can find a working solution in `/examples/base_api/`. Just go into that folder,  create a venv and install the requirements:
```bash
virtualenv -p python3 ./venv
source ./venv/bin/activate
pip -r requirements.txt
```
You should be able to run the api now with:
```python
pytho run.py
```

Access the API at:
```bash
http://127.0.0.1:4000/api/
```

### References:
-   [FLASK](https://www.palletsprojects.com/p/flask/)   
-   [FLASK-RESTPlus](https://flask-restplus.readthedocs.io/en/stable/)   
-   [Swagger-UI](https://swagger.io/tools/swagger-ui/)   
-   [Swagger-UI Themes](https://github.com/ostranme/swagger-ui-themes)   