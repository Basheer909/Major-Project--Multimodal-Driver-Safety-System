# dashboard/app.py
# ULTIMATE Driver Safety AI Dashboard
# Best possible UI/UX with cyberpunk military aesthetic

import streamlit as st
import cv2
import numpy as np
import time
import os
import sys
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="SafeGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

:root {
    --bg-primary:    #020810;
    --bg-card:       #071224;
    --bg-card2:      #060d1a;
    --border:        #0d2744;
    --border-glow:   #0a4a8a;
    --accent-blue:   #00a8ff;
    --accent-cyan:   #00e5ff;
    --accent-green:  #00ff9d;
    --accent-yellow: #ffd600;
    --accent-orange: #ff6d00;
    --accent-red:    #ff1744;
    --text-muted:    #4a6fa5;
}

#MainMenu, footer, header, .stDeployButton { display: none !important; }
.stApp { background: var(--bg-primary) !important; }
.block-container { padding: 0.5rem 1rem !important; max-width: 100% !important; }

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,168,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,168,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

.header-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 1.2rem;
    background: linear-gradient(90deg, rgba(0,168,255,0.08), rgba(0,229,255,0.04), rgba(0,168,255,0.08));
    border-bottom: 1px solid var(--border);
    border-top: 1px solid var(--border-glow);
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
}

.header-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 60%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
    animation: headerScan 4s linear infinite;
}

@keyframes headerScan { to { left: 200%; } }

.header-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.3rem;
    font-weight: 900;
    color: var(--accent-cyan);
    letter-spacing: 4px;
}

.header-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    color: var(--text-muted);
    letter-spacing: 3px;
    margin-top: 2px;
}

.hstat-val {
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--accent-green);
    text-align: center;
}

.hstat-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    color: var(--text-muted);
    letter-spacing: 1px;
    text-align: center;
}

.status-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,255,157,0.08);
    border: 1px solid rgba(0,255,157,0.2);
    border-radius: 20px;
    padding: 4px 14px;
}

@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.8)} }
@keyframes critFlash { 0%,100%{opacity:1} 50%{opacity:0.75} }

.cam-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 5px 10px;
    background: rgba(0,168,255,0.05);
    border-bottom: 1px solid var(--border);
    border-radius: 8px 8px 0 0;
}

.cam-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.62rem;
    color: var(--accent-blue);
    letter-spacing: 2px;
}

.cam-badge {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    padding: 1px 7px;
    border-radius: 10px;
    color: var(--accent-green);
    border: 1px solid rgba(0,255,157,0.3);
    background: rgba(0,255,157,0.08);
}

.risk-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 0.8rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.risk-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
}

.risk-number {
    font-family: 'Orbitron', monospace;
    font-size: 3.2rem;
    font-weight: 900;
    line-height: 1;
    transition: color 0.4s;
}

.risk-level-badge {
    font-family: 'Orbitron', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 14px;
    border-radius: 16px;
    display: inline-block;
    letter-spacing: 3px;
    transition: all 0.4s;
    margin: 6px 0 10px;
}

.risk-bar-track {
    background: rgba(255,255,255,0.05);
    border-radius: 4px;
    height: 5px;
    overflow: hidden;
    margin: 6px 0;
}

.score-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 5px;
    margin: 8px 0;
}

.score-cell {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 5px 6px;
}

.score-cell-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.55rem;
    color: var(--text-muted);
    letter-spacing: 1px;
}

.score-cell-val {
    font-family: 'Orbitron', monospace;
    font-size: 1rem;
    font-weight: 700;
}

.formula-chip {
    background: rgba(0,168,255,0.08);
    border: 1px solid rgba(0,168,255,0.2);
    border-radius: 5px;
    padding: 3px 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    color: var(--accent-blue);
    margin-top: 4px;
}

.detect-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 5px;
    margin-top: 5px;
}

.detect-card {
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-radius: 7px;
    padding: 7px 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.detect-card.danger { border-color: rgba(255,23,68,0.35); background: rgba(255,23,68,0.04); }
.detect-card.warning { border-color: rgba(255,109,0,0.35); background: rgba(255,109,0,0.04); }

.detect-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.55rem;
    color: var(--text-muted);
    letter-spacing: 1px;
    text-transform: uppercase;
}

