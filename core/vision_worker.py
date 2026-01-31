import cv2
import mediapipe as mp
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from core.api_client import post_gesture
from datetime import datetime


class VisionWorker(QThread):
    frame_signal = pyqtSignal(QImage)
    gesture_signal = pyqtSignal(str, int)

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

        last_gesture = ""
        stable_frames = 0
        last_time = 0

        while True:
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

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )
                    gesture = self.detect_gesture(hand_landmarks.landmark)
                    confidence = 85

            # Gesture stability filter
            if gesture == last_gesture:
                stable_frames += 1
            else:
                stable_frames = 0
                last_gesture = gesture

            if stable_frames >= 3:
                # self.gesture_signal.emit(gesture, confidence)
                self.gesture_signal.emit(gesture, confidence)

                # 🔗 Send to backend
                post_gesture({
                    "controllerId": "RP-AX92",
                    "gesture": gesture,
                    "confidence": confidence / 100,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })


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
            return "GESTURE DETECTION STARTED"
        elif not any(folded) and not thumb_open:
            return "POWER OFF"
        elif not any(folded) and thumb_open:
            return "LIGHTS ON"
        elif folded == [True, False, False, False]:
            return "FAN ON"
        elif folded == [True, True, False, False]:
            return "Victory ✌️"
        else:
            return "Unknown"
