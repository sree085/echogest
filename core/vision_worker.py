import cv2
import mediapipe as mp
import time
import math
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from core.api_client import post_gesture
from core.config import CONTROLLER_ID


class VisionWorker(QThread):
    frame_signal = pyqtSignal(QImage)
    gesture_signal = pyqtSignal(str, int)
    countdown_signal = pyqtSignal(int)

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 20)

        mp_hands = mp.solutions.hands
        mp_draw = mp.solutions.drawing_utils

        hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6
        )

        delay_s = 5.0
        last_gesture = ""
        stable_frames = 0
        last_time = 0
        detection_start_time = None
        emitted_once = False

        while True:
            if self.isInterruptionRequested():
                break
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)

            # ⏱ Frame skipping → CPU reduction
            if time.time() - last_time < 0.05:
                continue
            last_time = time.time()

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            gesture = "Unknown"
            confidence = 0

            should_exit = False

            if results.multi_hand_landmarks and not emitted_once:
                if detection_start_time is None:
                    detection_start_time = time.monotonic()
                    self.countdown_signal.emit(int(delay_s))

                elapsed = time.monotonic() - detection_start_time
                if elapsed >= delay_s:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_draw.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS
                        )
                        gesture = self.detect_gesture(hand_landmarks.landmark)
                        confidence = 85
                        break

                    # Gesture stability filter
                    if gesture == last_gesture:
                        stable_frames += 1
                    else:
                        stable_frames = 0
                        last_gesture = gesture

                    if stable_frames >= 3:
                        self.gesture_signal.emit(gesture, confidence)
                        emitted_once = True
                        self.countdown_signal.emit(0)
                        should_exit = True

                        # 🔗 Send to backend
                        if gesture != "Unknown":
                            post_gesture({
                                "controllerId": CONTROLLER_ID,
                                "gesture": gesture,
                                "confidence": confidence / 100,
                                "source": "vision"
                            })
                else:
                    remaining = int(max(0, math.ceil(delay_s - elapsed)))
                    self.countdown_signal.emit(remaining)
                    last_gesture = ""
                    stable_frames = 0
            elif not results.multi_hand_landmarks:
                detection_start_time = None
                last_gesture = ""
                stable_frames = 0
                self.countdown_signal.emit(0)

            if should_exit:
                break

            # Convert frame for Qt
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.frame_signal.emit(qt_img)

        cap.release()

    def detect_gesture(self, landmarks):
        tips = [8, 12, 16, 20]
        folded = [(landmarks[t].y < landmarks[t - 2].y) for t in tips]
        thumb_open = landmarks[4].x > landmarks[3].x

        if all(folded):
            return "OPEN PALM"
        elif not any(folded) and not thumb_open:
            return "POWER OFF"
        elif not any(folded) and thumb_open:
            return "Thumbs Up"
        elif folded == [True, False, False, False]:
            return "INDEX"
        elif folded == [True, True, False, False]:
            return "Victory"
        else:
            return "Unknown"
