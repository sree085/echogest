from fastapi import APIRouter, HTTPException
from datetime import datetime
# from database import audio_col
# from models import AudioEvent

from backend.database import audio_col
from backend.models import AudioEvent


router = APIRouter()

@router.post("/api/audio")
def store_audio(data: AudioEvent):
    now = datetime.utcnow()
    event_ts = data.timestamp or now

    doc = {
        "controllerId": data.controllerId,
        "sound": data.sound,
        "confidence": data.confidence,
        "timestamp": event_ts,
        "createdAt": now,
        "updatedAt": now,
        "__v": 0
    }

    try:
        audio_col.insert_one(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio insert failed: {e}")

    return {
        "status": "ok",
        "message": "Audio event stored"
    }
