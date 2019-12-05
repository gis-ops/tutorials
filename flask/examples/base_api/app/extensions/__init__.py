from flask_cors import CORS

from . import api

cors = CORS()


def init_app(app):
    """
    Application extensions initialization.
    """
    for extension in (
            cors,
            api,
    ):
        extension.init_app(app)
