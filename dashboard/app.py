# dashboard/app.py
# Streamlit dashboard for Driver Safety System
# Visually appealing with dark theme and animations

import streamlit as st
import cv2
import numpy as np
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page config
st.set_page_config(
    page_title="Driver Safety AI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for stunning UI
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

    /* Hide streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0f1a 100%);
        color: #e0e0e0;
    }

    /* Main title */
    .main-title {
        font-family: 'Orbitron', monospace;
        font-size: 2.2rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00d4ff, #0088ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: shine 3s linear infinite;
        margin-bottom: 0.2rem;
        letter-spacing: 3px;
    }

    .subtitle {
        font-family: 'Rajdhani', sans-serif;
        text-align: center;
        color: #4a9eff;
        font-size: 0.9rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }

    @keyframes shine {
        to { background-position: 200% center; }
    }

    /* Camera containers */
    .camera-container {
        background: linear-gradient(145deg, #0d1117, #161b22);
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 1rem;
        position: relative;
        overflow: hidden;
    }

    .camera-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00d4ff, transparent);
    }

    .camera-label {
        font-family: 'Orbitron', monospace;
        font-size: 0.7rem;
        color: #4a9eff;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    /* Risk score card */
    .risk-card {
        background: linear-gradient(145deg, #0d1117, #161b22);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #21262d;
        position: relative;
        overflow: hidden;
    }

    .risk-number {
        font-family: 'Orbitron', monospace;
        font-size: 4rem;
        font-weight: 900;
        line-height: 1;
        margin: 0.5rem 0;
    }

    .risk-label {
        font-family: 'Orbitron', monospace;
        font-size: 1.2rem;
        letter-spacing: 4px;
        font-weight: 700;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.5rem 0;
    }

    /* Status badges */
    .status-safe { color: #00ff88; border: 1px solid #00ff88; background: rgba(0,255,136,0.1); }
    .status-medium { color: #ffaa00; border: 1px solid #ffaa00; background: rgba(255,170,0,0.1); }
    .status-high { color: #ff6600; border: 1px solid #ff6600; background: rgba(255,102,0,0.1); }
    .status-critical {
        color: #ff0044;
        border: 1px solid #ff0044;
        background: rgba(255,0,68,0.1);
        animation: pulse-red 1s ease-in-out infinite;
    }

    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 5px #ff0044; }
        50% { box-shadow: 0 0 20px #ff0044, 0 0 40px #ff004488; }
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, #0d1117, #161b22);
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin: 0.4rem 0;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }

    .metric-icon {
        font-size: 1.4rem;
        width: 36px;
        text-align: center;
    }

    .metric-info {
        flex: 1;
    }

    .metric-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.75rem;
        color: #8b949e;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .metric-value {
        font-family: 'Orbitron', monospace;
        font-size: 0.95rem;
        font-weight: 700;
        color: #e0e0e0;
    }

    /* Alert banner */
    .alert-banner {
        background: linear-gradient(90deg, rgba(255,0,68,0.15), rgba(255,0,68,0.05));
        border-left: 3px solid #ff0044;
        border-radius: 0 8px 8px 0;
        padding: 0.6rem 1rem;
        margin: 0.5rem 0;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.95rem;
        color: #ff6680;
        letter-spacing: 1px;
    }

    .info-banner {
        background: linear-gradient(90deg, rgba(0,212,255,0.1), rgba(0,212,255,0.02));
        border-left: 3px solid #00d4ff;
        border-radius: 0 8px 8px 0;
        padding: 0.6rem 1rem;
        margin: 0.5rem 0;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.95rem;
        color: #4ad4ff;
        letter-spacing: 1px;
    }

    .safe-banner {
        background: linear-gradient(90deg, rgba(0,255,136,0.1), rgba(0,255,136,0.02));
        border-left: 3px solid #00ff88;
        border-radius: 0 8px 8px 0;
        padding: 0.6rem 1rem;
        margin: 0.5rem 0;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.95rem;
        color: #00ff88;
        letter-spacing: 1px;
    }

    /* Log section */
    .log-entry {
        font-family: 'Rajdhani', monospace;
        font-size: 0.82rem;
        color: #8b949e;
        padding: 0.25rem 0;
        border-bottom: 1px solid #21262d;
        letter-spacing: 0.5px;
    }

    .log-entry span {
        color: #4a9eff;
        margin-right: 0.5rem;
    }

    /* Score bar */
    .score-bar-container {
        background: #161b22;
        border-radius: 6px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }

    /* Divider */
    .custom-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #21262d, transparent);
        margin: 1rem 0;
    }

    /* Section headers */
    .section-header {
        font-family: 'Orbitron', monospace;
        font-size: 0.7rem;
        color: #4a9eff;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .section-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, #21262d, transparent);
    }

    /* Streamlit image override */
    .stImage img {
        border-radius: 8px;
        border: 1px solid #21262d;
    }

    /* Progress bar colors */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00d4ff, #0088ff);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">DRIVER SAFETY AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">⚡ Multimodal Real-Time Monitoring System ⚡</div>', unsafe_allow_html=True)

# Import modules
from ultralytics import YOLO
from fusion.risk_engine import calculate_risk
import mediapipe as mp
from mediapipe.tasks.python.vision import FaceLandmarker
from mediapipe.tasks.python.vision import FaceLandmarkerOptions
from mediapipe.tasks.python import BaseOptions
from deepface import DeepFace
import urllib.request

# Load models
@st.cache_resource
def load_models():
    yolo = YOLO("yolo11n.pt")
    model_path = "face_landmarker.task"
    if not os.path.exists(model_path):
        urllib.request.urlretrieve(
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            model_path
        )
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        num_faces=1
    )
    landmarker = FaceLandmarker.create_from_options(options)
    return yolo, landmarker

with st.spinner("🔄 Initializing AI Models..."):
    yolo_model, landmarker = load_models()

# Settings
LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]
EAR_THRESHOLD = 0.25
DROWSY_FRAMES = 20

HAZARD_SCORES = {
    "person":   ("Pedestrian", 70),
    "dog":      ("Animal", 40),
    "cat":      ("Animal", 40),
    "cow":      ("Animal", 40),
    "bottle":   ("Road Debris", 70),
    "cup":      ("Road Debris", 60),
    "car":      ("Vehicle", 50),
    "truck":    ("Vehicle", 50),
    "bus":      ("Vehicle", 50),
    "motorcycle": ("Vehicle", 50),
    "bicycle":  ("Vehicle", 40),
}

def get_ear(landmarks, eye_indices, w, h):
    pts = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in eye_indices]
    A = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
    B = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
    C = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
    return (A + B) / (2.0 * C)

