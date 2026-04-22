# %% [markdown]
# # <center> Step 4: SQL Optimization

# %%
from IPython.display import Image

Image(filename='database_schema.jpeg')

# %% [markdown]
# ## Loading necessary libraries

# %%
import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
import requests
import os
import time
from sqlalchemy import create_engine, inspect
from sqlalchemy import text
import re
from dotenv import load_dotenv
from IPython.display import display

import warnings
warnings.filterwarnings("ignore")

# %% [markdown]
# ## Core connection

# %%
# Load the variables from the .env file
load_dotenv()

# SQL Config
SQL_URL = os.getenv("SQL_URL")

SQL_ENGINE = create_engine(
    SQL_URL,
    connect_args={"ssl": {"fake_flag_to_enable_tls": True}}
)

# %% [markdown]
# #### Creating Denormalized table with Primary key

# %%
# Fetch the data into Python
query = """
SELECT 
    c.city_id, c.city, m.pk_id, m.meeting_id,
    mm.metric_id, mm.video_duration_sec, mm.item_count, mm.segment_count
FROM cities c
JOIN meetings m ON c.city_id = m.city_id
JOIN meeting_metrics mm ON m.pk_id = mm.pk_id;
"""

with SQL_ENGINE.connect() as conn:
    print("Fetching data...")
    df = pd.read_sql(text(query), conn)

    # Manually create the table with a Primary Key
    # We drop table if it exists first to ensure a clean slate
    conn.execute(text("DROP TABLE IF EXISTS denormalized_table"))
    
    create_statement = """
    CREATE TABLE denormalized_table (
        metric_id BIGINT PRIMARY KEY,
        city_id BIGINT,
        city VARCHAR(255),
        pk_id BIGINT,
        meeting_id VARCHAR(255),
        video_duration_sec BIGINT,
        item_count BIGINT,
        segment_count BIGINT
    );
    """
    print("Creating table with Primary Key...")
    conn.execute(text(create_statement))
    conn.commit()

    # Use to_sql to 'append' the data to the existing structure
    print(f"Uploading {len(df)} rows...")
    df.to_sql(
        'denormalized_table', 
        con=conn, 
        if_exists='append', 
        index=False, 
        chunksize=500
    )
    conn.commit()

print("Success! Denormalized table created with a Primary Key.")

# %% [markdown]
# #### Reading tables from Database

# %%
def inspect_database(engine):
    # Get all table names from the database
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    print(f"Connected to Database. Found {len(table_names)} tables.\n")
    print("-" * 50)

    for table in table_names:
        # Load table into a Pandas DataFrame
 
        try:
            df = pd.read_sql(f"SELECT * FROM `{table}`", engine)
            
            # Collect Details
            rows, cols = df.shape
            memory_usage = df.memory_usage(deep=True).sum() / 1024  # KB
            
            print(f"TABLE: {table}")
            print(f"  - Shape: {rows} rows x {cols} columns")
            print(f"  - Size in Memory: {memory_usage:.2f} KB")
            print(f"  - Columns & Types:")
            
            # Displaying column names and types concisely
            for col, dtype in df.dtypes.items():
                print(f"    - {col}: {dtype}")
                
            print("-" * 50)
            
        except Exception as e:
            print(f"Error reading table {table}: {e}")

if __name__ == "__main__":
    inspect_database(SQL_ENGINE)

# %% [markdown]
# #### Printing sample from tables

# %%
# List of your table names
tables = ["cities", "meetings", "meeting_metrics","denormalized_table"]

with SQL_ENGINE.connect() as conn:
    for table in tables:
        print(f"--- Table: {table} (First few rows) ---")
        
        # Query with limit - viewing a sample
        query = text(f"SELECT * FROM {table} LIMIT 5")
        df = pd.read_sql(query, conn)
        
        # Display the dataframe
        display(df)
        print("\n")

# %% [markdown]
# #### Inefficient query example

# %%
def run_denormalized_inefficient():
    # Drop the index if it exists
    with SQL_ENGINE.connect() as conn:
        try:
            # Removing the index so MySQL has to do a Full Table Scan - 
            conn.execute(text("DROP INDEX idx_city_denormalized ON denormalized_table"))
            conn.commit()
        except Exception:
            pass 

    # Executing and timing the query
    start_time = time.perf_counter()
    
    # Grouping by a non-indexed VARCHAR column
    query = """
    SELECT 
        city,
        AVG(video_duration_sec) AS avg_duration
    FROM denormalized_table
    GROUP BY city;
    """
    
    with SQL_ENGINE.connect() as conn:
        df = pd.read_sql(text(query), conn)
        
    end_time = time.perf_counter()
    return df, end_time - start_time

