from fastapi import APIRouter
from datetime import datetime
import re
# from database import gestures_col
# from models import GestureEvent

from backend.database import gestures_col, gesture_mappings_col
from backend.models import GestureEvent


router = APIRouter()

@router.post("/api/gesture")
def store_gesture(data: GestureEvent):
    now = datetime.utcnow()
    doc = {
        "controllerId": data.controllerId,
        "gesture": data.gesture,
        "confidence": data.confidence,
        "timestamp": data.timestamp,
        "source": "vision",
        "createdAt": now
    }

    gestures_col.insert_one(doc)
    action = data.action or "NONE"
    gesture_mappings_col.update_one(
        {"gesture": data.gesture},
        {
            "$set": {
                "gesture": data.gesture,
                "action": action,
                "updatedAt": now
            },
            "$setOnInsert": {
                "createdAt": now
            }
        },
        upsert=True
    )

    return {
        "status": "ok",
        "message": "Gesture stored"
    }


@router.get("/api/gesturemappings/{gesture}")
def get_gesture_mapping(gesture: str):
    doc = gesture_mappings_col.find_one({"gesture": gesture})
    if not doc:
        doc = gesture_mappings_col.find_one(
            {"gesture": {"$regex": f"^{re.escape(gesture)}$", "$options": "i"}}
        )
    if not doc:
        return {"found": False}
    return {
        "found": True,
        "gesture": doc.get("gesture"),
        "control": doc.get("control"),
        "mqtt": doc.get("mqtt")
    }
