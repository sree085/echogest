from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton # type: ignore
from PyQt5.QtCore import Qt # type: ignore

class EmergencyScreen(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main

        self.setStyleSheet("""
            QWidget {
                border:6px solid red;
                background:#fff5f5;
            }
        """)

        layout = QVBoxLayout(self)

        title = QLabel("⚠ Emergency Alert!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:26px; color:red;")

        icon = QLabel("❗")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size:64px; color:red;")

        msg1 = QLabel("Loud distress sound detected")
        msg1.setAlignment(Qt.AlignCenter)
        msg1.setStyleSheet("font-size:20px;")

        msg2 = QLabel("Notifying caregiver...")
        msg2.setAlignment(Qt.AlignCenter)
        msg2.setStyleSheet("font-size:16px; color:#555;")

        alert = QLabel("● Alert Active")
        alert.setAlignment(Qt.AlignCenter)
        alert.setStyleSheet("""
            font-size:16px;
            color:red;
            border:2px solid red;
            border-radius:20px;
            padding:8px;
        """)

        home = QPushButton("Home")
        home.setFixedHeight(45)
        home.clicked.connect(main.show_home)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(icon)
        layout.addWidget(msg1)
        layout.addWidget(msg2)
        layout.addSpacing(15)
        layout.addWidget(alert)
        layout.addStretch()
        layout.addWidget(home)
