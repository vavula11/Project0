# How I Used AI on This Project

* **AI Tool Used:** Gemini

Instead of just generating standard code, I used the AI as a debugging partner and a sounding board to build out this pipeline and fix some weird data bugs. 

Here is exactly how I used the prompts to get the project done:

---

### 1. Building the Foundation
* **What I asked:** "script to load to olap"
* **How it helped:** I used this to get the basic blueprint for the ClickHouse loader script. It gave me the starting code structure for the tables and helped me organize the data by `(titleType, releaseYear, tconst)` so that my queries would run fast.

### 2. Customizing the Filters
* **What I asked:** "filter((col("titleType") == "movie") | (col("titleType") == "tvEpisode") | (col("titleType") == "short")) \ i made this change" and "send the whole script again"
* **How it helped:** I needed the pipeline to handle three different types of video content at the same time. I showed the AI the filter logic I wanted to use, and we worked together to update both the PySpark ETL script and the loader script so they worked cleanly without dropping rows.

### 3. Cracking the Spark Partition Bug (The Hardest Part)
* **What I asked:** Feeding the AI raw error logs like ClickHouse `ILLEGAL_COLUMN (Code: 44)`.
* **How it helped:** This was a tricky bug. When PySpark saved the data as Parquet files, it automatically removed the `titleType` column from inside the files and used it to name the folders instead. Because the column vanished, ClickHouse crashed when trying to read it. I used the AI to help me write a regex path trick (`regexpExtract(_path, ...)`) that tells ClickHouse to look at the folder names and rebuild the missing data column automatically during ingestion.

### 4. Fixing Connection Snags
* **What I asked:** Pasting library errors like `ModuleNotFoundError` and `AUTHENTICATION_FAILED`.
* **How it helped:** I hit a few bumps getting my local Python environment to talk to the Docker containers. The AI helped me quickly troubleshoot these missing packages and port issues so the final loading script could run end-to-end.