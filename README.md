# Data Wrangling with MongoDB


Data Wrangling process involves the following steps:
- Gathering
- Extracting
- Cleaning
- Storing the data
Analysis of the data is carried out after these steps.

Gathering the data
* In this project the data of "The Southampton of England" was gathered from the website called  https://www.openstreetmap.org, as per the instructions.
* "The uncompressed size of the file must be atleast 50MB" was one of the criteria to choose a data.
* The compressed data file was downloaded and found that they were much larger in an uncompressed format .
* The data of fairly small size was selected to avoid the long execution times for each query.

Extracting the data
* The data was extracted from the metro extracts section of the openstreetmap.org. The data was in compressed format.
* The compressed data was then unzipped to get the actual data of size greater than 50MB.
* The part of the world, chosen for this project is Southampton of England. The uncompressed size of the file is about 63MB.

File size

Southampton.osm 63.0 MB

Southampton.osm.bz2 4.5 MB

Cleaning the data
* Data cleaning is an iterative process involves identifying the problems and fix them.
* The data may contain missing or extra fields, that needs to be fixed.
* Json document may not be in the expected structure, that needs to be fixed.

Storing the data
* Creating a local host connection with MongoDB and a database named "maps" was created .
* Pymongo(a library) was used to connect to the database.
* The data was uploaded into the database.
* various queries were created and run on the database to get required information.

This project helped me to
- Assess the quality of the data for validity, accuracy, completeness, consistency and uniformity.
- Parse and gather data from popular file formats such as .csv, .json, .xml, and .html
- Process data from multiple files or very large files that can be cleaned programmatically.
- store, query and aggregate data using MongoDB.
