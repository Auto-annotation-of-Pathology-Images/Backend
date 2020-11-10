## Database Design

The database is designed in the following way:

<pre>
table 1                    
Slides	                   
Key: slide_ID	             
slide_name	               
slide_path	               

table 2
Annotations
Key: slide_ID, Annotation_ID
Foreign key: slide_ID to Slides
Annotation_path_before
Annotation_path_after
update_time 
region_x
region_y
region_height
region_width
</pre>