df_bad_denorm, time_bad_denorm = run_denormalized_inefficient()
print(f"Inefficient Denormalized Runtime: {time_bad_denorm:.4f} seconds")
display(df_bad_denorm.head())

# %% [markdown]
# #### Optimized query

# %%
def run_optimized_efficient():
    # Recreating the test environment: Dropping and recreating the Index
    with SQL_ENGINE.connect() as conn:
        # Dropping if it exists to avoid a 'Duplicate key' error
        try:
            conn.execute(text("DROP INDEX idx_city_search ON cities"))
            conn.commit()
        except Exception:
            pass 
            
        print("Creating index for optimization...")
        conn.execute(text("CREATE INDEX idx_city_search ON cities(city)"))
        conn.commit()
            
    # Executing and timing the query
    start_time = time.perf_counter()
    
    # Aggregating on integers in a subquery to optimize efficiency
    query = """
    SELECT 
        c.city,
        sub.avg_duration
    FROM cities c
    JOIN (
        SELECT 
            m.city_id, 
            AVG(mm.video_duration_sec) AS avg_duration
        FROM meetings m
        JOIN meeting_metrics mm ON m.pk_id = mm.pk_id
        GROUP BY m.city_id
    ) sub ON c.city_id = sub.city_id;
    """
    
    with SQL_ENGINE.connect() as conn:
        df = pd.read_sql(text(query), conn)
        
    end_time = time.perf_counter()
    return df, end_time - start_time

df_good, time_good = run_optimized_efficient()
print(f"Optimized Efficient Runtime: {time_good:.4f} seconds")
display(df_good.head())

# %% [markdown]
# #### EXPLAIN ANALYZE querry

# %%
def explain_denormalized_inefficient():
    # Drop the index to force inefficiency for demonstration purposes
    with SQL_ENGINE.connect() as conn:
        try:
            conn.execute(text("DROP INDEX idx_city_denormalized ON denormalized_table"))
            conn.commit()
        except Exception:
            pass 

    # EXPLAIN ANALYZE to the raw SQL
    query = """
    EXPLAIN ANALYZE
    SELECT 
        city,
        AVG(video_duration_sec) AS avg_duration
    FROM denormalized_table
    GROUP BY city;
    """
    
    with SQL_ENGINE.connect() as conn:
        # We use .scalar() or fetchone() because EXPLAIN ANALYZE returns a text block
        result = conn.execute(text(query))
        plan = result.fetchone()[0]
        
    return plan

# Execute and print
plan_bad = explain_denormalized_inefficient()
print("--- Inefficient Query Plan ---")
print(plan_bad)

# %%
def explain_optimized_efficient():
    # Ensure index exists for optimization
    with SQL_ENGINE.connect() as conn:
        try:
            conn.execute(text("CREATE INDEX idx_city_search ON cities(city)"))
            conn.commit()
        except Exception:
            pass 
            
    # EXPLAIN ANALYZE to the "complex" query
    query = """
    EXPLAIN ANALYZE
    SELECT 
        c.city,
        sub.avg_duration
    FROM cities c
    JOIN (
        SELECT 
            m.city_id, 
            AVG(mm.video_duration_sec) AS avg_duration
        FROM meetings m
        JOIN meeting_metrics mm ON m.pk_id = mm.pk_id
        GROUP BY m.city_id
    ) sub ON c.city_id = sub.city_id;
    """
    
    with SQL_ENGINE.connect() as conn:
        result = conn.execute(text(query))
        plan = result.fetchone()[0]
        
    return plan

# Execute and print
plan_good = explain_optimized_efficient()
print("--- Optimized Query Plan ---")
print(plan_good)

# %% [markdown]
# #### EXPLAIN ANALYZE Performance report

# %%
def print_business_summary(plan_text, query_name):
    # Extract the total time from the very first line (the root of the query)
    time_match = re.search(r'actual time=\d+\.\d+\.\.(\d+\.\d+)', plan_text)
    total_time = time_match.group(1) if time_match else "Unknown"
    
    # Extract how many rows the database *guessed* it needed to look at
    rows_match = re.search(r'rows=(\d+)', plan_text)
    total_rows = rows_match.group(1) if rows_match else "Unknown"

    # Look for key "Red Flags" or "Green Flags"
    is_brute_force = "Table scan" in plan_text
    
    # Print the clean dashboard
    print(f"Performance Report: {query_name}")
    print("-" * 50)
    print(f"Total Time Taken : {total_time} milliseconds")
    print(f"Data Volume Touched: ~{total_rows} rows")
    
    if is_brute_force:
        print("Strategy: 'Brute Force' (Full Table Scan)")
        print("Explanation: The database read every single row in the table like ")
        print("reading a book cover-to-cover to find one word. This is fine for ")
        print("small amounts of data, but will cause major lag as the system grows.")
    else:
        print("Strategy: 'Surgical Precision' (Index Lookup)")
        print("Explanation: The database used an index (like a book's glossary) ")
        print("to jump straight to the exact data needed. This will stay lightning ")
        print("fast even if we add millions of rows to the system.")
    print("-" * 50)
    print("\n")

