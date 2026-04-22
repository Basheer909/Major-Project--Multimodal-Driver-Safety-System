# driver_monitoring/drowsiness.py
# Improved drowsiness detection with calibration
# Handles glasses wearers automatically

import cv2
import numpy as np
import mediapipe as mp
import urllib.request
import os

LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]

MODEL_PATH = "face_landmarker.task"

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading MediaPipe face model...")
        urllib.request.urlretrieve(
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            MODEL_PATH
        )

def get_ear(landmarks, eye_indices, w, h):
    pts = [(int(landmarks[i].x * w),
            int(landmarks[i].y * h))
           for i in eye_indices]
    A = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
    B = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
    C = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
    if C == 0:
        return 0.3
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

        # Calibration variables
        self.calibration_frames = []
        self.calibrated = False
        self.ear_threshold = 0.25  # default
        self.drowsy_frames = 0
        self.DROWSY_FRAME_LIMIT = 20
        print("Drowsiness Detector ready! ✅")

    def calibrate(self, ear_value):
        """
        Collects first 60 frames to find
        personal EAR baseline
        Handles glasses wearers automatically
        """
        if not self.calibrated:
            self.calibration_frames.append(ear_value)
            if len(self.calibration_frames) >= 60:
                avg_ear = np.mean(self.calibration_frames)
                # Set threshold at 75% of personal average
                self.ear_threshold = avg_ear * 0.75
                self.calibrated = True
                print(f"Calibrated! Personal EAR threshold: {self.ear_threshold:.3f}")

    def detect(self, frame):
        h, w = frame.shape[:2]
        driver_score = 0
        state = "Alert"

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        )
        result = self.landmarker.detect(mp_image)

        if result.face_landmarks:
            lm = result.face_landmarks[0]
            ear = (get_ear(lm, LEFT_EYE, w, h) +
                   get_ear(lm, RIGHT_EYE, w, h)) / 2.0

            # Calibrate first
            self.calibrate(ear)

            if ear < self.ear_threshold:
                self.drowsy_frames += 1
            else:
                self.drowsy_frames = 0

            if self.drowsy_frames >= self.DROWSY_FRAME_LIMIT:
                driver_score = 60
                state = "Drowsy"
                cv2.putText(frame,
                    "DROWSY DETECTED!",
                    (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)
            else:
                # Show calibration progress
                if not self.calibrated:
                    progress = len(self.calibration_frames)
                    cv2.putText(frame,
                        f"Calibrating... {progress}/60",
                        (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 255), 2)
                else:
                    cv2.putText(frame,
                        f"ALERT  EAR:{ear:.2f} T:{self.ear_threshold:.2f}",
                        (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)
        else:
            cv2.putText(frame,
                "NO FACE DETECTED",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 255), 2)

        return frame, state, driver_score