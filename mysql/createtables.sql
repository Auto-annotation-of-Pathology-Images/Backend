CREATE DATABASE AAPL_DB;
use AAPL_DB;
-- drop table Slides, Annotations;
create table AAPL_DB.Slides(
   slide_ID VARCHAR(100) NOT NULL,
   slide_name VARCHAR(100) NOT NULL,
   slide_path VARCHAR(100) NOT NULL,
   PRIMARY KEY ( slide_ID )
);

create table AAPL_DB.Annotations(
   slide_ID VARCHAR(100) NOT NULL,
   annotation_path_before VARCHAR(100),
   annotation_path_after VARCHAR(100) NOT NULL,
   updated_time DATETIME NOT NULL
			    DEFAULT CURRENT_TIMESTAMP,
   region_x INT,
   region_y INT,
   region_height INT,
   region_width INT,
   PRIMARY KEY ( slide_ID, Annotation_path_after ),
   FOREIGN KEY ( slide_ID ) REFERENCES AAPL_DB.Slides(slide_ID)
);

-- insert into AAPL_DB.Slides (slide_ID, slide_name, slide_path )
-- values ('a78eae29dd4c101feb7bc3f264786e7a',
-- 'FFPE PostRep 001' , 
-- '/Users/Hamsik·kai/Desktop/MyFlaskProjects/new_webapp/files/slides/FFPE PostRep 001.svs');

-- insert into AAPL_DB.Annotations ( slide_ID, annotation_path_after )
-- values ('a78eae29dd4c101feb7bc3f264786e7a',
-- '/Users/Hamsik·kai/Desktop/MyFlaskProjects/new_webapp/files/slides/FFPE PostRep 001.svs');

-- select * from AAPL_DB.Slides;
-- select * from AAPL_DB.Annotations order by updated_time desc;
