import click
from pathlib import Path

from flask.cli import with_appcontext
from .query import insert_new_annotation_records, insert_new_slide_records
from .utils import md5_hash
from .db import get_db


@click.command("init-data")
@click.option('--slide_dir',
              default=Path(__file__).parent.parent / Path("../Data/slides/"),
              help='Directory containing slides.')
@click.option('--ncpu', default=1,
              help='Number of CPUs used for generating data.')
@with_appcontext
def init_data_command(slide_dir, ncpu):
    """Scan the Data directory, crop patches and insert records to DB"""
    slide_dir = Path(slide_dir)
    click.echo(f"Load data from {slide_dir}.\nUsing {ncpu} CPU.")
    slide_paths = [p.absolute() for p in slide_dir.glob("*.svs")]
    db = get_db()
    insert_new_slide_records(db, slide_paths)

    annotation_paths = [slide_path.with_suffix(".xml") for slide_path in slide_paths]
    valid_annotation_paths = []
    slide_ids = []
    for slide_path, annotation_path in zip(slide_paths, annotation_paths):
        if slide_path.exists() and annotation_path.exists():
            valid_annotation_paths.append(annotation_path)
            slide_ids.append(md5_hash(slide_path).hexdigest())
    insert_new_annotation_records(db, slide_ids, valid_annotation_paths)


def init_app(app):
    """Register data init function with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(lambda x: None)
    app.cli.add_command(init_data_command)
