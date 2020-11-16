from flask import Blueprint, current_app
from flask import request, send_file

from .db import get_db
from .query import *
from .utils import read_covered_patches_as_region, predict_on_region, deserialize_annotations_from_str, \
    replace_annotations_within_region, write_annotations_to_file, format_timestamp

app = Blueprint("annotations", __name__)


@app.route('/')
def home():
    return 'home'


@app.route('/slide_paths', methods=['GET'])
def slide_paths():
    retrieved_slide_paths = get_slide_paths(get_db())
    return "".join(retrieved_slide_paths)


@app.route('/annotation/<slide_id>', methods=['GET', 'POST'])
def annotation(slide_id):
    """
   Retrieve or update an annotation file
    for a given <slide_id> and region (optional, see below examples for details),
    'GET' (view the slide's annotations) OR
    'POST' (modify the annotation and enable the system to update them)

    Parameters
    ----------
    slide_id

    Returns
    -------
    str
    ASAP format xml annotation encoded in a string

    Examples
    _______

    # test url: http://127.0.0.1:5000/annotation/a78eae29dd4c101feb7bc3f264786e7a?x=0&y=0&width=3000&height=3000
    # "a78e...786e7a" is the md5 hash for the first slide Dr.Coley sent us
    # "?x=0&y=0&width=3000&height=3000" is the argument list, can be empty
    # if empty, request.args.get("x") = None

    """

    x = request.args.get("x", type=int)
    y = request.args.get("y", type=int)
    width = request.args.get("width", type=int)
    height = request.args.get("height", type=int)
    args_incomplete = x is None or y is None or width is None or height is None
    db = get_db()

    if request.method == 'GET':
        if args_incomplete:
            # use the following to get the annotation file
            annotation_path = get_newest_annotation(db, slide_id)
            if Path(annotation_path).exists():
                return send_file(annotation_path)
            else:
                # if there is no annotation for the whole slide, \
                # return None or return the prediction on the whole slide?
                return None

        else:
            # should return the predicted annotation file for that region
            # read region
            slide_path = get_slide_path_by_id(db, slide_id)
            if slide_path:
                patches_dir = Path(slide_path).parent.parent / Path(f"patches/{slide_id}")
                patch_size = current_app.config["PATCH_SIZE"]
                if patches_dir.exists():
                    region = read_covered_patches_as_region(patches_dir, patch_size, x, y, width, height)
                    calibrated_x, calibrated_y = patch_size * (x // patch_size), patch_size * (y // patch_size)
                    xml_annotation = predict_on_region(region, calibrated_x, calibrated_y)
                    return xml_annotation

            return None

    elif request.method == 'POST':
        data = request.get_data()  # byte array containing xml annotations
        str_data = data.decode("utf-8")  # decode as string

        most_recent_annotation_path = get_newest_annotation(db, slide_id)
        old_annotations = []
        if most_recent_annotation_path and Path(most_recent_annotation_path).exists():
            with open(most_recent_annotation_path) as f:
                res = f.read()
                old_annotations = deserialize_annotations_from_str(res)
        new_annotations = deserialize_annotations_from_str(str_data)

        if args_incomplete:
            x, y, width, height = 0, 0, 1e8, 1e8

        updated_annotations = replace_annotations_within_region(old_annotations, new_annotations,
                                                               x, y, width, height)

        slide_path = get_slide_path_by_id(db, slide_id)
        if slide_path:
            updated_annotation_path = Path(slide_path).parent.parent / \
                                      Path(f"annotations/{slide_id}/updated_at_{format_timestamp()}")

            write_annotations_to_file(updated_annotations, updated_annotation_path)

            insert_one_updated_annotation_record(db, slide_id,
                                                 prev_annotation_path=most_recent_annotation_path,
                                                 updated_annotation_path=updated_annotation_path,
                                                 region_x=x,
                                                 region_y=y,
                                                 region_height=height,
                                                 region_width=width)

        return str_data
