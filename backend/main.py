import os
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
from transformers import pipeline


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


MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.gita_chatbot_db
collection = db.shlokas

print("Loading emotion detection model...")
emotion_classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english", top_k=1)




class UserInput(BaseModel):
    text: str
    language: str = 'english'


class ShlokaResponse(BaseModel):
    chapter: int
    verse: int
    sanskrit: str
    translation: str
    spiritual_theme: str  



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


EXTENDED_EMOTION_MAP = {
    # Positive & Uplifting
    "joy": "inspiration", "love": "devotion",
    # Core Gita Themes
    "detachment": "spiritual_detachment", "curiosity": "self_inquiry",
    # Negative Emotions & Spiritual Reframing
    "anger": "self_control", "sadness": "acceptance", "fear": "surrender"
}



@app.get("/")
def read_root():
    return {"message": "Welcome to the Emotion-Aware Bhagavad Gita Chatbot API"}


@app.post("/suggest", response_model=ShlokaResponse)
def get_suggestion(user_input: UserInput):
    """
    Analyzes user text to find a spiritual theme and suggests a relevant shloka.
    """
    
    try:
        results = emotion_classifier(user_input.text)
        raw_emotion = results[0][0]['label']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in emotion analysis: {e}")

    
    basic_emotion = EMOTION_MAP.get(raw_emotion, "detachment")
    spiritual_theme = EXTENDED_EMOTION_MAP.get(basic_emotion, "reflection")  # 'reflection' as a fallback

   
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
