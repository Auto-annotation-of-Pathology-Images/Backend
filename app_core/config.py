from os import environ


class Config:
    """Base config."""
    SECRET_KEY = environ.get('SECRET_KEY', 'justasimpledemosecretkey')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    DATABASE_USER = 'AAPI'
    DATABASE_PASSWORD = 'aapi2020'
    DATABASE_NAME ='AAPI_DB'

    PATCH_SIZE = 256


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
