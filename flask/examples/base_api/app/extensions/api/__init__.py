from copy import deepcopy

from flask import current_app
from flask_restplus import Api

api_v1 = Api(
    version='1.0',
    title="FLASK | FLASK-RESTPlus GeoAPI",
    description=(
        "This is a FLASK-RESPlus powered API with geospatial super power.\n\n"
        "Checkout more at https://gis-ops.com or https://github.com/gis-ops\n"
    ),
)

def serve_swaggerui_assets(path):
    """
    Swagger-UI assets serving route.
    """
    from flask import send_from_directory
    return send_from_directory('../static/', path)


def init_app(app, **kwargs):
    """
    API extension initialization point.
    """
    app.route('/swaggerui/<path:path>')(serve_swaggerui_assets)
