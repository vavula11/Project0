# Project0
# IMDb Data Pipeline Project

I built this pipeline to process raw IMDb datasets using PySpark and load them into a ClickHouse database so they can be queried instantly for analytics. 

---

## The Numbers
The pipeline successfully cleaned, filtered, and loaded **1,403,369 total records** into the database with zero issues. Here is how the rows split up:
* **TV Episodes:** 870,001 rows
* **Movies:** 347,889 rows
* **Shorts:** 185,479 rows

---

## How the Architecture Works

* **Fixing Spark's Partition Issue:** When saving the cleaned data into a Parquet lakehouse structure, PySpark automatically drops the `titleType` column from inside the files and uses it to name the folders instead (e.g., `titleType=movie/`). To fix this, I used a regex path tool (`regexpExtract(_path, ...)`) inside ClickHouse's ingestion step to grab the category right out of the file paths on the fly.
* **Database Setup:** The database uses ClickHouse's `MergeTree` engine and is sorted by `(titleType, releaseYear, tconst)`. Because it is indexed this way, queries looking for specific content types take less than a millisecond to run.

---

## Why I Chose ClickHouse (Performance Note)
Dealing with over 1.4 million rows can slow down traditional row-based databases (like PostgreSQL or MySQL) when you start running big analytical queries. I chose ClickHouse because:
1. **It's Columnar:** ClickHouse reads data by columns rather than whole rows. If you write a query to calculate average ratings, the engine only reads the `averageRating` column from disk and ignores the massive text columns like movie titles and genres, making queries incredibly fast.
2. **Smart Skipping:** Because the data is physically organized on disk by our sorting keys, if a user filters specifically for TV episodes, ClickHouse knows exactly where they are and completely skips scanning the half-million movie and short records.

---

## How to Run It

Run these commands in order from your terminal to spin up the system and process the data:

### 1. Boot up the containers
Start up the Spark cluster and ClickHouse engine services:

docker-compose up -d

### 2. Run the PySpark ETL job
This command reaches into the Spark container to clean, filter, and partition the raw data:

docker exec -it spark-master /opt/spark/bin/spark-submit /src/etl_job.py

### 3. Load the data into ClickHouse
Run the database loader script locally to create the target tables and stream the Parquet files into the database:

python src/load_to_olap.py

### 4. Verify the database counts
Log into the ClickHouse client to confirm all 1.4 million rows loaded successfully:

docker exec -it olap-engine clickhouse-client --query "SELECT titleType, count() FROM default.content GROUP BY titleType"
