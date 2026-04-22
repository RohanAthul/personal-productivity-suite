# Step 3: Loading Database

import pandas as pd
import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv

# CONFIGURATION & PATHING
try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    BASE_DIR = Path.cwd() 

PROCESSED_DIR = BASE_DIR / "Processed_Data"
SUMMARY_PARQUET = PROCESSED_DIR / "meeting_summary.parquet"
TRANSCRIPT_PARQUET = PROCESSED_DIR / "meeting_transcripts.parquet"

# Loading variables from env file
load_dotenv()

# SQL and NOSQL DATABASE CONNECTIONS
SQL_URL = os.getenv("SQL_URL")

SQL_ENGINE = create_engine(
    SQL_URL,
    connect_args={"ssl": {"fake_flag_to_enable_tls": True}},
    pool_pre_ping=True
)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

MONGO_CLIENT = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
MONGO_DB = MONGO_CLIENT[MONGO_DB_NAME]
MONGO_COLLECTION = MONGO_DB[MONGO_COLLECTION_NAME]

def get_existing_sql_ids(table_name, id_column):
    """
    Fetches the existing primary keys from a SQL table to prevent duplicates.
    Returns a set of IDs.
    """
    inspector = inspect(SQL_ENGINE)
    if not inspector.has_table(table_name):
        return set()

    query = text(f"SELECT {id_column} FROM {table_name}")
    try:
        with SQL_ENGINE.connect() as conn:
            existing_ids = pd.read_sql(query, conn)
            return set(existing_ids[id_column].unique())
    except Exception as e:
        print(f"Warning: Could not fetch existing IDs for {table_name}: {e}")
        return set()

def load_data_optimized():
    # --- SQL SECTION: Meeting Summaries ---
    if not SUMMARY_PARQUET.exists():
        print(f"Error: {SUMMARY_PARQUET} not found.")
        return

    print("Reading Summary Parquet...")
    df = pd.read_parquet(SUMMARY_PARQUET)
    
    BATCH_SIZE = 1000
    
    def safe_to_sql_delta(temp_df, table_name, pk_col):
        """
        Filters data against existing DB records and inserts only new rows.
        """
        # -- Get existing IDs from DB
        existing_ids = get_existing_sql_ids(table_name, pk_col)
        
        # -- Filter the DataFrame: Keep rows where pk_col is NOT in existing_ids
        if not existing_ids:
            new_data = temp_df
        else:
            new_data = temp_df[~temp_df[pk_col].isin(existing_ids)]
        
        count_new = len(new_data)
        
        if count_new == 0:
            print(f"  -> {table_name}: No new records to add (all duplicates).")
            return

        print(f"  -> {table_name}: Inserting {count_new} new records...")
        
        try:
            new_data.to_sql(
                table_name, 
                SQL_ENGINE, 
                if_exists='append', 
                index=False, 
                chunksize=BATCH_SIZE, 
                method='multi'
            )
            print(f"     Success.")
        except Exception as e:
            print(f"     Failed to insert into {table_name}: {e}")

    # Load Tables with Delta Checks
    # -- Cities (Primary Key: city_id)
    safe_to_sql_delta(
        df[['city_id', 'city']].drop_duplicates(), 
        'cities', 
        'city_id'
    )
    
    # -- Meetings (Primary Key: pk_id)
    safe_to_sql_delta(
        df[['pk_id', 'city_id', 'meeting_id']].drop_duplicates(), 
        'meetings', 
        'pk_id'
    )
    
    # -- Metrics (Primary Key: metric_id)
    metrics_cols = ['metric_id', 'pk_id', 'video_duration_sec', 'item_count', 'segment_count']
    safe_to_sql_delta(
        df[metrics_cols].drop_duplicates(), 
        'meeting_metrics', 
        'metric_id'
    )

    # --- MONGO SECTION: Transcripts ---
    print("\nChecking Transcripts...")
    if TRANSCRIPT_PARQUET.exists():
        df_transcripts = pd.read_parquet(TRANSCRIPT_PARQUET)
        
        # -- Fetch existing meeting_ids from MongoDB to avoid duplicates
        # Assuming 'meeting_id' is the unique identifier in your Mongo documents
        try:
            existing_mongo_ids = set(MONGO_COLLECTION.distinct("meeting_id"))
        except Exception as e:
            print(f"Warning: Could not fetch existing Mongo IDs: {e}")
            existing_mongo_ids = set()

        # -- Filter the dataframe
        if existing_mongo_ids:
            # Only keep rows where meeting_id is NOT in the existing set
            initial_count = len(df_transcripts)
            df_transcripts = df_transcripts[~df_transcripts['meeting_id'].isin(existing_mongo_ids)]
            filtered_count = len(df_transcripts)
            print(f"  -> Filtered out {initial_count - filtered_count} existing transcripts.")
        
        # -- Insert remaining
        if not df_transcripts.empty:
            records = df_transcripts.to_dict(orient='records')
            try:
                print(f"  -> Inserting {len(records)} new transcripts to Mongo...")
                result = MONGO_COLLECTION.insert_many(records)
                print(f"     Success! Inserted ids count: {len(result.inserted_ids)}")
            except Exception as e:
                print(f"     Mongo Insert Failed: {e}")
        else:
            print("  -> No new transcripts to upload.")

    else:
        print("Transcript Parquet file not found. Skipping Mongo step.")

if __name__ == "__main__":
    load_data_optimized()
