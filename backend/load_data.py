import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# --- Database Connection ---
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")

client = MongoClient(MONGO_URI)
db = client.gita_chatbot_db
collection = db.shlokas


# --- Function to load data from CSV to MongoDB ---
def load_data_from_csv(filepath):
    # Check if the collection is already populated
    if collection.count_documents({}) > 0:
        print("Data already exists in the database. Skipping data load.")
        return

    print("Database is empty. Loading data from CSV...")
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(filepath)

        # We will process the data to create a list of dictionaries
        shlokas_to_insert = []
        for index, row in df.iterrows():
            # Create a dictionary for each shloka
            shloka_doc = {
                "chapter": int(row['Chapter']),
                "verse": int(row['Verse']),
                "sanskrit": row['Shloka'].strip(),
                "english": row['EngMeaning'].strip(),
                "hindi": row['HinMeaning'].strip(),
                # We will add emotions later in Phase 2
                "emotion": "neutral"
            }
            shlokas_to_insert.append(shloka_doc)

        # Insert the data into the MongoDB collection
        if shlokas_to_insert:
            collection.insert_many(shlokas_to_insert)
            print(f"Successfully loaded {len(shlokas_to_insert)} shlokas into the database.")
        else:
            print("No data found to load.")

    except FileNotFoundError:
        print(f"Error: The file {filepath} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# --- Run the data loader ---
if __name__ == "__main__":
    # The path to your CSV file
    csv_filepath = 'Bhagwad_Gita.csv'
    load_data_from_csv(csv_filepath)
    client.close()
