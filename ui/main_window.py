import os
import sys
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
        self.vibration_motor = None
        self.buzzer = None
        if Buzzer is not None:
            try:
                # Vibration motor driver on GPIO26 -> GND
                self.vibration_motor = Buzzer(26)
            except Exception:
                self.vibration_motor = None
            try:
                # Buzzer on GPIO12 -> GND
                self.buzzer = Buzzer(12)
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

        # Vibration pulse on app launch
        QTimer.singleShot(150, self._vibrate_once)

        # Heartbeat timer to keep backend status fresh
        self._heartbeat_timer = QTimer(self)
        self._heartbeat_timer.setInterval(20 * 1000)
        self._heartbeat_timer.timeout.connect(self._send_heartbeat)
        self._heartbeat_timer.start()
        QTimer.singleShot(500, self._send_heartbeat)

    # -------------------------------
    def show_home(self, feedback=True):
        if self._navigation_busy:
            return
        self._navigation_busy = True
        QTimer.singleShot(250, self._unlock_navigation)
        if feedback:
            self._vibrate_once()
        self.stack.setCurrentWidget(self.home)

    def show_gesture(self, feedback=True):
        if self._navigation_busy:
            return
        self._navigation_busy = True
        QTimer.singleShot(250, self._unlock_navigation)
        if feedback:
            self._vibrate_once()
        try:
            self.stack.setCurrentWidget(self.gesture)
            self.gesture.start_worker()
        except Exception as exc:
            print(f"[MainWindow] show_gesture failed: {exc}")
            self.stack.setCurrentWidget(self.home)

    def show_audio(self, feedback=True):
        if self._navigation_busy:
            return
        self._navigation_busy = True
        QTimer.singleShot(250, self._unlock_navigation)
        if feedback:
            self._vibrate_once()
        try:
            self.stack.setCurrentWidget(self.audio)
            self.audio.restart_audio()
        except Exception as exc:
            print(f"[MainWindow] show_audio failed: {exc}")
            self.stack.setCurrentWidget(self.home)

    def show_emergency(self):
        self.stack.setCurrentWidget(self.emergency)

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
    def _cleanup_for_exit(self):
        if self.gesture:
            self.gesture.stop_worker()
        if self.audio:
            self.audio.cleanup()
        if self.gpio_button:
            self.gpio_button.close()
        if self.buzzer:
            self.buzzer.off()
            self.buzzer.close()
        if self.vibration_motor:
            self.vibration_motor.off()
            self.vibration_motor.close()

    def shutdown(self):
        self._is_shutting_down = True
        try:
            self._cleanup_for_exit()
        finally:
            app = QApplication.instance()
            if app:
                app.quit()

    def restart_program(self):
        self._is_shutting_down = True
        try:
            self._cleanup_for_exit()
        finally:
            os.execv(sys.executable, [sys.executable] + sys.argv)
    
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
    def _vibrate_once(self, duration_ms=200):
        if not self.vibration_motor:
            return
        self.vibration_motor.on()
        QTimer.singleShot(duration_ms, self.vibration_motor.off)

    def feedback_detection(self, duration_ms=200):
        self._vibrate_once(duration_ms)
        if not self.buzzer:
            return
        self.buzzer.on()
        QTimer.singleShot(duration_ms, self.buzzer.off)

    def _send_heartbeat(self):
        post_heartbeat(self.controller_id)
