# chatbot/llm_coach.py
# Dynamic Voice Coach
# Gives fresh advice every 8 seconds

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

last_spoken      = ""
last_spoken_time = 0


def speak(text):
    """Speaks text — repeats after 8 seconds"""
    global last_spoken, last_spoken_time

    current_time = time.time()

    # Allow same message after 8 seconds
    if text == last_spoken and \
       current_time - last_spoken_time < 8:
        return

    last_spoken      = text
    last_spoken_time = current_time

    print(f"Voice: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        pass


def get_road_alert(hazard):
    """Specific alert for each road hazard"""
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
            "Stop sign detected. Please slow down.",
        "Pothole":
            "Caution! Pothole detected ahead. Reduce speed now.",
        "None": ""
    }
    return alerts.get(hazard,
        f"Caution! {hazard} detected ahead. Stay alert.")


def get_driver_alert(driver_state):
    """Specific alert for each driver condition"""
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
        "Alert": ""
    }
    return alerts.get(driver_state,
        f"Alert! {driver_state} detected. Please focus on driving.")


def get_combined_alert(hazard, driver_state):
    """
    LLM generated combined alert
    when BOTH road and driver danger exist
    Generates fresh advice every call
    """
    try:
        # Add timestamp to get fresh response each time
        timestamp = int(time.time())

        prompt = f"""
        You are a car safety AI assistant.
        Give exactly 2 urgent sentences of safety advice.
        Situation at time {timestamp}:
        - Road hazard: {hazard}
        - Driver condition: {driver_state}
        Rules:
        - Be direct and urgent
        - Mention both the hazard and driver condition
        - Never suggest sudden braking
        - Vary your wording each time
        - Keep total under 30 words
        """

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user",
                       "content": prompt}],
            max_tokens=80,
            temperature=0.9  # Higher = more varied responses
        )

        advice = response.choices[0].message.content.strip()
        return advice

    except Exception as e:
        # Rotate through fallback messages
        fallbacks = [
            f"Critical danger! {hazard} ahead and driver is {driver_state}. Pull over immediately!",
            f"Emergency! {driver_state} driver with {hazard} on road. Take action now!",
            f"Danger! Both road hazard and driver impairment detected. Stop safely!",
        ]
        idx = int(time.time()) % len(fallbacks)
        return fallbacks[idx]


def give_voice_advice(risk_level, hazard, driver_state):
    """
    Main function called every 8 seconds
    Gives dynamic voice alert based on situation
    """
    message = ""

    if risk_level == "SAFE":
        return "All clear."

    elif risk_level == "MEDIUM":
        if hazard != "None" and driver_state == "Alert":
            message = get_road_alert(hazard)
        elif hazard == "None" and driver_state != "Alert":
            message = get_driver_alert(driver_state)
        else:
            message = get_road_alert(hazard)

    elif risk_level == "HIGH":
        if hazard != "None" and driver_state == "Alert":
            message = get_road_alert(hazard)
        elif hazard == "None" and driver_state != "Alert":
            message = get_driver_alert(driver_state)
        else:
            message = get_combined_alert(hazard, driver_state)

    elif risk_level == "CRITICAL":
        if hazard != "None" and driver_state != "Alert":
            message = get_combined_alert(hazard, driver_state)
        elif hazard != "None":
            message = get_road_alert(hazard)
        else:
            message = get_driver_alert(driver_state)

    if message:
        speak(message)

    return message


# Test
if __name__ == "__main__":
    print("Testing Dynamic Voice Coach...")
    print()

    print("Test 1 — Phone:")
    give_voice_advice("HIGH", "None", "Phone")
    time.sleep(6)

    print("Test 2 — Pedestrian:")
    give_voice_advice("HIGH", "Pedestrian", "Alert")
    time.sleep(6)

    print("Test 3 — Drowsy:")
    give_voice_advice("HIGH", "None", "Drowsy")
    time.sleep(6)

    print("Test 4 — CRITICAL both:")
    give_voice_advice("CRITICAL", "Pedestrian", "Drowsy")
    time.sleep(6)

    print("Test 5 — Same CRITICAL again:")
    give_voice_advice("CRITICAL", "Pedestrian", "Drowsy")
    time.sleep(6)

    print("Test 6 — Animal:")
    give_voice_advice("MEDIUM", "Animal", "Alert")
    time.sleep(6)

    print("All tests done!")