from pathlib import Path
from datetime import datetime
from shutil import copyfile

from .db import get_db
from .query import get_annotated_slide_ids, get_slide_path_by_id, get_newest_annotation

from AAPI_code.ml_core.utils import slide_utils
from AAPI_code.ml_core.utils.annotations import load_annotations_from_asap_xml
from AAPI_code.ml_core.preprocessing import patches_extraction, dataset
from AAPI_code.ml_core.modeling import utils as model_utils
from AAPI_code.ml_core.api import load_label_info_from_config, default_label_info_path


def crop_roi_from_latest_annotations(label_info, annotations, slide_path, save_dir):
    roi_paths_dict = {}
    for class_name in label_info["label_name"]:
        roi_paths = slide_utils.crop_ROI_using_annotations(slide_path=slide_path,
                                                           save_dir=Path(save_dir),
                                                           annotations=annotations,
                                                           class_name=class_name,
                                                           section_size=3000)

        roi_paths_dict[class_name] = roi_paths

    return roi_paths_dict


def generate_hdf5_from_roi(label_info, roi_paths_dict, save_dir):
    for label_row in label_info.itertuples():
        class_name = label_row.label_name
        if class_name in roi_paths_dict:
            extractor = patches_extraction.Extractor(config_section_name=label_row.extractor_config_name)
            paths = roi_paths_dict[class_name]
            img_paths = [p[0] for p in paths]
            mask_paths = [p[1] for p in paths]
            save_path = Path(save_dir) / Path(f"{class_name}.h5")
            patches_extraction.crop_and_save_patches_to_hdf5(save_path,
                                                             img_paths,
                                                             mask_paths,
                                                             extractor)


def update_model(label_info, train_slide_ids, roi_dir):
    for label_row in label_info.itertuples():
        model = label_row.model
        class_name = label_row.label_name

        ckpt_callback = model_utils.get_checkpoint_callback(save_top_k=1)

        train_fnames = [Path(roi_dir) / Path(slide_id) / f"{class_name}.h5"
                        for slide_id in train_slide_ids]

        train_data = dataset.create_dataloader(train_fnames,
                                               transform=model_utils.get_augmentation_transforms(),
                                               return_dataset=False)

        val_data = dataset.create_dataloader([Path(roi_dir) / Path(f"{class_name}_val.h5")],
                                             batch_size=64,
                                             shuffle=False,
                                             return_dataset=False)

        log_dir = Path(f"/tmp/{int(datetime.now().timestamp())}/")
        log_dir.mkdir(parents=True)

        trainer = model_utils.create_pl_trainer(use_gpu=True,
                                                root_dir=log_dir,
                                                epochs=5,
                                                checkpoint_callback=ckpt_callback)
        metrics = trainer.test(model, val_data)
        old_val_f1 = metrics[0]["test/f1_score"]

        trainer.fit(model, train_data, val_data)
        updated_val_f1 = ckpt_callback.best_model_score.detach().cpu().numpy()
        rel_improvement = (updated_val_f1 - old_val_f1) / old_val_f1 * 100
        print(f"Online updating summary: {updated_val_f1} ({old_val_f1}, {rel_improvement:.2f}%)")

        if rel_improvement > -5:
            old_model_path = label_row.model_path
            new_model_path = (Path(old_model_path).parent /
                              (datetime.now().isoformat(timespec='seconds') + ".ckpt"))
            copyfile(ckpt_callback.best_model_path, new_model_path)


def schedule_model_updates(app):
    with app.app_context():
        db = get_db()

        annotated_slide_ids = get_annotated_slide_ids(db)
        label_info = load_label_info_from_config(default_label_info_path)
        roi_dir = None

        for slide_id in annotated_slide_ids:
            annotation_path = get_newest_annotation(db, slide_id)
            slide_path = Path(get_slide_path_by_id(db, slide_id))

            if roi_dir is None:
                roi_dir = Path(slide_path).parent.parent / Path("roi/")

            save_dir = roi_dir / Path(f"{slide_id}/")
            annotations = load_annotations_from_asap_xml(annotation_path)

            print(f"Start collecting annotated ROI for slide {slide_path.name} ...")
            roi_paths_dict = crop_roi_from_latest_annotations(label_info,
                                                              annotations,
                                                              slide_path,
                                                              save_dir)
            print(f"Start aggregating ROIs as HDF5 files for slide {slide_path.name} ...")
            generate_hdf5_from_roi(label_info, roi_paths_dict, save_dir)

        if roi_dir is not None:
            print(f"Start updating models ...")
            update_model(label_info, annotated_slide_ids, roi_dir)