# Layout
col_driver, col_score, col_road = st.columns([5, 3, 5])

with col_driver:
    st.markdown('<div class="camera-label">📷 Driver Monitor</div>', unsafe_allow_html=True)
    driver_img = st.empty()
    driver_status = st.empty()

with col_score:
    st.markdown('<div class="camera-label">⚠️ Risk Analysis</div>', unsafe_allow_html=True)
    risk_display = st.empty()
    metrics_display = st.empty()

with col_road:
    st.markdown('<div class="camera-label">🚦 Road Scanner</div>', unsafe_allow_html=True)
    road_img = st.empty()
    road_status = st.empty()

# Bottom section
st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
col_voice, col_log = st.columns([1, 1])

with col_voice:
    st.markdown('<div class="section-header">🔊 Voice Alerts</div>', unsafe_allow_html=True)
    voice_display = st.empty()

with col_log:
    st.markdown('<div class="section-header">📋 System Log</div>', unsafe_allow_html=True)
    log_display = st.empty()

# Open cameras
driver_cam = cv2.VideoCapture(1)
road_cam   = cv2.VideoCapture(0)

# State
drowsy_frames = 0
frame_count   = 0
emotion       = "neutral"
log_messages  = []
last_voice    = ""

def add_log(msg, level="info"):
    timestamp = time.strftime("%H:%M:%S")
    log_messages.append((timestamp, msg, level))
    if len(log_messages) > 8:
        log_messages.pop(0)

