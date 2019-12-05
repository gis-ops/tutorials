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
