import os
from pymongo import MongoClient
from dotenv import load_dotenv
from transformers import pipeline
import time

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.gita_chatbot_db
collection = db.shlokas

print("Loading zero-shot classification model...")

classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")



CANDIDATE_LABELS = [
    "inspiration", "devotion", "encouragement", "motivation", "peace",
    "self-belief", "upliftment", "confidence", "spiritual_detachment",
    "equanimity", "introspection", "self_inquiry", "awareness",
    "spiritual_clarity", "self_control", "tolerance", "discernment",
    "self_purification", "acceptance", "compassion", "non_attachment",
    "self_reflection", "surrender", "humility", "trust", "reflection"
]


def tag_all_shlokas():
    """
    Iterates through all shlokas in the database and updates them
    with a predicted spiritual theme using a zero-shot model.
    """
    print("Starting to tag shlokas in the database...")
    
    shlokas_to_tag = list(collection.find({"emotion": "neutral"}))
    total_shlokas = len(shlokas_to_tag)
    print(f"Found {total_shlokas} shlokas to tag.")

    for i, shloka in enumerate(shlokas_to_tag):
        
        text_to_classify = shloka.get("english", "")
        if not text_to_classify:
            continue

        try:
            
            result = classifier(text_to_classify, CANDIDATE_LABELS, multi_label=False)
            top_label = result['labels'][0]
            top_score = result['scores'][0]

            
            collection.update_one(
                {"_id": shloka["_id"]},
                {"$set": {"emotion": top_label}}  # We are overwriting the 'emotion' field
            )

            print(
                f"({i + 1}/{total_shlokas}) Shloka {shloka['chapter']}.{shloka['verse']} tagged as '{top_label}' (Score: {top_score:.2f})")

        except Exception as e:
            print(f"Could not process shloka {shloka['chapter']}.{shloka['verse']}: {e}")

        
        time.sleep(1)

    print("Finished tagging all shlokas.")


# --- Run the Tagger ---
if __name__ == "__main__":
    tag_all_shlokas()
    client.close()
