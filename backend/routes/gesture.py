from fastapi import APIRouter
from datetime import datetime
# from database import gestures_col
# from models import GestureEvent

from backend.database import gestures_col
from backend.models import GestureEvent


router = APIRouter()

@router.post("/api/gesture")
def store_gesture(data: GestureEvent):
    doc = {
        "controllerId": data.controllerId,
        "gesture": data.gesture,
        "confidence": data.confidence,
        "timestamp": data.timestamp,
        "source": "vision",
        "createdAt": datetime.utcnow()
    }

    gestures_col.insert_one(doc)

    return {
        "status": "ok",
        "message": "Gesture stored"
    }
