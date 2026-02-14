from PyQt5.QtWidgets import ( # type: ignore
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt, QTimer # type: ignore
from PyQt5.QtGui import QPainter, QColor, QBrush # type: ignore

import sounddevice as sd
import numpy as np

from core.audio_worker import AudioWorker


# =====================================================
# Real Microphone Waveform Widget
# =====================================================
class Waveform(QWidget):
    def __init__(self):
        super().__init__()
        self.levels = [0.05] * 16
        self.stream = None
        self.setFixedHeight(140)

    def start(self):
        self.stop()
        self.stream = sd.InputStream(
            channels=1,
            samplerate=16000,
            blocksize=512,
            callback=self.audio_callback
        )
        self.stream.start()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.levels = [0.05] * 16
        self.update()

    def audio_callback(self, indata, frames, time, status):
        if status:
            return

        rms = np.sqrt(np.mean(indata**2))
        level = min(rms * 25, 1.0)

        self.levels.pop(0)
        self.levels.append(level)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        bar_w = w // (len(self.levels) * 2)
        center = h // 2

        painter.setBrush(QBrush(QColor("#7bb3ff")))
        painter.setPen(Qt.NoPen)

        x = bar_w
        for lvl in self.levels:
            bar_h = int(lvl * h * 0.85)
            painter.drawRoundedRect(
                x, center - bar_h // 2,
                bar_w, bar_h,
                6, 6
            )
            x += bar_w * 2


# =====================================================
# Audio Screen
# =====================================================
class AudioScreen(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.worker = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        # Title
        title = QLabel("AI Assistant Mode")
        title.setStyleSheet("font-size:26px; font-weight:500;")
        layout.addWidget(title)

        layout.addStretch()

        # Waveform
        self.waveform = Waveform()
        layout.addWidget(self.waveform, alignment=Qt.AlignCenter)

        # Command text
        self.command = QLabel("Listening...")
        self.command.setAlignment(Qt.AlignCenter)
        self.command.setStyleSheet("font-size:20px;")
        layout.addWidget(self.command)

        layout.addSpacing(30)

        # Status pills
        status_row = QHBoxLayout()
        status_row.setAlignment(Qt.AlignCenter)
        status_row.setSpacing(25)

        status_row.addWidget(self.pill("🎤", "Mic Active", "#dbeafe"))
        status_row.addWidget(self.pill("📷", "Camera ON", "#dcfce7"))
        status_row.addWidget(self.pill("✔", "Connected", "#dcfce7"))

        layout.addLayout(status_row)
        layout.addStretch()

        # Home Button
        home = QPushButton("Home")
        home.setFixedHeight(48)
        home.setStyleSheet("""
            QPushButton {
                background:#e5e7eb;
                border-radius:12px;
                font-size:16px;
            }
            QPushButton:pressed {
                background:#d1d5db;
            }
        """)
        home.clicked.connect(self.go_home)
        layout.addWidget(home)

        footer = QLabel("EchoGest | AI Wearable Assistant")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color:#666;")
        layout.addWidget(footer)

    # -------------------------------------------------
    def pill(self, icon, text, bg):
        lbl = QLabel(f"{icon}  {text}")
        lbl.setStyleSheet(f"""
            background:{bg};
            padding:12px 18px;
            border-radius:25px;
            font-size:14px;
        """)
        return lbl

    # -------------------------------------------------
    def restart_audio(self):
        self.cleanup()

        self.command.setText("Listening...")
        self.waveform.start()

        self.worker = AudioWorker()
        self.worker.status_signal.connect(self.on_status)
        self.worker.result_signal.connect(self.on_result)
        self.worker.error_signal.connect(self.on_error)
        self.worker.start()

    # -------------------------------------------------
    def on_status(self, msg):
        if "Processing" in msg:
            self.waveform.stop()
            self.command.setText("Processing...")

    def on_result(self, label):
        self.waveform.stop()
        self.command.setText(f'Audio Detected: "{label}"')
        if hasattr(self.main, "feedback_detection"):
            self.main.feedback_detection()

    def on_error(self, err):
        self.waveform.stop()
        msg = err or "Audio error"
        self.command.setText(f"Audio error: {msg}")

    # -------------------------------------------------
    def go_home(self):
        self.cleanup()
        self.main.show_home()

    def cleanup(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        self.waveform.stop()