# %%
print_business_summary(plan_bad, "Inefficient Query (No Indexes)")
print_business_summary(plan_good, "Optimized Query (Indexed & Normalized)")

# %% [markdown]
# ## Advanced Query Implementation

# %%
def run_avg_segment_count_query():
    # Recreating the test environment: Dropping and recreating the Index
    with SQL_ENGINE.connect() as conn:
        # Dropping if it exists to avoid a 'Duplicate key' error
        try:
            conn.execute(text("DROP INDEX idx_city_search ON cities"))
            conn.commit()
        except Exception:
            pass 
            
        print("Creating index for optimization...")
        conn.execute(text("CREATE INDEX idx_city_search ON cities(city)"))
        conn.commit()
            
    # Executing and timing the query
    start_time = time.perf_counter()
    
    # Using the CTE to calculate average segment count by city
    query = """
    WITH city_segments AS (
        SELECT 
            m.city_id,
            AVG(mm.segment_count) AS avg_segments
        FROM meetings m
        JOIN meeting_metrics mm ON m.pk_id = mm.pk_id
        GROUP BY m.city_id
    )
    SELECT 
        c.city, 
        cs.avg_segments
    FROM cities c
    JOIN city_segments cs ON c.city_id = cs.city_id;
    """
    
    with SQL_ENGINE.connect() as conn:
        df = pd.read_sql(text(query), conn)
        
    end_time = time.perf_counter()
    return df, end_time - start_time

# Execute, unpack, and display the results
df_segments, time_segments = run_avg_segment_count_query()
print(f"CTE Query Runtime: {time_segments:.4f} seconds")
display(df_segments.head())

# %%
def run_window_function_ranking():
    with SQL_ENGINE.connect() as conn:
        # Dropping if it exists to avoid a 'Duplicate key' error
        try:
            conn.execute(text("DROP INDEX idx_duration_sort ON meeting_metrics"))
            conn.commit()
        except Exception:
            pass 
            
        print("Creating index on video_duration_sec for ranking optimization...")
        conn.execute(text("CREATE INDEX idx_duration_sort ON meeting_metrics(video_duration_sec DESC)"))
        conn.commit()
            
    # Executing and timing the query
    start_time = time.perf_counter()
    
    # Executing the Window Function for Ranking
    query = """
    SELECT 
        pk_id,
        video_duration_sec,
        item_count,
        RANK() OVER (ORDER BY video_duration_sec DESC) AS duration_rank
    FROM meeting_metrics;
    """
    
    with SQL_ENGINE.connect() as conn:
        df = pd.read_sql(text(query), conn)
        
    end_time = time.perf_counter()
    return df, end_time - start_time

# Execute, unpack, and display the results
df_ranked, time_ranked = run_window_function_ranking()
print(f"Window Function Runtime: {time_ranked:.4f} seconds")
display(df_ranked.head())

# %%
def run_analytical_top_meetings():
    # Recreating the test environment: Indexing for Sort/Limit Performance
    with SQL_ENGINE.connect() as conn:
        # Dropping if it exists to avoid a 'Duplicate key' error
        try:
            conn.execute(text("DROP INDEX idx_item_count_sort ON meeting_metrics"))
            conn.commit()
        except Exception:
            pass 
            
        print("Creating index on item_count for analytical optimization...")
        conn.execute(text("CREATE INDEX idx_item_count_sort ON meeting_metrics(item_count DESC)"))
        conn.commit()
            
    # Executing and timing the query
    start_time = time.perf_counter()
    
    # Executing the Analytical Join Query
    query = """
    SELECT 
        c.city,
        m.meeting_id,
        mm.video_duration_sec,
        mm.item_count
    FROM cities c
    JOIN meetings m ON c.city_id = m.city_id
    JOIN meeting_metrics mm ON m.pk_id = mm.pk_id
    ORDER BY mm.item_count DESC
    LIMIT 10;
    """
    
    with SQL_ENGINE.connect() as conn:
        df = pd.read_sql(text(query), conn)
        
    end_time = time.perf_counter()
    return df, end_time - start_time

# Execute, unpack, and display the results
df_analytics, time_analytics = run_analytical_top_meetings()
print(f"Analytical Query Runtime: {time_analytics:.4f} seconds")
display(df_analytics)

# %% [markdown]
# # <center> ----------------------Thank you :) ----------------------


