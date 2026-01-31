from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from core.vision_worker import VisionWorker


class GestureScreen(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main

        layout = QVBoxLayout(self)

        title = QLabel("Gesture Recording Mode")
        title.setStyleSheet("font-size:22px;")
        layout.addWidget(title, alignment=Qt.AlignLeft)

        self.camera_box = QLabel()
        self.camera_box.setFixedHeight(180)
        self.camera_box.setAlignment(Qt.AlignCenter)
        self.camera_box.setStyleSheet("""
            border:3px solid #5fa3ff;
            border-radius:16px;
            background:#000;
        """)

        self.gesture_label = QLabel("Gesture detected: ---")
        self.gesture_label.setAlignment(Qt.AlignCenter)
        self.gesture_label.setStyleSheet("font-size:18px; color:#3b82f6;")

        self.progress = QProgressBar()
        self.progress.setValue(0)

        footer = QLabel("Lighting: OK   |   Camera: Active   |   Trigger: Hand Motion")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size:13px; color:#666;")

        home = QPushButton("Home")
        home.setFixedHeight(45)
        home.clicked.connect(self.go_home)

        layout.addStretch()
        layout.addWidget(self.camera_box)
        layout.addSpacing(15)
        layout.addWidget(self.gesture_label)
        layout.addWidget(self.progress)
        layout.addSpacing(10)
        layout.addWidget(footer)
        layout.addStretch()
        layout.addWidget(home)

        # Start vision worker
        self.worker = VisionWorker()
        self.worker.frame_signal.connect(self.update_frame)
        self.worker.gesture_signal.connect(self.update_gesture)
        self.worker.start()

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
        self.gesture_label.setText(f"Gesture detected: {gesture}")
        self.progress.setValue(confidence)

    def go_home(self):
        self.worker.terminate()
        self.worker.wait()
        self.main.show_home()

    def closeEvent(self, event):
        self.worker.terminate()
        self.worker.wait()
        event.accept()
