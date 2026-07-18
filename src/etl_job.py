from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def main():
    print("--- Starting Ultra-Fast Safe PySpark ETL Job ---")

    # 1. Initialize Spark Session inside the container
    spark = SparkSession.builder \
        .appName("IMDb-Teleparty-Fast") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .getOrCreate()
    
    # 2. Paths inside the docker container (mapping to local folders)

    basics_path = "/data/archive/title.basics.tsv"
    ratings_path = "/data/archive/title.ratings.tsv"
    output_lake_root = "/data/lake"
    
    # 3. Read the TSV files
    
    print("Loading core metadata...")
    df_basics = spark.read.csv(basics_path, sep=r'\t', header=True, nullValue=r'\N')
    df_ratings = spark.read.csv(ratings_path, sep=r'\t', header=True, nullValue=r'\N')

    # 4. Filter for necessary titletypes and clean up data types

    print("Filtering and transforming content...")
    df_content = df_basics.filter((col("titleType") == "movie") | (col("titleType") == "tvEpisode") | (col("titleType") == "short")) \
                          .select(
                              col("tconst"),
                              col("titleType"),
                              col("primaryTitle"),
                              col("originalTitle"),
                              col("startYear").cast("int").alias("releaseYear"),
                              col("runtimeMinutes").cast("int").alias("runtimeMinutes"),
                              col("genres")
                          )
    # 5. Clean up ratings data types

    df_clean_ratings = df_ratings.select(
        col("tconst"),
        col("averageRating").cast("float").alias("averageRating"),
        col("numVotes").cast("int").alias("numVotes")
    )
    
    df_fact_content = df_content.join(df_clean_ratings, on="tconst", how="inner")

    # 7. Write the output to a data lake folder

    print("Writing cleanly partitioned Parquet files to data lake...")
    df_fact_content.write.mode("overwrite").partitionBy("titleType").parquet(f"{output_lake_root}/clean_content")

    print("--- ETL Job Completed Successfully! ---")
    spark.stop()

if __name__ == "__main__":
    main()