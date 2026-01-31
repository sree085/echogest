from PyQt5.QtCore import QThread, pyqtSignal
import subprocess
import os

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

            label = result.stdout.strip()
            self.result_signal.emit(label)

        except Exception as e:
            self.error_signal.emit(str(e))
