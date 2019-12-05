# encoding: utf-8

from app.extensions.api import api_v1


class GeoApiNamespace:
    namespace = "geoapi"
    description = "GeoAPI"


def init_app(app, **kwargs):
    """
    Init GeoAPI module.
    """
    # Touch underlying modules
    from . import resources

    api_v1.add_namespace(resources.api)
