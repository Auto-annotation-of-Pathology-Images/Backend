import os
import pymysql
pymysql.install_as_MySQLdb() #if the error -- No module named 'MySQLdb' occured, use this for solution
import pymysql.cursors
from flask import Flask, request, render_template, g, redirect, Response, jsonify, send_from_directory
import json
import datetime
from utils import md5_hash, get_newest_annotation, read_region, write_updated_annotation_to_file, insert_updated_annotation_to_sql
# from AAPI_code.ml_core.api import segment_ROI,segment_WSI

#define the app
app = Flask(__name__)
###configurations... can be changed to a config file in the future.
image_patch_size=256
root='/Users/Hamsik·kai/Desktop/MyFlaskProjects/Backend-main/'
static_folder=root+'files/'
slides_path=root+'files/slides/'
annotations_path=root+'files/annotations/'
patches_path=root+'files/patches/'
slide_suffix='.png' #png for dev mode, change to svs
annotation_suffix='.png' #png for dev mode, change to annotations

###connect to the database...
connection = pymysql.connect(host='localhost',
                            port = 3306,
                            user='root',
                            password='aapi2020',                       
                            db='AAPI_DB')

print ("connect successful!!")

print("START...")
@app.route('/')
def home():
    return 'home'

### function 1: return all available slides' path 
@app.route('/get_slides_pathes', methods = ['GET'])
def get_slides_names():
    sql = 'select slide_path from Slides;'
    if request.method == "GET":
        with connection.cursor() as cursor: 
            cursor.execute(sql)
            slides_path = []
            for result in cursor:
                slides_path.append(result[0])  
        return '\n'.join(slides_path)
    return

### function 2:  
### for a given <slide_id> and area, use could 
### 'GET' (view the slide's annotations) OR
### 'POST' (modify the annotation and enable the system to update them)
@app.route('/annotation/<slide_id>', methods = ['GET', 'POST'])
def annotation(slide_id):
    # test url: http://127.0.0.1:5000/annotation/a78eae29dd4c101feb7bc3f264786e7a?x=0&y=0&width=3000&height=3000
    # "a78e...786e7a" is the md5 hash for the first slide Dr.Coley sent us
    # "?x=0&y=0&width=3000&height=3000" is the argument list, can be empty
    # if empty, request.args.get("x") = None
    x = request.args.get("x")
    y = request.args.get("y")
    width = request.args.get("width")
    height = request.args.get("height")
    args_incomplete = x is None or y is None or width is None or height is None
    
    if request.method == 'GET':
        if args_incomplete:
            # use the following to get the annotation file
            newest_annotation_path = get_newest_annotation(slide_id)
            if slide_id is not None:
                return send_from_directory(newest_annotation_path) 
            else:
                #if there is no annotation for the whole slide, \
                #return None or return the prediction on the whoe slide?
                return None
                
        else:
            # should return the predicted annotation file for that region
            # read region... 
            region = read_region(slide_id, x,y,width, height)
            # use segment_ROI api in AAPI_code/ml_core/api.py 
            xml_annotation = segment_ROI(ROIs=[region],
                                        upper_left_coords=[(x,y)],
                                        label_info=None,
                                        batch_size=64,
                                        return_masks=False)
            return xml_annotation[0]

    elif request.method == 'POST':
        data = request.get_data() # byte array containing xml annotations
        str_data = data.decode("utf-8") # decode as string
        # 1. save the annotation to DB ... 
        # 2. merge the annotation 
        if args_incomplete:
            whole_slide = True
            #return("Receving POST request for annotation of the whole slide.")
            #for the whole slide, save {region_x, region_y, region_width, region_height} all as NULL
            region_x= region_y= region_width= region_height=None
        save_path,updated_time=write_updated_annotation_to_file(slide_id, srt_data, whole=whole_slide)
        insert_updated_annotation_to_sql(slide_id, save_path, updated_time,
                             region_x, region_y, region_width, region_height))
        return str_data

if __name__ == "__main__":
    app.run()
