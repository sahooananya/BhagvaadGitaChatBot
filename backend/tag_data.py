import os
from pymongo import MongoClient
from dotenv import load_dotenv
from transformers import pipeline
import time

load_dotenv()

# --- Database Connection ---
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.gita_chatbot_db
collection = db.shlokas

# --- Load Zero-Shot Classification Model ---
print("Loading zero-shot classification model...")
# This model is excellent for classifying text without prior training on specific labels
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
print("Model loaded.")

# --- Define Your Spiritual Themes (from EXTENDED_EMOTION_MAP values) ---
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
    # Find all documents that haven't been tagged yet or are 'neutral'
    shlokas_to_tag = list(collection.find({"emotion": "neutral"}))
    total_shlokas = len(shlokas_to_tag)
    print(f"Found {total_shlokas} shlokas to tag.")

    for i, shloka in enumerate(shlokas_to_tag):
        # The text we will classify is the English meaning of the shloka
        text_to_classify = shloka.get("english", "")
        if not text_to_classify:
            continue

        try:
            # Get the model's prediction
            result = classifier(text_to_classify, CANDIDATE_LABELS, multi_label=False)
            top_label = result['labels'][0]
            top_score = result['scores'][0]

            # Update the document in MongoDB
            collection.update_one(
                {"_id": shloka["_id"]},
                {"$set": {"emotion": top_label}}  # We are overwriting the 'emotion' field
            )

            print(
                f"({i + 1}/{total_shlokas}) Shloka {shloka['chapter']}.{shloka['verse']} tagged as '{top_label}' (Score: {top_score:.2f})")

        except Exception as e:
            print(f"Could not process shloka {shloka['chapter']}.{shloka['verse']}: {e}")

        # To avoid overwhelming any API rate limits (if any) and to be gentle on your machine
        time.sleep(1)

    print("Finished tagging all shlokas.")


# --- Run the Tagger ---
if __name__ == "__main__":
    tag_all_shlokas()
    client.close()