.detect-value {
    font-family: 'Orbitron', monospace;
    font-size: 0.68rem;
    font-weight: 700;
}

.alert-chip {
    padding: 2px 8px;
    border-radius: 10px;
    font-family: 'Orbitron', monospace;
    font-size: 0.58rem;
    border: 1px solid;
    letter-spacing: 1px;
    opacity: 0.25;
    transition: all 0.3s;
    display: inline-block;
    margin: 2px;
}

.alert-chip.active { opacity: 1; }
.c-buz { color:#ff6d00;border-color:#ff6d00 } .c-buz.active { background:rgba(255,109,0,0.1);box-shadow:0 0 7px rgba(255,109,0,0.4) }
.c-led { color:#ff1744;border-color:#ff1744 } .c-led.active { background:rgba(255,23,68,0.1);box-shadow:0 0 7px rgba(255,23,68,0.4) }
.c-vib { color:#aa00ff;border-color:#aa00ff } .c-vib.active { background:rgba(170,0,255,0.1);box-shadow:0 0 7px rgba(170,0,255,0.4) }
.c-voice { color:#00e5ff;border-color:#00e5ff } .c-voice.active { background:rgba(0,229,255,0.1);box-shadow:0 0 7px rgba(0,229,255,0.4) }
.c-sms { color:#ffd600;border-color:#ffd600 } .c-sms.active { background:rgba(255,214,0,0.1);box-shadow:0 0 7px rgba(255,214,0,0.4) }

.log-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 7px 9px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
}

.log-entry { display:flex;gap:8px;padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.02) }
.log-time { color:#00a8ff;min-width:58px }
.log-info { color:#4a6fa5 }
.log-warning { color:#ff6d00 }
.log-critical { color:#ff1744 }

.stImage > img { border-radius: 6px !important; border: 1px solid var(--border) !important; }
div[data-testid="column"] { padding: 0 3px !important; }
</style>
""", unsafe_allow_html=True)

# ── IMPORTS ──
from ultralytics import YOLO
from fusion.risk_engine import calculate_risk
from chatbot.llm_coach import give_voice_advice
from driver_monitoring.drowsiness import DrowsinessDetector
from driver_monitoring.emotion import EmotionDetector
from driver_monitoring.phone_detection import PhoneDetector

@st.cache_resource
def load_models():
    return (YOLO("yolo11n.pt"),
            DrowsinessDetector(),
            EmotionDetector(),
            PhoneDetector())

with st.spinner("🔄 Initializing SafeGuard AI..."):
    yolo_model, drowsiness_det, emotion_det, phone_det = load_models()

HAZARD_SCORES = {
    "person":("Pedestrian",70),"dog":("Animal",40),"cat":("Animal",40),
    "cow":("Animal",40),"horse":("Animal",40),"bird":("Animal",30),
    "bottle":("Road Debris",70),"cup":("Road Debris",60),
    "backpack":("Road Debris",60),"suitcase":("Road Debris",60),
    "sports ball":("Road Debris",50),"car":("Vehicle",50),
    "truck":("Vehicle",50),"bus":("Vehicle",50),
    "motorcycle":("Vehicle",50),"bicycle":("Vehicle",40),
}

start_time = time.time()
header_ph  = st.empty()

col_d, col_r, col_road = st.columns([5,3,5])
with col_d:
    st.markdown('<div class="cam-header"><div class="cam-title">📷 DRIVER MONITOR</div><div class="cam-badge">● LIVE</div></div>', unsafe_allow_html=True)
    driver_img = st.empty()
    detect_ph  = st.empty()

with col_r:
    risk_ph = st.empty()

with col_road:
    st.markdown('<div class="cam-header"><div class="cam-title">🚦 ROAD SCANNER</div><div class="cam-badge">● LIVE</div></div>', unsafe_allow_html=True)
    road_img = st.empty()
    road_ph  = st.empty()

st.markdown('<div style="height:5px"></div>', unsafe_allow_html=True)
col_a, col_v, col_l = st.columns([2,3,3])
with col_a: alerts_ph = st.empty()
with col_v: voice_ph  = st.empty()
with col_l: log_ph    = st.empty()

driver_cam = cv2.VideoCapture(1)
road_cam   = cv2.VideoCapture(0)
if not driver_cam.isOpened():
    driver_cam = cv2.VideoCapture(0)
    road_cam   = cv2.VideoCapture(1)

log_msgs    = []
voice_timer = 0
frame_count = 0

def add_log(msg, level="info"):
    log_msgs.append((time.strftime("%H:%M:%S"), msg, level))
    if len(log_msgs) > 6: log_msgs.pop(0)

def get_col(level):
    return {"SAFE":"#00ff9d","MEDIUM":"#ffd600","HIGH":"#ff6d00","CRITICAL":"#ff1744"}.get(level,"#00ff9d")

def get_bg(level):
    return {"SAFE":"rgba(0,255,157,0.1)","MEDIUM":"rgba(255,214,0,0.1)","HIGH":"rgba(255,109,0,0.1)","CRITICAL":"rgba(255,23,68,0.1)"}.get(level,"rgba(0,255,157,0.1)")

add_log("SafeGuard AI started","info")
add_log("Both cameras active","info")
add_log("Calibrating EAR threshold...","info")

while True:
    ret1, driver_frame = driver_cam.read()
    ret2, road_frame   = road_cam.read()
    if not ret1: break

    frame_count += 1
    uptime = int(time.time()-start_time)
    ups = f"{uptime//60:02d}:{uptime%60:02d}"

    # ── DRIVER ──
    temp_score = 0; temp_state = "Alert"; dets = []

    driver_frame, d_state, d_score = drowsiness_det.detect(driver_frame)
    temp_score += d_score
    if d_state != "Alert":
        temp_state = d_state
        dets.append(("😴","DROWSY","DETECTED","danger","#ff1744"))
        if frame_count%30==0: add_log("Drowsiness detected!","critical")
    else:
        dets.append(("👁️","EYES","Alert","","#00ff9d"))

    driver_frame, emotion, e_score, e_state = emotion_det.detect(driver_frame)
    temp_score += e_score
    if e_state != "Alert" and temp_state == "Alert":
        temp_state = e_state
        dets.append(("😠","EMOTION",emotion.upper()[:8],"warning","#ff6d00"))
        if frame_count%30==0: add_log(f"Emotion: {emotion}","warning")
    else:
        dets.append(("😊","EMOTION",emotion[:8],"","#00ff9d"))

    driver_frame, p_state, p_score = phone_det.detect(driver_frame)
    temp_score += p_score
    if p_state != "Alert":
        temp_state = p_state
        dets.append(("📱","PHONE","IN USE","danger","#ff1744"))
        if frame_count%30==0: add_log("Phone usage detected!","critical")
    else:
        dets.append(("📱","PHONE","Clear","","#00ff9d"))

    driver_score = min(100, temp_score)
    driver_state = temp_state

    # ── ROAD ──
    road_score = 0; hazard_label = "None"
    if ret2:
        results = yolo_model(road_frame, conf=0.4, verbose=False)
        for box in results[0].boxes:
            cn = yolo_model.names[int(box.cls[0])]
            if cn in HAZARD_SCORES:
                lbl, sc = HAZARD_SCORES[cn]
                if sc > road_score: road_score=sc; hazard_label=lbl
        road_frame = results[0].plot()
        hc = (0,255,100) if road_score==0 else (0,80,255)
        cv2.putText(road_frame, f"  {hazard_label} ({road_score}pts)", (12,36), cv2.FONT_HERSHEY_SIMPLEX, 0.72, hc, 2)
        if hazard_label!="None" and frame_count%30==0: add_log(f"Hazard: {hazard_label}","warning")

    # ── RISK ──
    final_score, level = calculate_risk(road_score, driver_score)
    col = get_col(level); bg = get_bg(level)
    is_critical = level=="CRITICAL"; is_high = level in ["HIGH","CRITICAL"]

    cv2_col = {"SAFE":(0,255,157),"MEDIUM":(0,214,255),"HIGH":(0,109,255),"CRITICAL":(23,68,255)}[level]
    cv2.putText(driver_frame, f"  RISK {final_score}/100  {level}", (12,36), cv2.FONT_HERSHEY_SIMPLEX, 0.72, cv2_col, 2)

    # ── VOICE ──
    current_time = time.time()
    if current_time-voice_timer > 5 and is_high:
        threading.Thread(target=give_voice_advice, args=(level,hazard_label,driver_state), daemon=True).start()
        voice_timer = current_time
        add_log(f"Voice alert fired: {level}","info")

    buzzer_on = is_high; led_on = is_critical; vib_on = is_critical
    voice_on  = is_high; sms_on = is_critical and (current_time-start_time)>30

    # ═══ UPDATE UI ═══

    # Header
    header_ph.markdown(f"""
    <div class="header-wrap">
        <div>
            <div style="display:flex;align-items:center;gap:10px">
                <div style="width:34px;height:34px;border:2px solid var(--accent-cyan);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:17px;box-shadow:0 0 12px rgba(0,229,255,0.4)">🛡️</div>
                <div>
                    <div class="header-title">SAFEGUARD AI</div>
                    <div class="header-subtitle">MULTIMODAL DRIVER SAFETY — VTU 2025-26</div>
                </div>
            </div>
        </div>
        <div style="display:flex;gap:20px;align-items:center">
            <div><div class="hstat-val">{ups}</div><div class="hstat-label">UPTIME</div></div>
            <div><div class="hstat-val" style="color:{'#ff1744' if road_score>0 else '#00ff9d'}">{road_score}</div><div class="hstat-label">ROAD PTS</div></div>
            <div><div class="hstat-val" style="color:{'#ff1744' if driver_score>0 else '#00ff9d'}">{driver_score}</div><div class="hstat-label">DRIVER PTS</div></div>
            <div><div class="hstat-val">{frame_count}</div><div class="hstat-label">FRAMES</div></div>
        </div>
        <div class="status-pill" style="background:{'rgba(255,23,68,0.08)' if is_critical else 'rgba(0,255,157,0.08)'};border-color:{'rgba(255,23,68,0.3)' if is_critical else 'rgba(0,255,157,0.2)'}">
            <div style="width:8px;height:8px;border-radius:50%;background:{col};animation:pulse 1.5s ease-in-out infinite"></div>
            <div style="font-family:Orbitron,monospace;font-size:0.65rem;color:{col};letter-spacing:2px">{level}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Camera feeds
    driver_img.image(cv2.cvtColor(driver_frame,cv2.COLOR_BGR2RGB), use_container_width=True)
    road_img.image(cv2.cvtColor(road_frame,cv2.COLOR_BGR2RGB),     use_container_width=True)

    # Detection cards
    cards = '<div class="detect-grid">'
    for icon,title,value,dtype,vc in dets:
        cards += f'<div class="detect-card {dtype}"><span style="font-size:17px">{icon}</span><div><div class="detect-title">{title}</div><div class="detect-value" style="color:{vc}">{value}</div></div></div>'
    cards += '</div>'
    detect_ph.markdown(cards, unsafe_allow_html=True)

    # Risk panel
    formula = f"({road_score}+{driver_score})×1.5" if road_score>0 and driver_score>0 else "DIRECT SUM"
    risk_ph.markdown(f"""
    <div class="risk-panel" style="{'animation:critFlash 0.8s ease-in-out infinite' if is_critical else ''}">
        <div style="font-family:Share Tech Mono,monospace;font-size:0.58rem;color:var(--text-muted);letter-spacing:3px;margin-bottom:3px">UNIFIED RISK SCORE</div>
        <div class="risk-number" style="color:{col};text-shadow:0 0 18px {col}44">{final_score}</div>
        <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:var(--text-muted);letter-spacing:2px">OUT OF 100</div>
        <div class="risk-level-badge" style="color:{col};border:1px solid {col};background:{bg}">{level}</div>
        <div class="risk-bar-track"><div style="height:100%;width:{final_score}%;background:linear-gradient(90deg,{col}88,{col});border-radius:4px;transition:width 0.6s ease"></div></div>
        <div class="score-grid">
            <div class="score-cell"><div class="score-cell-label">ROAD HAZARD</div><div class="score-cell-val" style="color:{'#ff6d00' if road_score>0 else '#00ff9d'}">{road_score}</div></div>
            <div class="score-cell"><div class="score-cell-label">DRIVER RISK</div><div class="score-cell-val" style="color:{'#ff6d00' if driver_score>0 else '#00ff9d'}">{driver_score}</div></div>
        </div>
        <div class="formula-chip">⚡ {formula} = {final_score}</div>
        <div style="margin-top:6px;font-family:Share Tech Mono,monospace;font-size:0.58rem;color:var(--text-muted)">
            {'1.5× COMPOUNDING ACTIVE' if road_score>0 and driver_score>0 else 'STANDARD CALCULATION'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Road metric
    road_ph.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:6px 8px;background:rgba(0,15,30,0.6);border:1px solid #0d2744;border-radius:6px;margin-top:4px">
        <span style="font-size:19px">{'⚠️' if road_score>0 else '✅'}</span>
        <div style="flex:1">
            <div style="font-family:Share Tech Mono,monospace;font-size:0.57rem;color:#4a6fa5;letter-spacing:1px">DETECTED HAZARD</div>
            <div style="font-family:Orbitron,monospace;font-size:0.82rem;font-weight:700;color:{'#ff6d00' if road_score>0 else '#00ff9d'}">{hazard_label}</div>
        </div>
        <div style="text-align:right">
            <div style="font-family:Orbitron,monospace;font-size:1.3rem;font-weight:900;color:{'#ff6d00' if road_score>0 else '#00ff9d'}">{road_score}</div>
            <div style="font-family:Share Tech Mono,monospace;font-size:0.52rem;color:#4a6fa5">PTS</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Alert chips
    alerts_ph.markdown(f"""
    <div style="background:rgba(5,15,30,0.8);border:1px solid #0d2744;border-radius:8px;padding:7px 9px">
        <div style="font-family:Share Tech Mono,monospace;font-size:0.57rem;color:#4a6fa5;letter-spacing:2px;margin-bottom:5px">ALERT LAYERS</div>
        <div>
            <span class="alert-chip c-buz {'active' if buzzer_on else ''}">BUZZER</span>
            <span class="alert-chip c-led {'active' if led_on else ''}">LED</span>
            <span class="alert-chip c-vib {'active' if vib_on else ''}">VIBRATE</span>
            <span class="alert-chip c-voice {'active' if voice_on else ''}">VOICE AI</span>
            <span class="alert-chip c-sms {'active' if sms_on else ''}">SMS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Voice banner
    vm = {"SAFE":("✅","All systems normal. Drive safely.","#00ff9d","rgba(0,255,157,0.06)","rgba(0,255,157,0.18)"),
          "MEDIUM":(f"⚠️",f"Caution: {hazard_label if hazard_label!='None' else driver_state} detected.","#ffd600","rgba(255,214,0,0.06)","rgba(255,214,0,0.2)"),
          "HIGH":("🔶",f"Warning! {hazard_label if hazard_label!='None' else driver_state}. Slow down!","#ff6d00","rgba(255,109,0,0.07)","rgba(255,109,0,0.28)"),
          "CRITICAL":("🚨",f"CRITICAL! {hazard_label} ahead! Driver is {driver_state}!","#ff1744","rgba(255,23,68,0.09)","rgba(255,23,68,0.38)")}[level]
    voice_ph.markdown(f"""
    <div style="background:{vm[3]};border:1px solid {vm[4]};border-radius:8px;padding:9px 12px;display:flex;align-items:center;gap:10px">
        <span style="font-size:19px">{vm[0]}</span>
        <div style="flex:1">
            <div style="font-family:Share Tech Mono,monospace;font-size:0.57rem;color:#4a6fa5;letter-spacing:2px;margin-bottom:2px">VOICE ALERT</div>
            <div style="font-family:Exo 2,sans-serif;font-size:0.82rem;font-weight:600;color:{vm[2]}">{vm[1]}</div>
        </div>
        <div style="font-family:Share Tech Mono,monospace;font-size:0.58rem;color:{vm[2]};text-align:right">{level}<br/>{final_score}/100</div>
    </div>
    """, unsafe_allow_html=True)

    # Log
    log_html = '<div class="log-panel"><div style="font-family:Share Tech Mono,monospace;font-size:0.56rem;color:#1e3a5f;letter-spacing:2px;margin-bottom:4px;border-bottom:1px solid #0d2744;padding-bottom:2px">SYSTEM LOG</div>'
    for ts,msg,lvl in reversed(log_msgs):
        log_html += f'<div class="log-entry"><span class="log-time">{ts}</span><span class="log-{lvl}">{msg}</span></div>'
    log_html += '</div>'
    log_ph.markdown(log_html, unsafe_allow_html=True)

    time.sleep(0.03)

driver_cam.release()
road_cam.release()
