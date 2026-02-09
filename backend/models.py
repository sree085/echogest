from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GestureEvent(BaseModel):
    controllerId: str
    gesture: str
    confidence: float
    timestamp: Optional[datetime] = None
    source: Optional[str] = None
    action: Optional[str] = None


class AudioEvent(BaseModel):
    controllerId: str
    sound: str
    confidence: float
    timestamp: Optional[datetime] = None


class DeviceUpdate(BaseModel):
    controllerId: str
    deviceId: str
    status: bool
