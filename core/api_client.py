import requests

BACKEND_URL = "http://localhost:8000"

def post_audio(payload):
    try:
        requests.post(
            f"{BACKEND_URL}/api/audio",
            json=payload,
            timeout=2
        )
    except Exception as e:
        print("Audio API error:", e)


def post_gesture(payload):
    try:
        requests.post(
            f"{BACKEND_URL}/api/gesture",
            json=payload,
            timeout=2
        )
    except Exception as e:
        print("Gesture API error:", e)
