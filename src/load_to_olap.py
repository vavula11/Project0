import clickhouse_connect
import os

def main():
    print("--- Starting Production OLAP Ingestion Step ---")
    ddl_output_path = "/data/ddl/create_star_schema.sql"
    
    # Connect to the ClickHouse engine container
    try:
        client = clickhouse_connect.get_client(host='olap-engine', port=8123)
    except Exception as e:
        print(f"[ERROR] Engine connection timed out: {e}")
        print("Retrying connection via localhost tracking route...")
        client = clickhouse_connect.get_client(host='127.0.0.1', port=8123, username='default', password='pass123')
    
    clickhouse_ddl = """-- =========================================================
-- Teleparty Enterprise Category-Partitioned Analytical Table
-- =========================================================

CREATE TABLE IF NOT EXISTS default.content 
(
    tconst String,
    titleType String,
    primaryTitle String,
    originalTitle String,
    releaseYear Int32,
    runtimeMinutes Nullable(Int32),
    genres Nullable(String),
    averageRating Nullable(Float32),
    numVotes Nullable(Int32)
) 
ENGINE = MergeTree()
ORDER BY (titleType, releaseYear, tconst);"""

    print("Initializing production target table structure in ClickHouse...")
    client.command(clickhouse_ddl)

    print("Exporting structural schema backup tracking scripts to /data/ddl/...")
    os.makedirs(os.path.dirname(ddl_output_path), exist_ok=True)
    with open(ddl_output_path, "w") as f:
        f.write(clickhouse_ddl)

    print("Bulk ingesting Parquet data streams into ClickHouse...")
    try:
        # 1. Clear out the corrupted empty-string data first
        client.command("TRUNCATE TABLE default.content;")
        
        # 2. Run the explicit path-extraction insert
        client.command("""
        INSERT INTO default.content 
        (tconst, titleType, primaryTitle, originalTitle, releaseYear, runtimeMinutes, genres, averageRating, numVotes)
        SELECT 
            tconst, 
            regexpExtract(_path, 'titleType=([^/]+)') AS titleType, -- Extracts category from folder name
            primaryTitle, 
            originalTitle, 
            releaseYear, 
            runtimeMinutes, 
            genres, 
            averageRating, 
            numVotes 
        FROM file('lake/clean_content/**/*.parquet', 'Parquet');
        """)
    except Exception as e:
        print(f"[ERROR] Bulk ingestion failed: {e}")
        return

    print("\n--- INGESTION REPORT SUMMARY ---")
    try:
        total_rows = client.command('SELECT count() FROM default.content;')
        movie_count = client.command("SELECT count() FROM default.content WHERE titleType = 'movie';")
        episode_count = client.command("SELECT count() FROM default.content WHERE titleType = 'tvEpisode';")
        short_count = client.command("SELECT count() FROM default.content WHERE titleType = 'short';")
        
        print(f"Total Combined Records Loaded: {total_rows}")
        print(f"  └─ Movies Processed:         {movie_count}")
        print(f"  └─ TV Episodes Processed:    {episode_count}")
        print(f"  └─ Shorts Processed:         {short_count}")
    except Exception as e:
        print(f"Could not fetch audit report: {e}")
    print("--------------------------------")
    print("--- Ingestion Job Completed Successfully ---")

if __name__ == "__main__":
    main()