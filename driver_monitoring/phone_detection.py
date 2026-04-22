# driver_monitoring/phone_detection.py
# Improved phone detection with lower threshold

import cv2
from ultralytics import YOLO

class PhoneDetector:
    def __init__(self):
        print("Loading YOLOv11 for phone detection...")
        self.model = YOLO("yolo11n.pt")
        print("Phone Detector ready! ✅")

    def detect(self, frame):
        driver_score = 0
        state = "Alert"

        # Lower confidence to 0.25 for better detection
        results = self.model(
            frame,
            conf=0.25,
            verbose=False,
            classes=[67]  # 67 = cell phone
        )

        if len(results[0].boxes) > 0:
            driver_score = 50
            state = "Phone"

            # Draw box around phone
            for box in results[0].boxes:
                x1,y1,x2,y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cv2.rectangle(frame,
                    (x1,y1),(x2,y2),
                    (0,0,255), 2)
                cv2.putText(frame,
                    f"PHONE {conf:.0%}",
                    (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0,0,255), 2)

            cv2.putText(frame,
                "PHONE DETECTED!",
                (30, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 0, 255), 2)
        else:
            cv2.putText(frame,
                "No Phone",
                (30, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2)

        return frame, state, driver_score