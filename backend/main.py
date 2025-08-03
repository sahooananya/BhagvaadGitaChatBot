import os
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
from transformers import pipeline

# --- App Initialization and Middleware ---
app = FastAPI()
load_dotenv()

origins = ["*"]  # In production, restrict this
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Connection ---
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.gita_chatbot_db
collection = db.shlokas

# --- Load NLP Model ---
print("Loading emotion detection model...")
emotion_classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", top_k=1)
print("Model loaded successfully.")


# --- Pydantic Models ---
class UserInput(BaseModel):
    text: str
    language: str = 'english'


class ShlokaResponse(BaseModel):
    chapter: int
    verse: int
    sanskrit: str
    translation: str
    spiritual_theme: str  # Changed from 'emotion' to 'spiritual_theme'


# --- 2-Step Emotion to Spiritual Theme Mapping ---

# STEP 1: Map raw detected emotions to basic categories
EMOTION_MAP = {
    "admiration": "joy", "amusement": "joy", "approval": "joy", "caring": "love",
    "desire": "love", "excitement": "joy", "gratitude": "joy", "joy": "joy",
    "love": "love", "optimism": "joy", "pride": "joy", "relief": "joy",
    "anger": "anger", "annoyance": "anger", "disapproval": "anger", "disgust": "anger",
    "grief": "sadness", "sadness": "sadness", "disappointment": "sadness",
    "embarrassment": "fear", "fear": "fear", "nervousness": "fear", "remorse": "sadness",
    "curiosity": "curiosity", "surprise": "curiosity", "neutral": "detachment",
    "confusion": "detachment"
}

# STEP 2: Map basic categories to deeper spiritual themes
EXTENDED_EMOTION_MAP = {
    # Positive & Uplifting
    "joy": "inspiration", "love": "devotion",
    # Core Gita Themes
    "detachment": "spiritual_detachment", "curiosity": "self_inquiry",
    # Negative Emotions & Spiritual Reframing
    "anger": "self_control", "sadness": "acceptance", "fear": "surrender"
}


# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Emotion-Aware Bhagavad Gita Chatbot API"}


@app.post("/suggest", response_model=ShlokaResponse)
def get_suggestion(user_input: UserInput):
    """
    Analyzes user text to find a spiritual theme and suggests a relevant shloka.
    """
    # 1. Detect raw emotion
    try:
        results = emotion_classifier(user_input.text)
        raw_emotion = results[0][0]['label']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in emotion analysis: {e}")

    # 2. Perform the two-step mapping
    basic_emotion = EMOTION_MAP.get(raw_emotion, "detachment")
    spiritual_theme = EXTENDED_EMOTION_MAP.get(basic_emotion, "reflection")  # 'reflection' as a fallback

    # 3. Query the database for a shloka with the final spiritual theme
    # IMPORTANT: This requires your database to be tagged with these themes!
    query = {"emotion": spiritual_theme}  # Assuming the field in DB is still called 'emotion'

    results = list(collection.find(query, {"_id": 0}))

    if not results:
        # If no shloka for that theme is found, fallback to 'reflection' or 'spiritual_detachment'
        fallback_query = {"emotion": "reflection"}
        results = list(collection.find(fallback_query, {"_id": 0}))
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No shlokas found for the theme '{spiritual_theme}' or the fallback theme. Please tag your data."
            )

    # 4. Select a random shloka and prepare the response
    selected_shloka = random.choice(results)

    translation_key = user_input.language.lower()
    if translation_key not in selected_shloka or not selected_shloka[translation_key]:
        translation_key = 'english'

    return ShlokaResponse(
        chapter=selected_shloka['chapter'],
        verse=selected_shloka['verse'],
        sanskrit=selected_shloka['sanskrit'],
        translation=selected_shloka[translation_key],
        spiritual_theme=spiritual_theme  # Return the theme for context
    )
