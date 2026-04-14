# driver_monitoring/emotion.py
# This file detects driver emotion
# using DeepFace library
# Dangerous emotions: angry, fear, disgust
# Safe emotions: happy, neutral, surprise, sad

import cv2
from deepface import DeepFace

# Dangerous emotions that affect driving
DANGEROUS_EMOTIONS = ['angry', 'fear', 'disgust']

class EmotionDetector:
    def __init__(self):
        self.current_emotion = "neutral"
        self.frame_count = 0
        print("Emotion Detector ready! ✅")

    def detect(self, frame):
        """
        Detects emotion in a frame
        Runs every 5th frame to keep system fast
        Returns: frame with annotations, emotion, driver_score
        """
        self.frame_count += 1
        driver_score = 0
        state = "Alert"

        # Run DeepFace every 5th frame
        if self.frame_count % 5 == 0:
            try:
                # Resize frame for faster processing
                small = cv2.resize(frame, (640, 480))

                result = DeepFace.analyze(
                    small,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='opencv',
                    silent=True
                )
                self.current_emotion = result[0]['dominant_emotion']
            except Exception as e:
                self.current_emotion = "neutral"

        # Check if emotion is dangerous
        if self.current_emotion in DANGEROUS_EMOTIONS:
            driver_score = 40
            state = self.current_emotion.capitalize()
            cv2.putText(frame,
                f"DANGEROUS: {self.current_emotion.upper()}",
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


# Test emotion detection
if __name__ == "__main__":
    print("Testing Emotion Detection...")
    print("Make angry/happy/sad face to test!")
    print("Press Q to quit")

    detector = EmotionDetector()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, emotion, score, state = detector.detect(frame)

        # Show score on frame
        cv2.putText(frame,
            f"Driver Score: {score}",
            (30, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (255, 255, 0), 2)

        cv2.imshow("Emotion Test", frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()