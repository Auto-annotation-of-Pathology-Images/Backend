from pathlib import Path
from .utils import md5_hash
import inspect


# CRUD operations of the database using pure SQL


def create_schema_for_slides(db):
    query = ("create table if not exists Slides"
             "(slide_ID VARCHAR(100) NOT NULL, "
             "slide_name VARCHAR(100) NOT NULL, "
             "slide_path VARCHAR(300) NOT NULL, "
             "PRIMARY KEY ( slide_ID ));")

    with db.cursor() as cursor:
        cursor.execute(query)
        db.commit()


def create_schema_for_annotations(db):
    query = ("create table if not exists Annotations"
             "(slide_ID VARCHAR(100) NOT NULL, "
             "annotation_path_before VARCHAR(300), "
             "annotation_path_after VARCHAR(300) NOT NULL, "
             "updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "
             "region_x INTEGER, "
             "region_y INTEGER, "
             "region_height INTEGER, "
             "region_width INTEGER, "
             "PRIMARY KEY ( slide_ID, annotation_path_after ), "
             "FOREIGN KEY ( slide_ID ) REFERENCES Slides(slide_ID));")

    with db.cursor() as cursor:
        cursor.execute(query)
        db.commit()


def get_slide_paths(db):
    """
    return all available slides' path
    Returns
    -------

    """
    sql = 'select DISTINCT slide_path from Slides;'

    with db.cursor() as cursor:
        cursor.execute(sql)
        slides_paths = [row[0] for row in cursor.fetchall()]

    return slides_paths


def get_slide_path_by_id(db, slide_id):

    sql = f"select DISTINCT slide_path from Slides where slide_ID = '{slide_id}';"

    with db.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchone()

    return result[0] if result else None


def get_newest_annotation(db, slide_id):
    """
    read the newest annotation path for a slide.

    Parameters
    ----------
    slide_id: str
        input slide id

    Returns
    -------
    newest_annotation_path: str
        the latest annotation's path for that slide
    """

    with db.cursor() as cursor:
        cursor.execute("select annotation_path_after from "
                       f"Annotations where slide_id = '{slide_id}' "
                       f"order by updated_time desc;")
        result = cursor.fetchone()

    return result[0] if result else None


def insert_new_slide_records(db, slide_paths):
    """
    Insert slide's information into the Database.

    file: the file name of the slide
    """

    query_template = (
        "insert into Slides (slide_ID, slide_name, slide_path) "
        "values ( %(slide_ID)s, %(slide_name)s, %(slide_path)s ) "
        "on duplicate key update slide_name = (%(slide_name)s), slide_path = (%(slide_path)s);"
    )

    args = []

    for slide_path in slide_paths:
        slide_path = Path(slide_path).absolute()
        slide_name = slide_path.name
        slide_ID = md5_hash(slide_path).hexdigest()

        args.append({
            "slide_ID": slide_ID,
            "slide_name": slide_name,
            "slide_path": str(slide_path)
        })

    with db.cursor() as cursor:
        cursor.executemany(query_template, args)
        db.commit()


def insert_new_annotation_records(db, slide_ids, annotation_paths):
    assert len(slide_ids) == len(annotation_paths), f"{len(slide_ids)} != {len(annotation_paths)}"

    query_template = (
        "insert into Annotations (slide_ID, annotation_path_after) "
        "values ( %(slide_id)s, %(annotation_path)s ) "
        "on duplicate key update "
        "annotation_path_after = (%(annotation_path)s);"
    )

    args = []

    for slide_id, annotation_path in zip(slide_ids, annotation_paths):
        args.append({
            "slide_id": slide_id,
            "annotation_path": str(annotation_path),
        })

    with db.cursor() as cursor:
        cursor.executemany(query_template, args)
        db.commit()


def insert_one_updated_annotation_record(db,
                                         slide_id,
                                         prev_annotation_path,
                                         updated_annotation_path,
                                         region_x,
                                         region_y,
                                         region_height,
                                         region_width):

    query = (
        "insert into Annotations "
        "(slide_ID, annotation_path_after, annotation_path_before, "
        "region_x, region_y, region_width, region_height) "
        f"values ('{slide_id}', '{updated_annotation_path}', '{prev_annotation_path}', "
        f"'{region_x}', '{region_y}', '{region_width}', '{region_height}')"
    )

    with db.cursor() as cursor:
        cursor.execute(query)
        db.commit()
