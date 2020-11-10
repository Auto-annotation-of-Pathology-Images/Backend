#This file defined some functions used in server.py
import hashlib
import imageio
import numpy as np
import datetime
import os

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
    read the newest region given a slide_id.
    using g.conn.execute method
    '''
    sql_get_newest_annotation = 'select annotation_path_after from AAPL_DB.Annotations where slide_id = \'{slide_id}\' order by updated_time desc;'.format(slide_id=slide_id)
    cursor = g.conn.execute(sql_get_newest_annotation)
    for result in cursor:
        break #get the first one for the newest
    return reulst[0]

def read_region(slide_id, x,y,width, height):
    '''
    Input: slide_id, x,y,width, height
    Output: numpy array format for that specific part of the slide
    '''
    img_list=[]
    for i in range(x//image_patch_size, (x+width)//image_patch_size + 1):
        img_y_list = []
        for j in range(y//image_patch_size, (y+height)//image_patch_size + 1):
            file_patch_path = patches_path + slide_id + '/x={}&y={}.png'.format(i,j)
            img_y_list.append(imageio.imread(file_patch_path))
        img_list.append(np.concatenate(img_y_list, axis = 0))
    return(np.concatenate(img_list, axis = 1))

### TODO: find another way merging annotations in xml format.
def merge_annotations(whole, partial, x,y,width, height):
    '''
    merge the whole slide with the partially updated one
    '''
    whole[x:x+width, 
          y:y+height,:] = partial
    return whole

def write_annotation_to_file(slide_id, str_data, whole = True):
    '''
    write the updated annotation to the file system
    
    return the saved path and updated time for database insertion
    #TODO: change to the correct way writing the inputed str_data 
    '''
    
    now = datetime.datetime.utcnow()
    updated_time = now.strftime('%Y-%m-%d %H:%M:%S')
    annotation_name = now.strftime('%Y-%m-%d %H-%M-%S')
    if not whole:
        #need to merge those the partial annotations to the whole 
        #get the latest annotation:
        latest_annotation_path = get_newest_annotation(slide_id)
        latest_annotation = load(latest_annotation_path)
        merged_annotation = merge_annotations(str_data, latest_annotation)
    try: 
        os.mkdir(app.static_folder+'annotations/{slide_id}/'.format(slide_id=slide_id))
    except:
        pass
    save_path = app.static_folder + \
        'annotations/{slide_id}/updated_at_{annotation_name}.annotations'\
        .format(slide_id=slide_id, annotation_name=annotation_name)
    merged_annotation.write(save_path)
    return save_path, updated_time
    
def insert_annotation_to_sql(slide_id, save_path, updated_time,
                             region_x, region_y, region_width, region_height):
    '''
    insert the slide update record to the table 'Annotations'
    '''
    annotation_path_before = get_newest_annotation(slide_id)
    sql_get_prev_annotation = 'select annotation_path_after from AAPL_DB.Annotations'
    sql_Annotation = 'insert into AAPL_DB.Annotations (slide_ID, region_x, region_y, region_width, region_height, update_time, annotation_path_before, annotation_path_after) \
    values (\'{slide_ID}\', \'{region_x}\', \'{region_y}\', \'{region_width}\', \'{region_height}\', \'{update_time}\', \'{annotation_path_before}\', \'{annotation_path_after}\');'.format( \
    slide_ID=slide_ID,
    region_x=region_x,
    region_y=region_y,
    region_width=region_width,
    region_height=region_height,
    update_time=updated_time,
    annotation_path_before=annotation_path_before,
    annotation_path_after=save_path)
    cursor = g.conn.excecute(sql_get_newest_annotation)
    return 
