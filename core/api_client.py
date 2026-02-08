import requests

BACKEND_URL = "http://localhost:8000"

def post_audio(payload):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/audio",
            json=payload,
            timeout=2
        )
        if resp.status_code != 200:
            msg = f"Audio API non-200: {resp.status_code} {resp.text}"
            print(msg)
            return False, msg
        return True, ""
    except Exception as e:
        msg = f"Audio API error: {e}"
        print(msg)
        return False, msg


def post_gesture(payload):
    try:
        requests.post(
            f"{BACKEND_URL}/api/gesture",
            json=payload,
            timeout=2
        )
    except Exception as e:
        print("Gesture API error:", e)


def post_heartbeat(controller_id, battery=None):
    if battery is None:
        battery = 100
    try:
        resp = requests.post(
            f"https://echogestapp.onrender.com/api/controllers/heartbeat",
            json={
                "controllerId": controller_id,
                "battery": battery,
            },
            timeout=2,
        )
        if resp.status_code != 200:
            msg = f"Heartbeat API non-200: {resp.status_code} {resp.text}"
            print(msg)
            return False, msg
        return True, ""
    except Exception as e:
        msg = f"Heartbeat API error: {e}"
        print(msg)
        return False, msg


def get_gesture_mapping(gesture):
    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/gesturemappings/{gesture}",
            timeout=2
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data.get("found"):
            return None
        return data
    except Exception as e:
        print("Gesture mapping API error:", e)
        return None
