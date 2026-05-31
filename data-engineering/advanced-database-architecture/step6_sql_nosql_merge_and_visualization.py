# %% [markdown]
# # <center> Step 6: Merge SQL & NoSQL data and Visualization

# %%
import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
import requests
import os
import time
from pathlib import Path
from IPython.display import display
from dotenv import load_dotenv

from sqlalchemy import create_engine, inspect, text

from pymongo import MongoClient
import certifi

import warnings
warnings.filterwarnings("ignore")

# %% [markdown]
# ## Importing the dataset

# %%
# Loading variables from env file
load_dotenv()

# SQL Database connection
SQL_URL = os.getenv("SQL_URL")

SQL_ENGINE = create_engine(
    SQL_URL,
    connect_args={"ssl": {"fake_flag_to_enable_tls": True}},
    pool_pre_ping=True
)

# NOSQL MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

MONGO_CLIENT = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
MONGO_DB = MONGO_CLIENT[MONGO_DB_NAME]
MONGO_COLLECTION = MONGO_DB[MONGO_COLLECTION_NAME]

# %%
with SQL_ENGINE.connect() as conn:
    # Use .connection to access the raw driver (PyMySQL)
    df_sql = pd.read_sql("SELECT * FROM denormalized_table", conn.connection)

# 3. Verify the import
print(f"Table imported! Rows: {len(df_sql)}, Columns: {len(df_sql.columns)}")
df_sql.head()

# %%
# Drop unnecessary columns
df_sql.drop(columns=["metric_id","city_id"],inplace=True)

# %%
# Move only some columns to the front while keeping everything else the same


cols_to_front = ['pk_id', 'meeting_id']

# Create a list of all other columns that are NOT in cols_to_front
remaining_cols = [c for c in df_sql.columns if c not in cols_to_front]

# Combine the lists to create the final order
df_sql = df_sql[cols_to_front + remaining_cols]

df_sql.head()

# %%
# Fetch all documents from the collection
cursor = MONGO_COLLECTION.find()

# Convert the cursor to a DataFrame
df_transcript_data = pd.DataFrame(list(cursor))

# View the first few rows
df_transcript_data.head()

# %%
# Dropping redundant columns
df_transcript_data.drop(columns=["_id","meeting_id","city",], inplace=True)

# %%
df_transcript_data.head()

# %%
data_complete = pd.merge(
    df_sql,
    df_transcript_data,
    how="left",
    on="pk_id"
)

print("This is the complete data, from both SQL and MongoDB")
display(data_complete.head())

# %%
# Setup paths
BASE_DIR = Path.cwd() 
DATA_DIR = BASE_DIR / "Data"
OUTPUT_DIR = BASE_DIR / "Processed_Data"

# Ensure directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PARQUET_PATH = OUTPUT_DIR / "completedata.parquet"

# Write the actual file
data_complete.to_parquet(OUTPUT_PARQUET_PATH, index=False)

print(f"File successfully created at: {OUTPUT_PARQUET_PATH}")

# %%
# Set the style
sns.set_theme(style="whitegrid")
plt.figure(figsize=(16, 12))

# Subplot 1: Distribution of Meeting Durations
plt.subplot(2, 2, 1)
sns.histplot(data_complete['video_duration_sec'], kde=True, color='#2ecc71')
plt.title('Distribution of Video Duration (sec)')

# Subplot 2: Word Count vs. Duration (Density Check)
plt.subplot(2, 2, 2)
sns.scatterplot(data_complete, x='video_duration_sec', y='transcript_word_count', 
                hue='speaker_count', palette='viridis', alpha=0.6)
plt.title('Transcript Density: Word Count vs. Duration')

# Subplot 3: City meeting count distribution
plt.subplot(2, 2, 3)
city_counts = data_complete['city'].value_counts().head(10)
sns.barplot(x=city_counts.values, y=city_counts.index, palette='magma')
plt.title('City meeting count distribution')

# Subplot 4: Correlation Heatmap (Metrics only)
plt.subplot(2, 2, 4)

sns.regplot(data_complete, 
            x='video_duration_sec', 
            y='transcript_word_count', 
            scatter_kws={'alpha':0.3}, 
            line_kws={'color':'red'})

plt.title('Predictive Power: Duration vs. Word Count')

plt.tight_layout()
plt.show()

# %% [markdown]
# # <center> ----------------------Thank you :) ----------------------


