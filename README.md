# Backend
Flask based backend for AAPI Platform.

## Install
1. Clone this repo **with submodule**;
    ```shell script
    # clone the repository
    # use --recurse-submodules to fetch the inner module for AAPI_Code
    $ git clone --recurse-submodules https://github.com/Auto-annotation-of-Pathology-Images/Backend
    $ cd Backend
    ```
2. Use a virtual environment to install all [required packages](requirements.txt);
3. Set environment variables
    ```shell script
    # install this package
    $ python -m pip install -e .
    # set env variables for this shell session
    $ export FLASK_APP=app_core
    $ export FLASK_ENV=production
    ```

## Data Preparation
The data preparation process can be divided into two parts,
1. database setup;
2. large local file setup (including slides, patches and annotations).

### Database
1. Install MySQL and create a user with the following credentials.
    ```json
    {
     "user" : "AAPI",
     "password": "aapi2020"
    }
    ```
   Then run the following commands using this account in MySQL to grant permissions,
   ```
   mysql> GRANT ALL PRIVILEGES ON *.* TO 'AAPI'@'localhost';
   ```
2. At the root of this repo, run **```flask init-db```** to setup proper schemas. Note that data will only be added **after the next step**.

### Local File System
Slides, a.k.a. Whole Slide Image (WSI), are usually quite large (~300MB). Therefore, 
slides are saved in the local file system instead of in the database.

An initial version of annotation is also needed for every slide in order to render on frontend before human modification.

The total structure of required initial data is shown below,
<pre>
/data
|— slides
|   |— slide_001.svs
|   |— slide_001.xml                   --->[initial annotation]
    |— …
|— roi
|   |— Artery_val.h5                   --->[static validation data]
|   |— Glomerulus_val.h5
|   |— Tubules_val.h5
</pre>

The current online updating strategy requires preparing sevral validation datasets beforehand, in order
to evaluate how the model performs given newly annotated data.

Then, run the following command to generate directories for future annotations and cached patches. 
```shell script
$ flask init-data --slide-dir {path_to_the_slides_folder}
```
The ```{path_to_the_slides_folder}``` variable to point to the same location of the slides directory shown above. 
Checkout ```flask init-data --help``` for other options.

After this step, the whole local file system will look like below,
<pre>
/data
|— slides                              --->[user provided]
|   |— slide_001.svs
|   |— slide_001.xml
|
|— patches                             ----[code generated]
|   |— slide_id/                       --->[md5 checksum]
|      |— patch001.png
|      |— patch002.png
|      |— …
|
|— annotations                         ----[code generated]
|   |— slide_id/                       --->[md5 checksum]
|       |— updated_at_time001.xml      
|       |— updated_at_time002.xml
|       |— …
|       |— initial_annotation.xml
</pre>

The background updating task will also add new data to this file system, which will cache cropped ROIs
and annotations from calibrated results sent from the frontend. After periodical updates, the ``roi``
directory will be augmented as,
<pre>
|— roi
|   |— {CLASS_NAME}_val.h5             --->[user provided]
|   |— slide_id/                       --->[code generated]
|       |— {CLASS_NAME}/
|           |— {cropped_ROI || ROI_mask}.png
|       |— ...
</pre>

## Launch 
```shell script
$ flask run
```
If ``FLASK_ENV=development``, the run command should be ``flask run --no-reload``, otherwise the background updating will 
be run twice every interval.

## Test
1. Download [test dataset](https://drive.google.com/drive/folders/1PJYMMrK1w-UTOmGkTp7CVnOivYW1WlgX?usp=sharing) and make it as the
 ```../Data``` directory (relative to the path of this repo).
2. Run ```pytest``` at the root of this repo to start existing tests.



