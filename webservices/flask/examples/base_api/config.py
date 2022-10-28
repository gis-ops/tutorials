class BaseConfig(object):
    ENABLED_MODULES = {
        'api',
        'geoapi'
    }

    SWAGGER_UI_JSONEDITOR = True


class DevelopmentConfig(BaseConfig):
    """config for DevelopmentConfig."""
    DEBUG = False
    DEVELOPMENT = True
