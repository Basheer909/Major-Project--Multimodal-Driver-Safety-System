# driver_monitoring/drowsiness.py
# This file detects driver drowsiness
# using MediaPipe Face Mesh
# and Eye Aspect Ratio (EAR) formula

import cv2
import numpy as np
import mediapipe as mp
import urllib.request
import os

# Eye landmark indices
LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]

# Drowsiness settings
EAR_THRESHOLD = 0.25  # below this = eyes closing
DROWSY_FRAMES = 20    # 20 frames at 30fps = 0.7 seconds

# Download face landmarker model if not exists
MODEL_PATH = "face_landmarker.task"

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading MediaPipe face model...")
        urllib.request.urlretrieve(
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            MODEL_PATH
        )
        print("Downloaded! ✅")

def get_ear(landmarks, eye_indices, w, h):
    """
    Calculates Eye Aspect Ratio (EAR)
    EAR = vertical eye opening / horizontal eye width
    Low EAR = eyes closing = drowsy
    """
    pts = [(int(landmarks[i].x * w),
            int(landmarks[i].y * h))
           for i in eye_indices]
    A = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
    B = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
    C = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
    return (A + B) / (2.0 * C)


class DrowsinessDetector:
    def __init__(self):
        download_model()
        from mediapipe.tasks.python.vision import FaceLandmarker
        from mediapipe.tasks.python.vision import FaceLandmarkerOptions
        from mediapipe.tasks.python import BaseOptions

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=MODEL_PATH),
            num_faces=1
        )
        self.landmarker = FaceLandmarker.create_from_options(options)
        self.drowsy_frames = 0
        self.is_drowsy = False
        print("Drowsiness Detector ready! ✅")

    def detect(self, frame):
        """
        Detects drowsiness in a frame
        Returns: frame with annotations, is_drowsy, driver_score
        """
        h, w = frame.shape[:2]
        driver_score = 0
        state = "Alert"

        # Convert to MediaPipe format
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        )

        # Detect face landmarks
        result = self.landmarker.detect(mp_image)

        if result.face_landmarks:
            lm = result.face_landmarks[0]

            # Calculate EAR for both eyes
            ear = (get_ear(lm, LEFT_EYE, w, h) +
                   get_ear(lm, RIGHT_EYE, w, h)) / 2.0

            # Check if eyes are closing
            if ear < EAR_THRESHOLD:
                self.drowsy_frames += 1
            else:
                self.drowsy_frames = 0

            # Drowsy if eyes closed for 0.7 seconds
            if self.drowsy_frames >= DROWSY_FRAMES:
                self.is_drowsy = True
                driver_score = 60
                state = "Drowsy"
                cv2.putText(frame,
                    "DROWSY DETECTED!",
                    (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)
            else:
                self.is_drowsy = False
                cv2.putText(frame,
                    f"ALERT  EAR: {ear:.2f}",
                    (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame,
                "NO FACE DETECTED",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 255), 2)

        return frame, self.is_drowsy, driver_score, state


# Test drowsiness detection
if __name__ == "__main__":
    print("Testing Drowsiness Detection...")
    print("Close your eyes for 1 second to test!")
    print("Press Q to quit")

    detector = DrowsinessDetector()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, is_drowsy, score, state = detector.detect(frame)

        cv2.imshow("Drowsiness Test", frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()