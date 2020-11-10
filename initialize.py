import os
from utils import md5_hash
import pymysql
pymysql.install_as_MySQLdb() #if the error -- No module named 'MySQLdb' occured, use this for solution
import pymysql.cursors
import imageio
#Initialize the file system and \
#insert all initial files' records into the database system 
#1. insert all slides with annotations 
#2. prepare the small batches for the image

#c#configurations... can be moved to a config file in the future.
image_patch_size=256
root='/Users/Hamsik·kai/Desktop/capstone/backend/flask/MyFlaskProjects/'
slides_path=root+'files/slides/'
annotations_path=root+'files/annotations/'
patches_path=root+'files/patches/'
slide_suffix='.png' #png for dev mode, change to svs
annotation_suffix='.png' #png for dev mode, change to annotations
files=[x for x in os.listdir(slides_path) if slide_suffix in x]
connection = pymysql.connect(host='localhost',
                             port = 3306,
                             user='root',
                             password='aapl2020',                       
                             db='AAPL_DB')

print ("connect successful!!")

def insert_slide_intoDB(file):
    '''
    Insert slide's information into the Database.
    
    file: the file name of the slide
    '''
    file_path = slides_path+file
    annotations = annotations_path+file
    slide_ID = md5_hash(file_path).hexdigest()
    sql_Slides = 'insert into AAPL_DB.Slides (slide_ID, slide_name, slide_path) \
            values (\'{slide_ID}\', \'{slide_name}\', \'{slide_path}\');'.format( \
            slide_ID=slide_ID,
            slide_name=file,
            slide_path=file_path)
    sql_Annotations = 'insert into AAPL_DB.Annotations (slide_ID, annotation_path_after) \
            values (\'{slide_ID}\', \'{annotation_path_after}\');'.format( \
            slide_ID=slide_ID,
            annotation_path_after=annotations_path+file.replace(slide_suffix, annotation_suffix))
    with connection.cursor() as cursor: 
        cursor.execute(sql_Slides)
        cursor.execute(sql_Annotations)
        connection.commit()
    return 
    
def cut_slides_and_save(file, file_loaded, image_patch_size):
    '''
    Cut slides into patches
    
    Parameters
    ----------
    file: the file name
    file_loaded: the numpy array form of the slide (or other comparable types)
    image_patch_size: patch size, default 256
    '''
    slide_ID = md5_hash(slides_path+file).hexdigest()
    try:
        os.mkdir(patches_path+slide_ID)
    except:
        pass
    file_shape = file_loaded.shape
    x_num = file_shape[0] // image_patch_size + 1
    y_num = file_shape[1] // image_patch_size + 1
    for i in range(x_num):
        for j in range(y_num):
            file_patch = file_loaded[i*image_patch_size: (i+1)*image_patch_size,
                                     j*image_patch_size: (j+1)*image_patch_size,:]
            file_patch_path = patches_path + slide_ID + '/x={}&y={}.png'.format(i,j)
            #write to the file system... in png format 
            print('writing patches to...', file_patch_path)
            imageio.imwrite(file_patch_path, file_patch)
    return 

if __name__ == '__main__'
    for file in files:
        #TODO: change to another method laoding .svs file 
        file_loaded = imageio.imread(slides_path+file)
        insert_slide_intoDB(file)
        cut_slides_and_save(file, file_loaded, image_patch_size)
    connection.close()
    print('finished initializing the file system and the db.')
