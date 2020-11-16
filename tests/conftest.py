import os
import tempfile

import pytest

from app_core import create_app
from app_core.db import get_db, init_db

# read in SQL for populating test data
with open(os.path.join(os.path.dirname(__file__), "test_data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    # create the app with common test config
    app = create_app({"TESTING": True, "DATABASE_NAME": "AAPI_DB_Test"})

    # create the database and load test data
    with app.app_context():
        init_db()

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()