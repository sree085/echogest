import requests

BACKEND_URL = "https://echogestapp.onrender.com"

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
            f"{BACKEND_URL}/api/gestures",
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
            f"{BACKEND_URL}/api/controllers/heartbeat",
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
