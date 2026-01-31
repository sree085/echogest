from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QTimer, QDateTime

class HomeScreen(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main

        layout = QVBoxLayout(self)

        status = QLabel("●  AI Active")
        status.setStyleSheet("color:#4f8df7; font-size:16px;")
        layout.addWidget(status, alignment=Qt.AlignLeft)

        self.time = QLabel()
        self.time.setStyleSheet("font-size:64px; font-weight:600;")
        self.time.setAlignment(Qt.AlignCenter)

        self.date = QLabel()
        self.date.setStyleSheet("font-size:18px; color:gray;")
        self.date.setAlignment(Qt.AlignCenter)

        info = QLabel("System Active — Monitoring gestures and sounds...")
        info.setStyleSheet("font-size:16px; color:#666;")
        info.setAlignment(Qt.AlignCenter)

        btn_audio = QPushButton("AI Assistant Mode")
        btn_gesture = QPushButton("Gesture Recording Mode")

        for b in (btn_audio, btn_gesture):
            b.setFixedHeight(50)
            b.setStyleSheet("font-size:18px;")

        btn_audio.clicked.connect(main.show_audio)
        btn_gesture.clicked.connect(main.show_gesture)

        layout.addStretch()
        layout.addWidget(self.time)
        layout.addWidget(self.date)
        layout.addSpacing(20)
        layout.addWidget(info)
        layout.addSpacing(30)
        layout.addWidget(btn_audio)
        layout.addWidget(btn_gesture)
        layout.addStretch()

        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

    def update_time(self):
        now = QDateTime.currentDateTime()
        self.time.setText(now.toString("HH:mm:ss"))
        self.date.setText(now.toString("dddd, MMMM d, yyyy"))
