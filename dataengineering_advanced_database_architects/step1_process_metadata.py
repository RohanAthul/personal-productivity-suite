# Step 1: Process metadata

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

# Pathlib configuration
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"
OUTPUT_DIR = BASE_DIR / "Processed_Data"

# Creating output directory if it does not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
MEETINGBANK_JSON_PATH = DATA_DIR / "MeetingBank.json"
OUTPUT_PARQUET_PATH = OUTPUT_DIR / "meeting_summary.parquet"

# Filter criteria
TARGET_CITIES = {"LongBeachCC", "SeattleCityCouncil"}

def read_and_filter_meetingbank() -> List[Dict[str, Any]]:
    """
    Reads MeetingBank JSON and extracts metadata for specific cities.
    """
    if not MEETINGBANK_JSON_PATH.exists():
        print(f"Error: Could not find {MEETINGBANK_JSON_PATH}")
        return []

    with open(MEETINGBANK_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    meetings = []

    for meeting_id, meeting_data in data.items():
        # Identify the city prefix
        city = meeting_id.split("_")[0]

        if city not in TARGET_CITIES:
            continue

        item_info = meeting_data.get("itemInfo", {})
        
        # Calculate total segments across all items in the meeting
        total_segments = sum(
            len(item.get("transcripts", [])) 
            for item in item_info.values()
        )

        meetings.append({
            "meeting_id": meeting_id,
            "city": city,
            "video_duration_sec": meeting_data.get("VideoDuration"),
            "item_count": len(item_info),
            "segment_count": total_segments
        })

    return meetings

# --- Execution ---
if __name__ == "__main__":
    # Load and Filter Data
    meeting_list = read_and_filter_meetingbank()
    print(f"Total meetings filtered: {len(meeting_list)}")

    if meeting_list:
        # Create DataFrame
        df = pd.DataFrame(meeting_list)

        # Trim meeting_id to numeric part only (saved as string)
        df['meeting_id'] = df['meeting_id'].str.split('_').str[1].astype(str)

        # Generate ID Columns
        # -- Primary Key: Sequential 1 to N
        df['pk_id'] = range(1, len(df) + 1)

        # -- City ID: Unique integer for each unique city (starts at 1)
        df['city_id'] = pd.factorize(df['city'])[0] + 1

        # -- Metric ID: Sequential 1 to N (as requested)
        df['metric_id'] = range(1, len(df) + 1)

        # Reorder Columns (IDs first)
        id_cols = ['pk_id', 'city_id', 'metric_id']
        other_cols = [col for col in df.columns if col not in id_cols]
        df = df[id_cols + other_cols]

        # Save to Parquet
        df.to_parquet(OUTPUT_PARQUET_PATH, engine='pyarrow', index=False)

        # Final Preview
        print("\n--- Processed Data Preview ---")
        print(df.head(10).to_string(index=False))
        print(f"\nFile successfully saved at: {OUTPUT_PARQUET_PATH}")
        
    else:
        print("No data found to process.")
