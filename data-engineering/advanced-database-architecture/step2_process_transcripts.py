# Step 2: Process transcripts

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
OUTPUT_PARQUET_PATH = OUTPUT_DIR / "meeting_transcripts.parquet"

# Filter criteria
TARGET_CITIES = {"LongBeachCC", "SeattleCityCouncil"}

def build_transcript_features() -> List[Dict[str, Any]]:
    """
    Parses MeetingBank JSON to extract full text and speaker counts.
    Returns a list of dictionaries ready for DataFrame conversion.
    """
    
    if not MEETINGBANK_JSON_PATH.exists():
        raise FileNotFoundError(f"Source file not found at: {MEETINGBANK_JSON_PATH}")

    with open(MEETINGBANK_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    processed_meetings = []

    print(f"Processing {len(data)} meetings...")

    for meeting_id, meeting_data in data.items():
        
        # Split 'LongBeachCC_08092022' into ['LongBeachCC', '08092022']
        id_parts = meeting_id.split("_")
        
        # Safety check to ensure format is correct
        if len(id_parts) < 2:
            continue

        city = id_parts[0]
        numeric_id = id_parts[1] # Extracts '08092022'

        if city not in TARGET_CITIES:
            continue

        item_info = meeting_data.get("itemInfo", {})

        full_text_list = []
        speakers = set()

        # Deep extraction loop
        for item in item_info.values():
            transcripts = item.get("transcripts", [])
            
            # Logic to process segments
            for segment in transcripts:
                text = segment.get("text", "").strip()
                speaker = segment.get("speaker")
                
                if text:
                    full_text_list.append(text)
                
                # explicit None check because empty string "" is a valid speaker name in some messy data
                if speaker is not None:
                    speakers.add(speaker)

        # Join text at the end
        full_transcript_text = " ".join(full_text_list)
        
        processed_meetings.append({
            "meeting_id": str(numeric_id), # Saving only the numerical part as string
            "city": city,
            "transcript_word_count": len(full_transcript_text.split()),
            "speaker_count": len(speakers),
            "full_transcript_text": full_transcript_text
        })

    return processed_meetings


if __name__ == "__main__":
    try:
        meetings = build_transcript_features()
        
        if not meetings:
            print("No meetings matched the filter criteria.")
        else:
            # Create DataFrame
            df = pd.DataFrame(meetings)
            
            # Enforce string type on meeting_id to prevent it from becoming an Integer
            # This preserves leading zeros (e.g., "08092022" stays "08092022")
            df['meeting_id'] = df['meeting_id'].astype(str)

            # Adding the Primary Key
            df['pk_id'] = range(1, len(df) + 1)

            # Moving 'pk_id' to the first column position
            cols = ['pk_id'] + [col for col in df.columns if col != 'pk_id']
            df = df[cols]
            
            # to parquet step
            df.to_parquet(OUTPUT_PARQUET_PATH, engine='pyarrow', index=False)

            print(f"\nSUCCESS: Processed {len(df)} meetings.")
            print(f"Data saved to: {OUTPUT_PARQUET_PATH}")
            
            print("\nPreview:")
            print(df[["pk_id", "meeting_id", "transcript_word_count", "speaker_count"]].head(10))

    except Exception as e:
        print(f"An error occurred: {e}")
