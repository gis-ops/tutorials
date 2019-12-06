# encoding: utf-8
"""
Flask-RESTplus API registration module
======================================
"""

from flask import Blueprint

from app.extensions.api import api_v1


class ApiPaths(object):
    APIPath = "/api/v1"

# API endpoint initializer
def init_app(app, **kwargs):
    api_v1_blueprint = Blueprint('api', __name__, url_prefix=ApiPaths.APIPath)
    api_v1.init_app(api_v1_blueprint)
    app.register_blueprint(api_v1_blueprint)
