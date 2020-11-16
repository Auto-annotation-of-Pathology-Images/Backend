# Backend
Flask based backend scripts.

After putting all slides and annotations in the file system, do the following to set up.

### First step: 
create database using mysql/schema.sql script.

### Second step: 
run initialize.py to insert all records into the DB and cut slides into patches 

More information are illustrated in the files/ and mysql/ folders


### file system
The file system is designed in following way:

<pre>
/files
|— slides
|   |— slide_name.svs
|
|— patches
|   |— slide_id/
|      |— patch001.png
|      |— patch002.png
|      |— …
|
|— annotations
|   |— slide_id/
|       |— updated_at_time001.xml
|       |— updated_at_time002.xml
|       |— …
|       |— initial_annotation.xml
</pre>

