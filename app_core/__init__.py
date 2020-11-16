from flask import Flask
from .config import Config

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config is not None:
        # load the test config if passed in
        app.config.update(test_config)

    # register the database commands
    from app_core import db
    db.init_app(app)

    # register the data command
    from app_core import data
    data.init_app(app)

    # apply the blueprints to the app
    from app_core import annotation
    app.register_blueprint(annotation.app)

    return app
