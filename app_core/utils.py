#This file defined some functions used in server.py
import hashlib
import imageio
import numpy as np
import datetime
import os
from AAPI_code.ml_core.utils.annotations import create_asap_annotation_file, merge_annotations, load_annotations_from_asap_xml, load_annotations_from_halo_xml

def md5_hash(filename):
    with open(filename, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash

def get_newest_annotation(slide_id):
    '''
    read the newest annotation path for a slide.
    using g.conn.execute method to connect to the database

    Parameters
    ----------
    slide_id: str
        input slide id
    
    Returns 
    -------
    newest_annotation_path: str
        the latest annotation's path for that slide
    '''
    sql_get_newest_annotation = 'select annotation_path_after from AAPL_DB.Annotations where slide_id = \'{slide_id}\' order by updated_time desc;'.format(slide_id=slide_id)
    cursor = g.conn.execute(sql_get_newest_annotation)
    for result in cursor:
        break #get the first one for the newest
    newest_annotation_path=reulst[0]
    return newest_annotation_path

def read_region(slide_id, x,y,width, height):
    '''
    read the the slide's region by concatenating patches.

    Parameters
    ----------
    slide_id: str
        input slide id

    x, y: float 
        (x, y) is the upper left coordinates for the ROI on level 0
    
    width, height: float
        the size of the ROI
    
    Returns 
    -------
    region_img: 3-D numpy array
        the numpy array of the region 
    '''

    img_list=[]
    x_start = x//image_patch_size
    x_end = (x+width)//image_patch_size + 1
    y_start = y//image_patch_size
    y_end = (y+height)//image_patch_size + 1
    for i in range(x_start, x_end):
        img_y_list = []
        for j in range(y_start, y_end):
            file_patch_path = patches_path + slide_id + '/x={}&y={}.png'.format(i,j)
            img_y_list.append(imageio.imread(file_patch_path))
        img_list.append(np.concatenate(img_y_list, axis = 0))
    region_img = np.concatenate(img_list, axis = 1)
    return region_img


def write_updated_annotation_to_file(slide_id, str_data, whole = True):
    '''
    write the updated annotation to the file system

    Parameters
    ----------
    slide_id: str
        input slide id

    str_data: str 
        the decoded xml file sent from ASAP
    
    Returns 
    -------
    save_path: str
       the updated annotation's saved path
    
    updated_time: DATETIME
        the updated time 
    '''
    #transform the str_data into a list[Annotations] format
    #TODO: modify load_annotations_from_asap_xml to enable input as the encoded str
    merged_annotation = load_annotations_from_asap_xml(str_data)

    now = datetime.datetime.utcnow()
    updated_time = now.strftime('%Y-%m-%d %H:%M:%S')
    annotation_name = now.strftime('%Y-%m-%d %H-%M-%S')
    if not whole:
        #need to merge those the partial annotations to the whole 
        #first, get the latest annotation:
        latest_annotation_path = get_newest_annotation(slide_id)
        #TODO: change another way to determine the format of xml file
        try:
            latest_annotation = load_annotations_from_halo_xml(latest_annotation_path)
        except:
            latest_annotation = load_annotations_from_asap_xml(latest_annotation_path)
        #use api AAPI_code.ml_core.utils.annotations.annotations_group
        merged_annotation = annotations_group([merged_annotation, latest_annotation])
    try: 
        os.mkdir(app.static_folder+'annotations/{slide_id}/'.format(slide_id=slide_id))
    except:
        pass
    save_path = app.static_folder + \
        'annotations/{slide_id}/updated_at_{annotation_name}.annotations'\
        .format(slide_id=slide_id, annotation_name=annotation_name)
    create_asap_annotation_file(merged_annotation, save_path)
    return save_path, updated_time
    
def insert_updated_annotation_to_sql(slide_id, save_path, updated_time,
                                    x, y, width, height):
    '''
    insert the slide update record to the table 'Annotations'
    
    Parameters
    ----------
    slide_id: str
        input slide id

    save_path: str
       the updated annotation's saved path
    
    updated_time: DATETIME
        the updated time 
    
    x, y: float 
        (x, y) is the upper left coordinates for the ROI on level 0
    
    width, height: float
        the size of the ROI  
    '''
    annotation_path_before = get_newest_annotation(slide_id)
    sql_get_prev_annotation = 'select annotation_path_after from AAPL_DB.Annotations'
    sql_Annotation = 'insert into AAPL_DB.Annotations (slide_ID, region_x, region_y, region_width, region_height, update_time, annotation_path_before, annotation_path_after) \
    values (\'{slide_ID}\', \'{region_x}\', \'{region_y}\', \'{region_width}\', \'{region_height}\', \'{update_time}\', \'{annotation_path_before}\', \'{annotation_path_after}\');'.format( \
    slide_ID=slide_ID,
    region_x=x,
    region_y=y,
    region_width=width,
    region_height=height,
    update_time=updated_time,
    annotation_path_before=annotation_path_before,
    annotation_path_after=save_path)
    cursor = g.conn.excecute(sql_get_newest_annotation)
    return 
