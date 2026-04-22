# main.py
# Main integration file - Complete Version
# Uses improved drowsiness, emotion and phone detectors

import cv2
import numpy as np
import mediapipe as mp
from ultralytics import YOLO
from deepface import DeepFace
import threading
import time
import os
from collections import Counter

# Import our modules
from fusion.risk_engine import calculate_risk
from chatbot.llm_coach import give_voice_advice
from hardware.arduino_controller import ArduinoController
from driver_monitoring.drowsiness import DrowsinessDetector
from driver_monitoring.emotion import EmotionDetector
from driver_monitoring.phone_detection import PhoneDetector

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
voice_timer   = 0
alert_timer   = 0

# ═══════════════════════════════════
# ROAD DETECTION
# ═══════════════════════════════════

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


# ═══════════════════════════════════
# DRIVER MONITORING
# ═══════════════════════════════════

def process_driver_frame(frame, drowsiness_det,
                         emotion_det, phone_det):
    """Runs all driver monitoring using improved detectors"""
    global driver_score, driver_state

    temp_score = 0
    temp_state = "Alert"

    # Drowsiness detection
    frame, d_state, d_score = drowsiness_det.detect(frame)
    temp_score += d_score
    if d_state != "Alert":
        temp_state = d_state

    # Emotion detection
    frame, emotion, e_score, e_state = emotion_det.detect(frame)
    temp_score += e_score
    if e_state != "Alert" and temp_state == "Alert":
        temp_state = e_state

    # Phone detection
    frame, p_state, p_score = phone_det.detect(frame)
    temp_score += p_score
    if p_state != "Alert":
        temp_state = p_state

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

    # Initialize improved detectors
    print("Initializing detectors...")
    drowsiness_detector = DrowsinessDetector()
    emotion_detector    = EmotionDetector()
    phone_detector      = PhoneDetector()
    print("All detectors ready! ✅")

    # Open cameras
    driver_cam = cv2.VideoCapture(1)
    road_cam   = cv2.VideoCapture(0)

    if not driver_cam.isOpened():
        print("ERROR: Driver camera not found!")
        print("Trying index 0...")
        driver_cam = cv2.VideoCapture(0)
        road_cam   = cv2.VideoCapture(1)

    if not driver_cam.isOpened():
        print("ERROR: No camera found!")
        return

    critical_start_time = None

    print("\nSystem running! Look at driver camera to calibrate...")
    print("Keep eyes open for 2 seconds for calibration\n")

    while True:
        ret1, driver_frame = driver_cam.read()
        ret2, road_frame   = road_cam.read()

        if not ret1:
            print("Driver camera error!")
            break

        # Process frames
        driver_frame = process_driver_frame(
            driver_frame,
            drowsiness_detector,
            emotion_detector,
            phone_detector
        )

        if ret2:
            road_frame = process_road_frame(road_frame)
        else:
            road_frame = process_road_frame(
                driver_frame.copy())

        # Calculate risk
        final_score, level = calculate_risk(
            road_score, driver_score)

        # Show risk on driver frame
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

        # Send alert to Arduino every 2 seconds
        current_time = time.time()
        if current_time - alert_timer > 2:
            arduino.trigger_alert(level)
            alert_timer = current_time

        # Handle CRITICAL escalation
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

        # Voice alert every 5 seconds
        if current_time - voice_timer > 5:
            if level in ["HIGH", "CRITICAL"]:
                threading.Thread(
                    target=give_voice_advice,
                    args=(level, hazard_label,
                          driver_state),
                    daemon=True
                ).start()
                voice_timer = current_time

        # Print status in terminal
        print(f"Road:{road_score}({hazard_label}) "
              f"Driver:{driver_score}({driver_state}) "
              f"Score:{final_score} Level:{level}  ",
              end='\r')

        # Show both camera feeds
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