import json
from pathlib import Path

# Pathlib
ROOT_PATH = Path(__file__).resolve().parent
SOURCE_FILE = ROOT_PATH / "Data" / "MeetingBank.json"

def process_meeting_data(file_path):
    """
    Generator that streams meeting metrics one by one.
    """
    # checking if file exists to avoid crash
    if not file_path.exists():
        raise FileNotFoundError(f"Could not locate data at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as source:
        raw_dataset = json.load(source)

    # Iterate directly over items
    for unique_id, details in raw_dataset.items():
        
        # .get() ensures no crash if key is missing
        agenda_items = details.get("itemInfo", {})
        
        # Sums the length of 'transcripts' list for every entry in agenda_items
        total_speech_blocks = sum(len(entry.get("transcripts", [])) for entry in agenda_items.values())

        # Yield results immediately - helps save memory
        yield {
            "id": unique_id,
            "municipality": unique_id.partition("_")[0],
            "duration": details.get("VideoDuration"),
            "agenda_count": len(agenda_items),
            "speech_segments": total_speech_blocks
        }

if __name__ == "__main__":
    all_records = list(process_meeting_data(SOURCE_FILE))

    print(f"Dataset Size: {len(all_records)}")
    print("\nPreview of extracted data:")
    
    for idx, record in enumerate(all_records[:5], 1):
        print(f"{idx}. {record}")
        