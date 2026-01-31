from fastapi import APIRouter
from datetime import datetime
# from database import audio_col
# from models import AudioEvent

from backend.database import audio_col
from backend.models import AudioEvent


router = APIRouter()

@router.post("/api/audio")
def store_audio(data: AudioEvent):
    severity = "HIGH" if data.confidence > 0.85 else "MEDIUM"

    doc = {
        "controllerId": data.controllerId,
        "sound": data.sound,
        "confidence": data.confidence,
        "severity": severity,
        "timestamp": datetime.utcnow(),
        "actionTaken": "EMERGENCY_ALERT" if data.sound.lower().find("cry") != -1 else "NONE",
        "createdAt": datetime.utcnow()
    }

    audio_col.insert_one(doc)

    return {
        "status": "ok",
        "message": "Audio event stored"
    }
