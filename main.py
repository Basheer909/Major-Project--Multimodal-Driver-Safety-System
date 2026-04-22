# main.py
# Main integration file
# Connects all modules together
# Pothole model disabled - training in progress

import cv2
import numpy as np
import mediapipe as mp
from ultralytics import YOLO
from deepface import DeepFace
import threading
import time
import os

# Import our modules
from fusion.risk_engine import calculate_risk
from chatbot.llm_coach import give_voice_advice
from hardware.arduino_controller import ArduinoController

# ═══════════════════════════════════
# LOAD MODELS
# ═══════════════════════════════════

print("Loading YOLOv11 model...")
yolo_model = YOLO("yolo11n.pt")
print("YOLOv11 loaded! ✅")

# Pothole model disabled - training in progress
pothole_model = None
print("Pothole model disabled - training in progress")

# Load earphone model if exists
earphone_model = None
if os.path.exists("models/earphone_best.pt"):
    print("Loading earphone model...")
    earphone_model = YOLO("models/earphone_best.pt")
    print("Earphone model loaded! ✅")
else:
    print("Earphone model not found - skipping")

print("Loading MediaPipe...")
from mediapipe.tasks.python.vision import FaceLandmarker
from mediapipe.tasks.python.vision import FaceLandmarkerOptions
from mediapipe.tasks.python import BaseOptions
import urllib.request

MODEL_PATH = "face_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("Downloading face landmarker model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        MODEL_PATH
    )
print("MediaPipe loaded! ✅")

# ═══════════════════════════════════
# SETTINGS
# ═══════════════════════════════════

LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]
EAR_THRESHOLD = 0.25
DROWSY_FRAMES = 20

HAZARD_SCORES = {
    "person":        ("Pedestrian", 70),
    "dog":           ("Animal", 40),
    "cat":           ("Animal", 40),
    "cow":           ("Animal", 40),
    "horse":         ("Animal", 40),
    "bird":          ("Animal", 30),
    "bottle":        ("Road Debris", 70),
    "cup":           ("Road Debris", 60),
    "backpack":      ("Road Debris", 60),
    "suitcase":      ("Road Debris", 60),
    "sports ball":   ("Road Debris", 50),
    "car":           ("Vehicle", 50),
    "truck":         ("Vehicle", 50),
    "bus":           ("Vehicle", 50),
    "motorcycle":    ("Vehicle", 50),
    "bicycle":       ("Vehicle", 40),
    "traffic light": ("Traffic Signal", 30),
    "stop sign":     ("Stop Sign", 30),
}

# ═══════════════════════════════════
# SHARED VARIABLES
# ═══════════════════════════════════

road_score    = 0
hazard_label  = "None"
driver_score  = 0
driver_state  = "Alert"
emotion       = "neutral"
drowsy_frames = 0
frame_count   = 0
voice_timer   = 0
alert_timer   = 0

# ═══════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════

def get_ear(landmarks, eye_indices, w, h):
    pts = [(int(landmarks[i].x * w),
            int(landmarks[i].y * h))
           for i in eye_indices]
    A = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
    B = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
    C = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
    return (A + B) / (2.0 * C)


