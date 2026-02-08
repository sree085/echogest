from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from core.vision_worker import VisionWorker


class GestureScreen(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.worker = None
        self.gesture_handled = False

        # 🔒 Lock screen size for PiScreen 3.5"
        self.setFixedSize(480, 320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        title = QLabel("Gesture Mode")
        title.setStyleSheet("font-size:18px; font-weight:600;")
        layout.addWidget(title, alignment=Qt.AlignLeft)

        self.camera_box = QLabel()
        self.camera_box.setFixedSize(280, 180)
        self.camera_box.setAlignment(Qt.AlignCenter)
        self.camera_box.setStyleSheet("""
            border:2px solid #5fa3ff;
            border-radius:12px;
            background:#000;
        """)

        self.gesture_label = QLabel("Gesture: ---")
        self.gesture_label.setAlignment(Qt.AlignCenter)
        self.gesture_label.setStyleSheet(
            "font-size:16px; color:#2563eb;"
        )

        self.progress = QProgressBar()
        self.progress.setFixedHeight(14)
        self.progress.setRange(0, 5)
        self.progress.setValue(0)

        self.countdown_label = QLabel("Countdown: --")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("font-size:14px; color:#444;")

        footer = QLabel("Camera active • Hand motion trigger")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size:12px; color:#666;")

        home = QPushButton("Home")
        home.setFixedHeight(40)
        home.clicked.connect(self.go_home)

        layout.addWidget(self.camera_box)
        layout.addSpacing(6)
        layout.addWidget(self.gesture_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.countdown_label)
        layout.addWidget(footer)
        layout.addStretch()
        layout.addWidget(home)

    # --------------------------------------------------
    # 🔁 CALLED EVERY TIME SCREEN IS SHOWN
    # --------------------------------------------------
    def start_worker(self):
        self.stop_worker()
        self.gesture_handled = False
        self.update_countdown(0)

        self.worker = VisionWorker()
        self.worker.frame_signal.connect(self.update_frame)
        self.worker.gesture_signal.connect(self.update_gesture)
        self.worker.countdown_signal.connect(self.update_countdown)
        self.worker.start()

    def stop_worker(self):
        if self.worker and self.worker.isRunning():
            self.worker.requestInterruption()
            if not self.worker.wait(1500):
                self.worker.terminate()
                self.worker.wait(500)
        self.worker = None

    # --------------------------------------------------
    def update_frame(self, image):
        pixmap = QPixmap.fromImage(image)
        self.camera_box.setPixmap(
            pixmap.scaled(
                self.camera_box.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def update_gesture(self, gesture, confidence):
        if self.gesture_handled:
            return
        self.gesture_handled = True

        self.gesture_label.setText(f"Gesture: {gesture}")
        self.update_countdown(0)

        self.go_home()

    def update_countdown(self, remaining):
        if remaining <= 0:
            self.countdown_label.setText("Countdown: --")
            self.progress.setValue(0)
            return
        self.countdown_label.setText(f"Countdown: {remaining}s")
        self.progress.setValue(remaining)

    # --------------------------------------------------
    def go_home(self):
        self.stop_worker()
        self.main.show_home()

    def closeEvent(self, event):
        self.stop_worker()
        event.accept()
