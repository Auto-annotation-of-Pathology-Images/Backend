import click
from flask import current_app
from flask import g
from flask.cli import with_appcontext

try:
    import pymysql
except ImportError:
    pymysql.install_as_MySQLdb()

from .query import create_schema_for_annotations, create_schema_for_slides


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "db" not in g:
        db_name = current_app.config["DATABASE_NAME"]
        g.db = pymysql.connect(host='localhost',
                               port=3306,
                               user=current_app.config["DATABASE_USER"],
                               password=current_app.config["DATABASE_PASSWORD"])

        with g.db.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")

        close_db()

        g.db = pymysql.connect(host='localhost',
                               port=3306,
                               user=current_app.config["DATABASE_USER"],
                               password=current_app.config["DATABASE_PASSWORD"],
                               db=db_name)

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    create_schema_for_slides(db)
    create_schema_for_annotations(db)


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Add Schema for Slides and Annotations."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
