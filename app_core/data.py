import click
from pathlib import Path
from shutil import copyfile

from flask.cli import with_appcontext
from flask import current_app
from .query import insert_new_annotation_records, insert_new_slide_records
from .utils import md5_hash, crop_patches_from_slide
from .db import get_db


@click.command("init-data")
@click.option('--slide_dir',
              help='Directory containing slides.')
@with_appcontext
def init_data_command(slide_dir):
    """Scan the Data directory, crop patches and insert records to DB"""
    slide_dir = Path(slide_dir)
    click.echo(f"Load data from {slide_dir}.")
    assert slide_dir.exists()
    slide_paths = [p.absolute() for p in slide_dir.glob("*.svs")]
    db = get_db()
    insert_new_slide_records(db, slide_paths)
    click.echo("Finish inserting slides info.")

    annotation_paths = [slide_path.with_suffix(".xml") for slide_path in slide_paths]
    valid_annotation_paths = []
    slide_ids = []
    for slide_path, annotation_path in zip(slide_paths, annotation_paths):
        if slide_path.exists() and annotation_path.exists():
            slide_id = md5_hash(slide_path).hexdigest()
            slide_ids.append(slide_id)

            moved_annotation_path = slide_dir.parent / Path(f"annotations/{slide_id}/initial_annotation.xml")
            if not moved_annotation_path.parent.exists():
                moved_annotation_path.parent.mkdir(parents=True)

            copyfile(str(annotation_path), str(moved_annotation_path))
            click.echo(f"Moved from {annotation_path} to {moved_annotation_path}.")
            valid_annotation_paths.append(moved_annotation_path.absolute())

    insert_new_annotation_records(db, slide_ids, valid_annotation_paths)
    click.echo("Finish inserting annotations info.")

    for slide_path in slide_paths:
        click.echo(f"Start cropping slide {slide_path.name}.")
        patch_size = current_app.config["PATCH_SIZE"]
        crop_patches_from_slide(slide_path, patch_size)
        click.echo(f"Finish cropping slide {slide_path.name}.")


def init_app(app):
    """Register data init function with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(lambda x: None)
    app.cli.add_command(init_data_command)