def get_risk_color(level):
    colors = {
        "SAFE":     "#00ff88",
        "MEDIUM":   "#ffaa00",
        "HIGH":     "#ff6600",
        "CRITICAL": "#ff0044"
    }
    return colors.get(level, "#00ff88")

def get_risk_class(level):
    return f"status-{level.lower()}"

# Main loop
add_log("System initialized", "info")
add_log("Both cameras active", "info")
add_log("AI models loaded", "info")

while True:
    ret1, driver_frame = driver_cam.read()
    ret2, road_frame   = road_cam.read()

    if not ret1:
        st.error("Driver camera not found!")
        break

    frame_count += 1
    h, w = driver_frame.shape[:2]
    temp_driver_score = 0
    temp_driver_state = "Alert"
    detections = []

    # MediaPipe drowsiness
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=cv2.cvtColor(driver_frame, cv2.COLOR_BGR2RGB)
    )
    result = landmarker.detect(mp_image)

    if result.face_landmarks:
        lm = result.face_landmarks[0]
        ear = (get_ear(lm, LEFT_EYE, w, h) + get_ear(lm, RIGHT_EYE, w, h)) / 2.0

        if ear < EAR_THRESHOLD:
            drowsy_frames += 1
        else:
            drowsy_frames = 0

        if drowsy_frames >= DROWSY_FRAMES:
            temp_driver_score += 60
            temp_driver_state = "Drowsy"
            cv2.putText(driver_frame, "DROWSY DETECTED",
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            detections.append(("😴", "Drowsiness", "DETECTED", "critical"))
            add_log("Drowsiness detected!", "critical")
        else:
            cv2.putText(driver_frame, f"EAR: {ear:.2f}  ALERT",
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 100), 2)
            detections.append(("👁️", "Eye Status", f"EAR {ear:.2f}", "safe"))
    else:
        detections.append(("👤", "Face", "Not Detected", "warning"))

    # Emotion detection
    if frame_count % 5 == 0:
        try:
            small = cv2.resize(driver_frame, (640, 480))
            result_e = DeepFace.analyze(small, actions=['emotion'],
                enforce_detection=False, detector_backend='opencv', silent=True)
            emotion = result_e[0]['dominant_emotion']
        except:
            emotion = "neutral"

    if emotion in ['angry', 'fear', 'disgust']:
        temp_driver_score += 40
        if temp_driver_state == "Alert":
            temp_driver_state = emotion.capitalize()
        cv2.putText(driver_frame, f"EMOTION: {emotion.upper()}",
            (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)
        detections.append(("😠", "Emotion", emotion.upper(), "warning"))
    else:
        cv2.putText(driver_frame, f"Emotion: {emotion}",
            (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 100), 2)
        detections.append(("😊", "Emotion", emotion, "safe"))

    # Phone detection
    phone_res = yolo_model(driver_frame, conf=0.4, verbose=False, classes=[67])
    if len(phone_res[0].boxes) > 0:
        temp_driver_score += 50
        temp_driver_state = "Phone"
        cv2.putText(driver_frame, "PHONE IN USE!",
            (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        detections.append(("📱", "Phone", "IN USE", "critical"))
        add_log("Phone usage detected!", "critical")
    else:
        detections.append(("📱", "Phone", "Clear", "safe"))

    driver_score = min(100, temp_driver_score)
    driver_state = temp_driver_state

    # Road detection
    road_score   = 0
    hazard_label = "None"

    if ret2:
        results = yolo_model(road_frame, conf=0.4, verbose=False)
        for box in results[0].boxes:
            class_id   = int(box.cls[0])
            class_name = yolo_model.names[class_id]
            if class_name in HAZARD_SCORES:
                label, score = HAZARD_SCORES[class_name]
                if score > road_score:
                    road_score   = score
                    hazard_label = label
        road_frame = results[0].plot()
        if hazard_label != "None":
            add_log(f"Hazard: {hazard_label} detected!", "warning")

    cv2.putText(road_frame,
        f"HAZARD: {hazard_label} ({road_score}pts)",
        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
        (0, 255, 100) if road_score == 0 else (0, 100, 255), 2)

    # Calculate risk
    final_score, level = calculate_risk(road_score, driver_score)
    risk_color = get_risk_color(level)

    # Add risk overlay to driver frame
    overlay_color = {
        "SAFE": (0, 255, 100), "MEDIUM": (0, 170, 255),
        "HIGH": (0, 100, 255), "CRITICAL": (0, 0, 255)
    }[level]

    cv2.putText(driver_frame, f"RISK: {final_score}/100",
        (20, h-50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, overlay_color, 2)
    cv2.putText(driver_frame, level,
        (20, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, overlay_color, 2)

    # Convert frames
    driver_rgb = cv2.cvtColor(driver_frame, cv2.COLOR_BGR2RGB)
    road_rgb   = cv2.cvtColor(road_frame, cv2.COLOR_BGR2RGB)

    # Update camera feeds
    driver_img.image(driver_rgb, use_container_width=True)
    road_img.image(road_rgb, use_container_width=True)

    # Update driver status
    status_html = ""
    for icon, title, value, stype in detections:
        color_map = {
            "safe": "#00ff88", "warning": "#ffaa00",
            "critical": "#ff0044", "info": "#4a9eff"
        }
        color = color_map.get(stype, "#8b949e")
        status_html += f"""
        <div style="display:flex;align-items:center;gap:8px;padding:4px 0;border-bottom:1px solid #21262d">
            <span style="font-size:16px">{icon}</span>
            <span style="font-family:Rajdhani,sans-serif;font-size:0.8rem;color:#8b949e;text-transform:uppercase;letter-spacing:1px;flex:1">{title}</span>
            <span style="font-family:Orbitron,monospace;font-size:0.75rem;font-weight:700;color:{color}">{value}</span>
        </div>"""
    driver_status.markdown(status_html, unsafe_allow_html=True)

    # Update risk display
    risk_html = f"""
    <div style="text-align:center;padding:1rem 0">
        <div style="font-family:Rajdhani,sans-serif;font-size:0.75rem;color:#8b949e;letter-spacing:3px;text-transform:uppercase;margin-bottom:0.5rem">RISK SCORE</div>
        <div style="font-family:Orbitron,monospace;font-size:3.5rem;font-weight:900;color:{risk_color};line-height:1;text-shadow:0 0 20px {risk_color}44">{final_score}</div>
        <div style="font-family:Rajdhani,sans-serif;font-size:0.7rem;color:#8b949e;margin:0.3rem 0">OUT OF 100</div>
        <div style="background:{'rgba(255,0,68,0.1)' if level=='CRITICAL' else 'rgba(0,0,0,0.3)'};border:1px solid {risk_color};border-radius:20px;padding:0.3rem 1.2rem;display:inline-block;margin:0.5rem 0">
            <span style="font-family:Orbitron,monospace;font-size:0.9rem;font-weight:700;color:{risk_color};letter-spacing:3px">{level}</span>
        </div>
        <div style="background:#161b22;border-radius:6px;height:8px;overflow:hidden;margin:0.8rem 0">
            <div style="width:{final_score}%;height:100%;background:linear-gradient(90deg,{risk_color}88,{risk_color});transition:width 0.3s ease;border-radius:6px"></div>
        </div>
        <div style="margin-top:0.8rem">
            <div style="display:flex;justify-content:space-between;margin:4px 0">
                <span style="font-family:Rajdhani,sans-serif;font-size:0.78rem;color:#8b949e">Road Hazard</span>
                <span style="font-family:Orbitron,monospace;font-size:0.78rem;color:{'#ff6600' if road_score>0 else '#00ff88'}">{road_score}pts</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin:4px 0">
                <span style="font-family:Rajdhani,sans-serif;font-size:0.78rem;color:#8b949e">Driver Risk</span>
                <span style="font-family:Orbitron,monospace;font-size:0.78rem;color:{'#ff6600' if driver_score>0 else '#00ff88'}">{driver_score}pts</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin:4px 0">
                <span style="font-family:Rajdhani,sans-serif;font-size:0.78rem;color:#8b949e">Formula</span>
                <span style="font-family:Orbitron,monospace;font-size:0.72rem;color:#4a9eff">{'x1.5' if road_score>0 and driver_score>0 else 'Direct'}</span>
            </div>
        </div>
    </div>"""
    risk_display.markdown(risk_html, unsafe_allow_html=True)

    # Road status
    road_html = f"""
    <div style="display:flex;align-items:center;gap:8px;padding:6px 0;margin-top:4px">
        <span style="font-size:18px">{'⚠️' if road_score > 0 else '✅'}</span>
        <div>
            <div style="font-family:Rajdhani,sans-serif;font-size:0.75rem;color:#8b949e;text-transform:uppercase;letter-spacing:1px">Detected Hazard</div>
            <div style="font-family:Orbitron,monospace;font-size:0.9rem;font-weight:700;color:{'#ff6600' if road_score>0 else '#00ff88'}">{hazard_label}</div>
        </div>
        <div style="margin-left:auto">
            <div style="font-family:Orbitron,monospace;font-size:1.2rem;font-weight:900;color:{'#ff6600' if road_score>0 else '#00ff88'}">{road_score}</div>
            <div style="font-family:Rajdhani,sans-serif;font-size:0.7rem;color:#8b949e">PTS</div>
        </div>
    </div>"""
    road_status.markdown(road_html, unsafe_allow_html=True)

    # Voice alert display
    alert_messages = {
        "SAFE": ("✅", "All systems normal. Drive safely.", "safe"),
        "MEDIUM": ("⚠️", f"Caution: {hazard_label if hazard_label != 'None' else driver_state} detected.", "info"),
        "HIGH": ("🔶", f"WARNING: {hazard_label if hazard_label != 'None' else driver_state}. Slow down!", "warning"),
        "CRITICAL": ("🚨", f"CRITICAL DANGER! {hazard_label} ahead! Driver is {driver_state}!", "critical"),
    }
    icon, msg, atype = alert_messages[level]
    color_map2 = {"safe": "#00ff88", "info": "#4a9eff", "warning": "#ffaa00", "critical": "#ff0044"}
    bg_map = {"safe": "rgba(0,255,136,0.05)", "info": "rgba(74,159,255,0.05)",
              "warning": "rgba(255,170,0,0.08)", "critical": "rgba(255,0,68,0.1)"}
    alert_color = color_map2[atype]
    alert_bg    = bg_map[atype]

    voice_html = f"""
    <div style="background:{alert_bg};border-left:3px solid {alert_color};border-radius:0 8px 8px 0;padding:0.8rem 1rem;margin:0.3rem 0">
        <div style="display:flex;align-items:center;gap:10px">
            <span style="font-size:1.4rem">{icon}</span>
            <div>
                <div style="font-family:Rajdhani,sans-serif;font-size:0.95rem;color:{alert_color};letter-spacing:1px">{msg}</div>
                <div style="font-family:Rajdhani,monospace;font-size:0.75rem;color:#8b949e;margin-top:2px">Level: {level} | Score: {final_score}/100</div>
            </div>
        </div>
    </div>"""
    voice_display.markdown(voice_html, unsafe_allow_html=True)

    # System log
    log_html = ""
    for ts, lmsg, ltype in reversed(log_messages[-6:]):
        lcolor = color_map2.get(ltype, "#8b949e")
        log_html += f"""
        <div style="display:flex;gap:8px;padding:4px 0;border-bottom:1px solid #21262d11;font-family:Rajdhani,monospace;font-size:0.8rem">
            <span style="color:#4a9eff;min-width:60px">{ts}</span>
            <span style="color:{lcolor}">{lmsg}</span>
        </div>"""
    log_display.markdown(log_html or '<div style="color:#8b949e;font-size:0.8rem">No events yet...</div>',
        unsafe_allow_html=True)

    time.sleep(0.03)

driver_cam.release()
road_cam.release()
