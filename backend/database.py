from pymongo import MongoClient
import os

MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb+srv://echogest:echogestPI5@cluster0.sjdebtx.mongodb.net/echogest?appName=Cluster0"
    )
    
    # "mongodb+srv://echogest:echogestPI5@cluster0.xxxxx.mongodb.net/echogest?retryWrites=true&w=majority"

client = MongoClient(MONGO_URL)
db = client["echogest"]

gestures_col = db["gestures"]
gesture_mappings_col = db["gesturemappings"]
audio_col = db["audioevents"]
devices_col = db["devices"]
# echogestPI5
