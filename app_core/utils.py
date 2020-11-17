import hashlib
from pathlib import Path
from typing import List
import datetime
from tempfile import NamedTemporaryFile

import imageio
from PIL import Image
import numpy as np
from shapely.geometry import box, Polygon


from AAPI_code.ml_core.utils.slide_utils import crop_ROI_from_slide
import AAPI_code.ml_core.utils.annotations as annotation_utils
import AAPI_code.ml_core.api as ml_api


def md5_hash(filename):
    with open(filename, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash


def format_timestamp(format_str="%Y-%m-%d %H:%M:%S",
                     dt: datetime.datetime = None):
    if dt is None:
        dt = datetime.datetime.now()
    return dt.strftime(format_str)


def patch_name_formatter(x, y, size):
    return f'x={x}_y={y}_size={size}.png'


def read_covered_patches_as_region(patches_root, patch_size, x, y, width, height):
    """
    read the the slide's region by concatenating patches.

    Parameters
    ----------
    patches_root: str or Path
        path to the root of patches in file system

    x, y: int
        (x, y) is the upper left coordinates for the ROI on level 0

    width, height: int
        the size of the ROI

    Returns
    -------
    region_img: PIL Image

    """
    img_list = []
    col_id_start = x // patch_size
    col_id_end = (x+width) // patch_size + 1
    row_id_start = y // patch_size
    row_id_end = (y+height) // patch_size + 1

    for col_id in range(col_id_start, col_id_end):
        one_col_images = []
        x = int(col_id * patch_size)
        for row_id in range(row_id_start, row_id_end):
            y = int(row_id * patch_size)
            patch_path = Path(patches_root) / patch_name_formatter(x, y, patch_size)
            one_col_images.append(imageio.imread(patch_path))
        img_list.append(np.concatenate(one_col_images, axis=0))
    region_img = np.concatenate(img_list, axis=1)
    region_img = Image.fromarray(region_img)
    return region_img


def crop_patches_from_slide(slide_path, patch_size):
    slide_id = md5_hash(slide_path).digest().hex()
    patches_root = Path(slide_path).parent.parent / Path(f"patches/{slide_id}/")

    if not patches_root.exists():
        patches_root.mkdir(parents=True)

    crop_ROI_from_slide(slide_path, patches_root, patch_size,
                        stride=patch_size,
                        level=0,
                        apply_otsu=False,
                        fname_formatter=patch_name_formatter,
                        overwrite_exist=False)


def _filter_annotations_by_region(annotations: List[annotation_utils.ASAPAnnotation],
                                  region_bbox: Polygon,
                                  keep_intersection):

    check_intersect_predicate = lambda geom: region_bbox.intersects(geom)

    # if keep_intersection == True, then keep all geoms where check_intersect_predicate = True;
    # otherwise, then keep all geoms where check_intersect_predicate = False;
    # in other words, keep those geoms where keep_intersection == check_intersect_predicate

    return list(filter(lambda annotation:
                        (check_intersect_predicate(annotation.geometry)) == keep_intersection,
                       annotations))


def replace_annotations_within_region(old_annotations: List[annotation_utils.ASAPAnnotation],
                                      new_annotations: List[annotation_utils.ASAPAnnotation],
                                      region_x,
                                      region_y,
                                      region_width,
                                      region_height):

    region_bbox = box(region_x, region_y, region_x + region_width, region_y + region_height)

    # keep all old annotations with NO intersections with current region
    combined_annotations = _filter_annotations_by_region(old_annotations, region_bbox, False)

    # keep all new annotations with intersections with current region
    combined_annotations.extend(_filter_annotations_by_region(new_annotations, region_bbox, True))

    return combined_annotations


def write_annotations_to_file(annotations, filename):
    parent_dir = Path(filename).parent

    if not parent_dir.exists():
        parent_dir.mkdir(parents=True)

    return annotation_utils.create_asap_annotation_file(annotations, filename)


def deserialize_annotations_from_str(xml_str):
    tmp_file = NamedTemporaryFile()

    with open(tmp_file.name, "w") as f:
        f.write(xml_str)

    annotations = annotation_utils.load_annotations_from_asap_xml(tmp_file.name)

    tmp_file.close()

    return annotations


def predict_on_region(region, region_x, region_y):
    return ml_api.segment_ROI([region], [(region_x, region_y)])


def predict_on_slide(slide_path):
    return ml_api.segment_WSI(slide_path)





