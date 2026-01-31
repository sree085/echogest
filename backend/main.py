from fastapi import FastAPI
# from routes import gesture, audio, device
from backend.routes import gesture, audio, device


app = FastAPI(title="EchoGest Backend")

app.include_router(gesture.router)
app.include_router(audio.router)
app.include_router(device.router)

@app.get("/")
def root():
    return {
        "service": "EchoGest Backend",
        "status": "running"
    }