def process_road_frame(frame):
    """Runs YOLOv11 on road camera"""
    global road_score, hazard_label

    results = yolo_model(frame, conf=0.4, verbose=False)
    max_score = 0
    max_label = "None"

    for box in results[0].boxes:
        class_id   = int(box.cls[0])
        class_name = yolo_model.names[class_id]
        if class_name in HAZARD_SCORES:
            label, score = HAZARD_SCORES[class_name]
            if score > max_score:
                max_score = score
                max_label = label

    road_score   = max_score
    hazard_label = max_label

    annotated = results[0].plot()

    colour = (0, 255, 0) if max_score == 0 else (0, 0, 255)
    cv2.putText(annotated,
        f"Hazard: {max_label} ({max_score}pts)",
        (30, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7, colour, 2)

    return annotated


def process_driver_frame(frame, landmarker):
    """Runs all driver monitoring"""
    global driver_score, driver_state
    global drowsy_frames, frame_count, emotion

    frame_count += 1
    h, w = frame.shape[:2]
    temp_score = 0
    temp_state = "Alert"

    # MediaPipe drowsiness
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    )
    result = landmarker.detect(mp_image)

    if result.face_landmarks:
        lm = result.face_landmarks[0]
        ear = (get_ear(lm, LEFT_EYE, w, h) +
               get_ear(lm, RIGHT_EYE, w, h)) / 2.0

        if ear < EAR_THRESHOLD:
            drowsy_frames += 1
        else:
            drowsy_frames = 0

        if drowsy_frames >= DROWSY_FRAMES:
            temp_score += 60
            temp_state  = "Drowsy"
            cv2.putText(frame, "DROWSY!",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 2)
        else:
            cv2.putText(frame, f"ALERT EAR:{ear:.2f}",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "NO FACE DETECTED",
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 255), 2)

    # DeepFace emotion every 5th frame
    if frame_count % 5 == 0:
        try:
            small = cv2.resize(frame, (640, 480))
            result_emotion = DeepFace.analyze(
                small,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv',
                silent=True
            )
            emotion = result_emotion[0]['dominant_emotion']
        except:
            emotion = "neutral"

    if emotion in ['angry', 'fear', 'disgust']:
        temp_score += 40
        if temp_state == "Alert":
            temp_state = emotion.capitalize()
        cv2.putText(frame,
            f"EMOTION: {emotion.upper()}",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 0, 255), 2)
    else:
        cv2.putText(frame,
            f"Emotion: {emotion}",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 0), 2)

    # Phone detection
    phone_results = yolo_model(
        frame, conf=0.4, verbose=False, classes=[67])
    if len(phone_results[0].boxes) > 0:
        temp_score += 50
        temp_state  = "Phone"
        cv2.putText(frame, "PHONE DETECTED!",
            (30, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "No Phone",
            (30, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 0), 2)

    # Earphone detection
    if earphone_model is not None:
        earphone_results = earphone_model(
            frame, conf=0.4, verbose=False)
        if len(earphone_results[0].boxes) > 0:
            temp_score += 30
            if temp_state == "Alert":
                temp_state = "Earphone"
            cv2.putText(frame, "EARPHONE DETECTED!",
                (30, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 0, 255), 2)

    driver_score = min(100, temp_score)
    driver_state = temp_state
    return frame


# ═══════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════

def main():
    global voice_timer, alert_timer

    print("\nStarting Driver Safety System...")
    print("Press Q to quit\n")

    # Initialize Arduino
    arduino = ArduinoController()

    # Open cameras
    driver_cam = cv2.VideoCapture(1)
    road_cam   = cv2.VideoCapture(0)

    if not driver_cam.isOpened():
        print("ERROR: Driver camera not found!")
        return

    # Setup MediaPipe
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=MODEL_PATH),
        num_faces=1
    )

    critical_start_time = None

    with FaceLandmarker.create_from_options(options) as landmarker:
        while True:
            ret1, driver_frame = driver_cam.read()
            ret2, road_frame   = road_cam.read()

            if not ret1:
                print("Driver camera error!")
                break

            driver_frame = process_driver_frame(
                driver_frame, landmarker)

            if ret2:
                road_frame = process_road_frame(road_frame)
            else:
                road_frame = process_road_frame(
                    driver_frame.copy())

            final_score, level = calculate_risk(
                road_score, driver_score)

            colours = {
                "SAFE":     (0, 255, 0),
                "MEDIUM":   (0, 255, 255),
                "HIGH":     (0, 165, 255),
                "CRITICAL": (0, 0, 255)
            }
            colour = colours[level]

            cv2.putText(driver_frame,
                f"RISK: {final_score}/100 - {level}",
                (30, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8, colour, 2)

            current_time = time.time()
            if current_time - alert_timer > 2:
                arduino.trigger_alert(level)
                alert_timer = current_time

            if level == "CRITICAL":
                if critical_start_time is None:
                    critical_start_time = current_time
                elapsed = current_time - critical_start_time
                if elapsed > 10:
                    arduino.trigger_external_led("PULSE")
                if elapsed > 20:
                    arduino.trigger_external_led("SOLID")
            else:
                critical_start_time = None
                arduino.trigger_external_led("OFF")

            if current_time - voice_timer > 5:
                if level in ["HIGH", "CRITICAL"]:
                    threading.Thread(
                        target=give_voice_advice,
                        args=(level, hazard_label,
                              driver_state),
                        daemon=True
                    ).start()
                    voice_timer = current_time

            print(f"Road:{road_score}({hazard_label}) "
                  f"Driver:{driver_score}({driver_state}) "
                  f"Score:{final_score} Level:{level}  ",
                  end='\r')

            cv2.imshow("Road Camera", road_frame)
            cv2.imshow("Driver Camera", driver_frame)

            if cv2.waitKey(1) == ord('q'):
                break

    driver_cam.release()
    road_cam.release()
    arduino.close()
    cv2.destroyAllWindows()
    print("\nSystem stopped.")


if __name__ == "__main__":
    main()