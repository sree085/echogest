import cv2
import mediapipe as mp
from PyQt5.QtCore import QThread, pyqtSignal

class GestureWorker(QThread):
    gesture_signal = pyqtSignal(str)

    def run(self):
        mp_hands = mp.solutions.hands
        mp_draw = mp.solutions.drawing_utils
        hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

        cap = cv2.VideoCapture(0)

        def detect_gesture(landmarks):
            finger_tips = [4, 8, 12, 16, 20]
            finger_fold_status = []

            for tip in finger_tips[1:]:
                finger_fold_status.append(
                    1 if landmarks[tip].y < landmarks[tip - 2].y else 0
                )

            if landmarks[17].x < landmarks[5].x:
                thumb_open = landmarks[4].x > landmarks[3].x
            else:
                thumb_open = landmarks[4].x < landmarks[3].x

            if all(finger_fold_status):
                return "GESTURE DETECTION STARTED"
            elif not any(finger_fold_status) and not thumb_open:
                return "POWER OFF"
            elif not any(finger_fold_status) and thumb_open:
                return "LIGHTS ON"
            elif finger_fold_status == [1, 0, 0, 0]:
                return "FAN ON"
            elif finger_fold_status == [1, 1, 0, 0]:
                return "Victory ✌️"
            else:
                return "Unknown"

        while True:
            success, img = cap.read()
            if not success:
                break

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    landmarks = hand_landmarks.landmark
                    gesture = detect_gesture(landmarks)
                    self.gesture_signal.emit(gesture)

        cap.release()
