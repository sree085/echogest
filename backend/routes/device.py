from fastapi import APIRouter
from datetime import datetime
# from database import devices_col
# from models import DeviceUpdate

from backend.database import devices_col
from backend.models import DeviceUpdate


router = APIRouter()

@router.put("/api/device")
def update_device(data: DeviceUpdate):
    devices_col.update_one(
        {
            "controllerId": data.controllerId,
            "deviceId": data.deviceId
        },
        {
            "$set": {
                "status": data.status,
                "updatedAt": datetime.utcnow()
            }
        },
        upsert=True
    )

    return {
        "status": "ok",
        "message": "Device updated"
    }
