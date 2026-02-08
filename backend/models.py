from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GestureEvent(BaseModel):
    controllerId: str
    gesture: str
    confidence: float
    timestamp: datetime
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
