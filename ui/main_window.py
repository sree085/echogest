from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QApplication
from gpiozero import Button
from ui.screens.home import HomeScreen
from ui.screens.audio import AudioScreen
from ui.screens.gesture import GestureScreen
from ui.screens.emergency import EmergencyScreen
from core.api_client import post_heartbeat
from core.config import CONTROLLER_ID
try:
    from gpiozero import Buzzer
except Exception:
    Buzzer = None


class MainWindow(QMainWindow):
    gpio_cycle_requested = pyqtSignal()
    gpio_home_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("EchoGest")
        self.setFixedSize(480, 320)
        self.controller_id = CONTROLLER_ID
        self._is_shutting_down = False
        self._navigation_busy = False
        self.buzzer = None
        if Buzzer is not None:
            try:
                # Active buzzer on GPIO26 -> GND
                self.buzzer = Buzzer(26)
            except Exception:
                self.buzzer = None

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = HomeScreen(self)
        self.audio = AudioScreen(self)
        self.gesture = GestureScreen(self)
        self.emergency = EmergencyScreen(self)

        for s in (self.home, self.audio, self.gesture, self.emergency):
            self.stack.addWidget(s)

        self.stack.setCurrentWidget(self.home)

        # GPIO button: cycle screens (GPIO16 -> GND)
        self.gpio_button = Button(16, pull_up=True, bounce_time=0.1, hold_time=1.0)
        self.gpio_button.when_pressed = self.gpio_cycle_requested.emit
        self.gpio_button.when_held = self.gpio_home_requested.emit
        self.gpio_cycle_requested.connect(self.cycle_screen)
        self.gpio_home_requested.connect(self.show_home)

        # Beep once on initial launch after UI is ready
        QTimer.singleShot(150, self._beep_once)

        # Heartbeat timer to keep backend status fresh
        self._heartbeat_timer = QTimer(self)
        self._heartbeat_timer.setInterval(20 * 1000)
        self._heartbeat_timer.timeout.connect(self._send_heartbeat)
        self._heartbeat_timer.start()
        QTimer.singleShot(500, self._send_heartbeat)

    # -------------------------------
    def show_home(self):
        if self._navigation_busy:
            return
        self._navigation_busy = True
        QTimer.singleShot(250, self._unlock_navigation)
        self._stop_emergency_beep()
        self._beep_once()
        self.stack.setCurrentWidget(self.home)

    def show_gesture(self):
        if self._navigation_busy:
            return
        self._navigation_busy = True
        QTimer.singleShot(250, self._unlock_navigation)
        self._stop_emergency_beep()
        self._beep_once()
        try:
            self.stack.setCurrentWidget(self.gesture)
            self.gesture.start_worker()
        except Exception as exc:
            print(f"[MainWindow] show_gesture failed: {exc}")
            self.stack.setCurrentWidget(self.home)

    def show_audio(self):
        if self._navigation_busy:
            return
        self._navigation_busy = True
        QTimer.singleShot(250, self._unlock_navigation)
        self._stop_emergency_beep()
        self._beep_once()
        try:
            self.stack.setCurrentWidget(self.audio)
            self.audio.restart_audio()
        except Exception as exc:
            print(f"[MainWindow] show_audio failed: {exc}")
            self.stack.setCurrentWidget(self.home)

    def show_emergency(self):
        self._beep_once()
        self.stack.setCurrentWidget(self.emergency)
        self._start_emergency_beep()

    def cycle_screen(self):
        current = self.stack.currentWidget()
        if current is self.home:
            self.show_gesture()
        elif current is self.gesture:
            self.show_audio()
        else:
            self.show_home()

    # -------------------------------
    # 🔴 HARD EXIT BUTTON HANDLER
    # -------------------------------
    def shutdown(self):
        self._is_shutting_down = True
        try:
            if self.gesture:
                self.gesture.stop_worker()
            if self.audio:
                self.audio.cleanup()
                if getattr(self.audio, "buzzer", None):
                    self.audio.buzzer.close()
            if self.gpio_button:
                self.gpio_button.close()
            if self.buzzer:
                self.buzzer.off()
                self.buzzer.close()
        finally:
            app = QApplication.instance()
            if app:
                app.quit()
    
    def closeEvent(self, event):
        # Ignore accidental window close while running fullscreen kiosk UI.
        if self._is_shutting_down:
            event.accept()
            return
        event.ignore()
        self.showFullScreen()
    
    def _unlock_navigation(self):
        self._navigation_busy = False

    # -------------------------------
    def _beep_once(self, duration_ms=200):
        if not self.buzzer:
            return
        self.buzzer.on()
        QTimer.singleShot(duration_ms, self.buzzer.off)

    def _start_emergency_beep(self):
        if self.buzzer:
            self.buzzer.on()

    def _stop_emergency_beep(self):
        if self.buzzer:
            self.buzzer.off()

    def _send_heartbeat(self):
        post_heartbeat(self.controller_id)
