# driver_monitoring/emotion.py
# Improved emotion detection
# Uses better backend and preprocessing

import cv2
from deepface import DeepFace

DANGEROUS_EMOTIONS = ['angry', 'fear', 'disgust']

class EmotionDetector:
    def __init__(self):
        self.current_emotion = "neutral"
        self.frame_count = 0
        self.emotion_history = []
        print("Emotion Detector ready! ✅")

    def detect(self, frame):
        self.frame_count += 1
        driver_score = 0
        state = "Alert"

        # Run every 5th frame
        if self.frame_count % 5 == 0:
            try:
                # Improve image for better detection
                # Resize to good size
                small = cv2.resize(frame, (224, 224))

                # Improve brightness and contrast
                lab = cv2.cvtColor(small, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(
                    clipLimit=3.0,
                    tileGridSize=(8,8))
                l = clahe.apply(l)
                enhanced = cv2.merge([l,a,b])
                enhanced = cv2.cvtColor(
                    enhanced, cv2.COLOR_LAB2BGR)

                result = DeepFace.analyze(
                    enhanced,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='opencv',
                    silent=True
                )

                detected = result[0]['dominant_emotion']

                # Smooth emotion using history
                # Avoid flickering
                self.emotion_history.append(detected)
                if len(self.emotion_history) > 5:
                    self.emotion_history.pop(0)

                # Take most common emotion
                from collections import Counter
                self.current_emotion = Counter(
                    self.emotion_history).most_common(1)[0][0]

            except Exception as e:
                pass

        # Check if dangerous
        if self.current_emotion in DANGEROUS_EMOTIONS:
            driver_score = 40
            state = self.current_emotion.capitalize()
            cv2.putText(frame,
                f"EMOTION: {self.current_emotion.upper()}",
                (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 0, 255), 2)
        else:
            cv2.putText(frame,
                f"Emotion: {self.current_emotion}",
                (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2)

        return frame, self.current_emotion, driver_score, state