# chatbot/llm_coach.py
# Improved Voice Coach with specific messages
# for every detection scenario

from groq import Groq
import pyttsx3
import time
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# Track last spoken message to avoid repetition
last_spoken = ""
last_spoken_time = 0
REPEAT_COOLDOWN = 8  # seconds before repeating same message

def speak(text):
    """Speaks text through laptop speakers"""
    global last_spoken, last_spoken_time

    current_time = time.time()

    # Don't repeat same message within cooldown
    if text == last_spoken and \
       current_time - last_spoken_time < REPEAT_COOLDOWN:
        return

    last_spoken = text
    last_spoken_time = current_time

    print(f"Voice: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        pass


# ═══════════════════════════════════
# SPECIFIC ROAD ALERTS
# ═══════════════════════════════════

def get_road_alert(hazard):
    """Returns specific alert for each road hazard"""
    alerts = {
        "Pedestrian":
            "Warning! Pedestrian detected ahead. Please slow down immediately.",

        "Animal":
            "Caution! Animal on the road ahead. Reduce your speed now.",

        "Road Debris":
            "Warning! Road debris detected ahead. Drive carefully.",

        "Vehicle":
            "Caution! Vehicle detected ahead. Maintain safe distance.",

        "Traffic Signal":
            "Traffic signal ahead. Be prepared to stop.",

        "Stop Sign":
            "Stop sign detected ahead. Please slow down.",

        "Pothole":
            "Caution! Pothole detected ahead. Reduce speed now.",

        "None":
            ""
    }
    return alerts.get(hazard,
        f"Caution! {hazard} detected ahead. Stay alert.")


# ═══════════════════════════════════
# SPECIFIC DRIVER ALERTS
# ═══════════════════════════════════

def get_driver_alert(driver_state):
    """Returns specific alert for each driver condition"""
    alerts = {
        "Drowsy":
            "Alert! You are feeling drowsy. Please wake up and focus on the road.",

        "Phone":
            "Warning! Please put your phone down. Using phone while driving is dangerous.",

        "Angry":
            "Caution! You seem angry. Take a deep breath and calm down before driving.",

        "Fear":
            "Stay calm! Focus on the road ahead. You are in control.",

        "Disgust":
            "Please focus on the road. Distracted driving is dangerous.",

        "Earphone":
            "Warning! Remove your earphones. You need to hear road sounds while driving.",

        "Alert":
            ""
    }
    return alerts.get(driver_state,
        f"Alert! {driver_state} detected. Please focus on driving.")


# ═══════════════════════════════════
# COMBINED CRITICAL ALERT
# ═══════════════════════════════════

def get_combined_alert(hazard, driver_state):
    """
    Returns combined alert when BOTH road and
    driver danger exist simultaneously
    Uses Groq LLaMA 3 for personalised advice
    """
    try:
        prompt = f"""
        You are a car safety AI assistant.
        Give exactly 2 urgent sentences of safety advice.
        Current situation:
        - Road hazard: {hazard}
        - Driver condition: {driver_state}
        Rules:
        - Be direct and urgent
        - Mention both the hazard and driver condition
        - Never suggest sudden braking
        - Keep total under 30 words
        """

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user",
                       "content": prompt}],
            max_tokens=80
        )

        advice = response.choices[0].message.content.strip()
        return advice

    except Exception as e:
        # Fallback if Groq fails
        road_msg   = get_road_alert(hazard)
        driver_msg = get_driver_alert(driver_state)
        return f"Critical danger! {road_msg} Also, {driver_msg}"


# ═══════════════════════════════════
# MAIN VOICE ADVICE FUNCTION
# ═══════════════════════════════════

def give_voice_advice(risk_level, hazard, driver_state):
    """
    Main function called every 5 seconds
    Gives specific voice alert based on situation
    """
    message = ""

    if risk_level == "SAFE":
        # No alert for safe
        return "All clear."

    elif risk_level == "MEDIUM":
        # Single danger — specific message
        if hazard != "None" and driver_state == "Alert":
            message = get_road_alert(hazard)
        elif hazard == "None" and driver_state != "Alert":
            message = get_driver_alert(driver_state)
        else:
            message = get_road_alert(hazard)

    elif risk_level == "HIGH":
        # Significant danger — specific message
        if hazard != "None" and driver_state == "Alert":
            message = get_road_alert(hazard)
        elif hazard == "None" and driver_state != "Alert":
            message = get_driver_alert(driver_state)
        else:
            # Both exist — combined message
            message = get_combined_alert(
                hazard, driver_state)

    elif risk_level == "CRITICAL":
        # Both dangers — LLM combined message
        if hazard != "None" and driver_state != "Alert":
            message = get_combined_alert(
                hazard, driver_state)
        elif hazard != "None":
            message = get_road_alert(hazard)
        else:
            message = get_driver_alert(driver_state)

    if message:
        speak(message)

    return message


# ═══════════════════════════════════
# TEST
# ═══════════════════════════════════

if __name__ == "__main__":
    print("Testing Voice Coach...")
    print()

    print("Test 1 — Phone detected:")
    give_voice_advice("HIGH", "None", "Phone")
    time.sleep(5)

    print("Test 2 — Pedestrian on road:")
    give_voice_advice("HIGH", "Pedestrian", "Alert")
    time.sleep(5)

    print("Test 3 — Animal on road:")
    give_voice_advice("MEDIUM", "Animal", "Alert")
    time.sleep(5)

    print("Test 4 — Drowsy driver:")
    give_voice_advice("HIGH", "None", "Drowsy")
    time.sleep(5)

    print("Test 5 — Earphone detected:")
    give_voice_advice("MEDIUM", "None", "Earphone")
    time.sleep(5)

    print("Test 6 — CRITICAL both dangers:")
    give_voice_advice("CRITICAL", "Pedestrian", "Drowsy")
    time.sleep(6)

    print("Test 7 — Road debris:")
    give_voice_advice("HIGH", "Road Debris", "Alert")
    time.sleep(5)

    print("All tests done!")