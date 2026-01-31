from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from ui.screens.home import HomeScreen
from ui.screens.audio import AudioScreen
from ui.screens.gesture import GestureScreen
from ui.screens.emergency import EmergencyScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EchoGest")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = HomeScreen(self)
        self.audio = AudioScreen(self)
        self.gesture = GestureScreen(self)
        self.emergency = EmergencyScreen(self)

        for s in (self.home, self.audio, self.gesture, self.emergency):
            self.stack.addWidget(s)

        self.stack.setCurrentWidget(self.home)

    def show_home(self): self.stack.setCurrentWidget(self.home)
    # def show_audio(self): self.stack.setCurrentWidget(self.audio)
    def show_gesture(self): self.stack.setCurrentWidget(self.gesture)
    def show_emergency(self): self.stack.setCurrentWidget(self.emergency)
    def show_audio(self):
        self.stack.setCurrentWidget(self.audio)
        self.audio.restart_audio()
