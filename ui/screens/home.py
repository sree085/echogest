from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


class HomeScreen(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main

        # 🔒 Fit PiScreen 3.5"
        self.setFixedSize(480, 320)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)

        # ===============================
        # Top bar (status + exit button)
        # ===============================
        top_bar = QHBoxLayout()

        status = QLabel("●  AI Active")
        status.setStyleSheet("color:#4f8df7; font-size:14px;")
        self.backend_status = QLabel("●  Backend")
        self._set_backend_status(False)

        exit_btn = QPushButton("●")
        exit_btn.setFixedSize(22, 22)
        exit_btn.setStyleSheet("""
            QPushButton {
                background:#ef4444;
                color:#ef4444;
                border-radius:11px;
            }
            QPushButton:pressed {
                background:#dc2626;
            }
        """)
        exit_btn.clicked.connect(self.main.shutdown)

        top_bar.addWidget(status)
        top_bar.addSpacing(10)
        top_bar.addWidget(self.backend_status)
        top_bar.addStretch()
        top_bar.addWidget(exit_btn)

        root.addLayout(top_bar)

        # ===============================
        # Time & date
        # ===============================
        self.time = QLabel()
        self.time.setStyleSheet("font-size:56px; font-weight:600;")
        self.time.setAlignment(Qt.AlignCenter)

        self.date = QLabel()
        self.date.setStyleSheet("font-size:16px; color:gray;")
        self.date.setAlignment(Qt.AlignCenter)

        info = QLabel("System Active — Monitoring gestures and sounds…")
        info.setStyleSheet("font-size:14px; color:#666;")
        info.setAlignment(Qt.AlignCenter)

        btn_audio = QPushButton("AI Assistant Mode")
        btn_gesture = QPushButton("Gesture Recording Mode")

        for b in (btn_audio, btn_gesture):
            b.setFixedHeight(46)
            b.setStyleSheet("font-size:16px;")

        btn_audio.clicked.connect(self.main.show_audio)
        btn_gesture.clicked.connect(self.main.show_gesture)

        root.addStretch()
        root.addWidget(self.time)
        root.addWidget(self.date)
        root.addSpacing(12)
        root.addWidget(info)
        root.addSpacing(20)
        root.addWidget(btn_audio)
        root.addWidget(btn_gesture)
        root.addStretch()

        # Clock timer
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

        # Backend status timer
        self.backend_timer = QTimer(self)
        self.backend_timer.timeout.connect(self.check_backend)
        self.backend_timer.start(3000)
        self.check_backend()

    def _set_backend_status(self, ok: bool):
        color = "#22c55e" if ok else "#ef4444"
        text = "●  Backend" if ok else "●  Backend"
        self.backend_status.setText(text)
        self.backend_status.setStyleSheet(f"color:{color}; font-size:14px;")

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time.setText(now.toString("HH:mm"))
        self.date.setText(now.toString("ddd, MMM d"))

    def check_backend(self):
        try:
            with urlopen("http://localhost:8000/", timeout=1) as resp:
                self._set_backend_status(resp.status == 200)
        except (URLError, HTTPError):
            self._set_backend_status(False)
