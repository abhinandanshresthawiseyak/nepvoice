from sqlalchemy.orm import Session
from app.database.database import SessionLocal, init_db
from app.models.models import Feature

def seed_features():
    init_db()  # Ensure tables exist

    db: Session = SessionLocal()
    try:
        features_data = [
            {"name": "speech_to_text", "description": "Convert audio to text", "is_free": False, "credit_cost": 4},
            {"name": "text_to_speech", "description": "Convert text to audio", "is_free": False, "credit_cost": 3},
            {"name": "summarize", "description": "Summarize large texts", "is_free": False, "credit_cost": 2},
            {"name": "diarization", "description": "Separate speakers in audio", "is_free": False, "credit_cost": 5},
            {"name": "call_bot", "description": "Voice call automation", "is_free": False, "credit_cost": 7},
            {"name": "chatbot", "description": "Chat assistant interaction", "is_free": False, "credit_cost": 10},
        ]

        for feature in features_data:
            existing = db.query(Feature).filter(Feature.name == feature["name"]).first()
            if not existing:
                new_feature = Feature(**feature)
                db.add(new_feature)

        db.commit()
        print("✅ Features table seeded successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_features()
