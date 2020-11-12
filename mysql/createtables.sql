CREATE DATABASE IF NOT EXISTS AAPI_DB; 
use AAPI_DB;
-- drop table Slides, Annotations;
create table if not exists AAPI_DB.Slides(
   slide_ID VARCHAR(100) NOT NULL,
   slide_name VARCHAR(100) NOT NULL,
   slide_path VARCHAR(100) NOT NULL,
   PRIMARY KEY ( slide_ID )
);

create table if not exists AAPI_DB.Annotations(
   slide_ID VARCHAR(100) NOT NULL,
   annotation_path_before VARCHAR(100),
   annotation_path_after VARCHAR(100) NOT NULL,
   updated_time DATETIME NOT NULL
			    DEFAULT CURRENT_TIMESTAMP,
   region_x DOUBLE(12,4),
   region_y DOUBLE(12,4),
   region_height DOUBLE(12,4),
   region_width DOUBLE(12,4),
   PRIMARY KEY ( slide_ID, annotation_path_after ),
   FOREIGN KEY ( slide_ID ) REFERENCES AAPI_DB.Slides(slide_ID)
);
