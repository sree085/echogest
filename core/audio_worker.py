from PyQt5.QtCore import QThread, pyqtSignal # type: ignore
import subprocess
import os
from core.api_client import post_audio
from datetime import datetime


class AudioWorker(QThread):
    status_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def run(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            python_path = os.path.join(base_dir, "venv_audio", "bin", "python")
            script_path = os.path.join(base_dir, "audio", "audio_infer.py")

            # 🔔 Notify recording start
            self.status_signal.emit("🎙 Recording audio...")

            result = subprocess.run(
                [python_path, script_path],
                capture_output=True,
                text=True,
                timeout=60
            )

            # 🔔 Notify processing done
            self.status_signal.emit("🧠 Processing audio...")

            if result.returncode != 0:
                self.error_signal.emit(result.stderr.strip())
                return

            # label = result.stdout.strip()
            # self.result_signal.emit(label)

            label_out = result.stdout.strip()
            label = label_out.splitlines()[-1].strip()  # Get the last line of output
            self.result_signal.emit(label)
            # print(f"[AudioWorker] Detected sound: {label} ")  

            # 🔗 Send to backend
            post_audio({
                "controllerId": "RP-AX92",
                "sound": label,
                "confidence": 0.9
            })


        except Exception as e:
            self.error_signal.emit(str(e))
