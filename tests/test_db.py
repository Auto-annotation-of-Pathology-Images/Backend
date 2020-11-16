from app_core.db import get_db
from app_core import query
from app_core.utils import format_timestamp
from pathlib import Path


def test_insert_slide_record(app):
    with app.app_context():
        db = get_db()
        test_slide_path = Path(__file__).parent.parent / Path("../Data/slides/slide_001.svs")
        query.insert_new_slide_records(db, [test_slide_path])


def test_insert_annotation_record(app):
    with app.app_context():
        db = get_db()
        annotation_root = Path(__file__).parent.parent / Path("../Data/annotations/")
        test_annotation_dir = next(annotation_root.glob("*"))
        slide_id = str(test_annotation_dir.name)
        annotation_paths = list(test_annotation_dir.glob("*.xml"))
        query.insert_new_annotation_records(db,
                                            [slide_id] * len(annotation_paths),
                                            annotation_paths)


def test_get_most_recent_annotation(app):
    with app.app_context():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("""SELECT SLIDE_ID FROM Slides;""")
            slide_id = cursor.fetchone()[0]
        assert query.get_newest_annotation(db, slide_id) is not None


def test_insert_updated_record(app):
    with app.app_context():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("""SELECT SLIDE_ID FROM Slides;""")
            slide_id = cursor.fetchone()[0]

        most_recent_annotation_path = Path(query.get_newest_annotation(db, slide_id))

        test_updated_path = most_recent_annotation_path.parent / f"test_{format_timestamp()}.xml"
        query.insert_one_updated_annotation_record(db,
                                                   slide_id,
                                                   most_recent_annotation_path,
                                                   test_updated_path,
                                                   -1, -1, -1, -1)