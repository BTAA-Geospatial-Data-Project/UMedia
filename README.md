# UMedia Maps Harvest
[UMedia](https://umedia.lib.umn.edu) provides access to digitized collections from across the University of Minnesota. These materials include photographs, archives, audio, video, maps, and more, with new items added on a regular basis. Thus, this repository is specifically for tracking UMedia Maps from **John R. Borchert Map Library**. 

The **John R. Borchert Map Library**, in the sub basement of Wilson Library, specializes in cartographic collections and geospatial services that support research and instruction. The Map Library also contains unique collections of cartographic materials related to Minnesota.

## Metadata Version
Metadata Version for this UMedia Maps harvest is updated to **Aardvark Version**. Please check the [B1G Aardvark Metadata Template](https://docs.google.com/spreadsheets/d/1g7TFqjYQ2KEShhocI0stINnI1cYDoMpoFgD8yWA6tbM/edit?pli=1#gid=1901875040) for more information.

## Environment Setup

Before execute the `harvest.py`, please make sure the following dependencies are installed already:
- jsons
- time
- csv
- urllib.request
- pandas
<!-- - [iso639-lang](https://pypi.org/project/iso639-lang/) -->

## Python Script
- **harvest.py**

The UMedia harvest script aims to find the newly added map items in a specific date range.Two manual inputs are needed once the execution starts:
1. Users need to input the expected `number` of search results. Since the search results return 20 maps by default, we need to set an approximate number to include all newly added maps.

2. Users also need to input a starting date in a `YYYY-MM` format, and the ending date will be current date by default. This will set a date range for the script to look for new maps.

- **find_bbox.ipynb**

If the `dateAdded_YYYYMM.csv` from **reports** folder does not include `Bounding Box` values, we need to run this python notebook to help find the missing bounding boxes. Here are some steps for finding the bounding box **after** you execute the `harvest.py` script and **have** the new `dateAdded_YYYYMM.csv` in the **reports** folder:

1. Download the lookup sheet from [Map Library pre-1930 Map Digitization Project](https://docs.google.com/spreadsheets/d/1A2MxmWxQ31_aDpxYQ5WSS9WcuoGdLGa9MOJWF-M7q6U/edit#gid=0) spreadsheets. Remember to find the correct sheet that includes all maps added recently. Usually, I will copy some random `Identifiers` from the metadata CSV file and use the **Find and Replace** tool from Google Sheet to search among all existing sheets, and the one which contains all these Identifiers is the sheet you need to download next. After download, please move this file into your working directory and rename it `bbox_lookup.csv` instead. 

2. Read the `bbox_lookup.csv` file and extract the **System Identifier** and its **Coordinates** only to a dictionary. Some values may have leading or trailing spaces, so that we need to remove the spaces by using the `strip()` method. 

3. Cleaning data will be the most important process, since the format from the `bbox_lookup.csv` are four `degree, minute, second` coordinates connected together by some characters like `/` and `--`. For example: `(E 12°00'--E 48°00'/N 57°00'--N 47°00').` We need to do the following cleanup steps before store into a new lookup dictionary:
    - So first of all, we will use the `clean_coords()` function to remove the parentheses and the trailing period, and separate it into 4 coordinates individually:  `E 12°00'`, `E 48°00'`, 
    `N 57°00'` and `N 47°00'`.

    - Next, continue using the `parse_dms()` function to parse each coordinate into `direction, degree, minute and second` separately.

    - Last, use the `dms2dd()` function to convert the coordinate from **DMS** to **Decimal Degree** with 4 digits after the decimal point.

4. Manual change the filename to the metadata CSV file from your **reports** folder, read and find the missing **bounding box** from the lookup dictionary.

5. Write the updated records into a csv file with the same filename to overwrite the previous one. And if there are more than one csv files with missing bounding boxes, please edit the filename and repeat the step 4 and 5.




## Folders
- **requests**

This folder stores all search results in JSON format for each reaccession as `request_YYYYMMDD.json`. 

- **jsons**

This folder stores all JSON files by different added month for UMedia maps. After we get the search result JSON file from each reaccession, we will read this `request_YYYYMMDD.json` file in detail to filter out the included maps by month, and store them to `dateAdded_YYYYMM.json` individually.

- **reports**

This folder stores all CSV files for metadata by month. Once we have JSON files for different month, we extract all useful metadata and contribute in the `dateAdded_YYYYMM.csv` in this folder.


## Google Drive
After we get the metadata CSV files from the **reports** folder, we need to upload them to the [Google Drive](https://drive.google.com/drive/u/0/folders/17ZvpFbTBPh7shYTx4m_hnP8AekqGj0wD) and do some manual edits for the **Temporal Coverage, Date Range**.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

If you have any questions, feel free to contact:
- Ziying(Gene) Cheng (cheng904@umn.edu)

## Updates
- Original created on Dec 01, 2020 by Gene Cheng

- Updated on May 1st, 2021 by Gene Cheng

- Update on Nov 08, 2021 by Gene Cheng
    - Remove `Publisher` field
    - No manual edit for `Title` field
    <!-- - Use [iso639-lang](https://pypi.org/project/iso639-lang/) library for ISO 639 standard to generate `Language` value to  **ISO 639-2 Code** -->

