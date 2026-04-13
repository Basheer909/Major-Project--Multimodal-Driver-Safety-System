# chatbot/llm_coach.py
# This is the voice coach of our project
# It uses Groq LLaMA 3 to generate
# personalised safety advice
# and speaks it through laptop speakers

from groq import Groq
import pyttsx3
import time
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Setup Groq client
client = Groq(api_key=GROQ_API_KEY)

# Setup text to speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)


def speak(text):
    """Speaks text through laptop speakers"""
    print(f"Speaking: {text}")
    engine.say(text)
    engine.runAndWait()


def get_road_alert(hazard):
    """Returns specific alert based on road hazard"""
    road_alerts = {
        "Pedestrian": "Warning! Pedestrian ahead. Slow down immediately.",
        "Pothole":    "Caution! Pothole ahead. Reduce speed now.",
        "Animal":     "Warning! Animal on road ahead. Slow down.",
        "Vehicle":    "Caution! Vehicle detected ahead. Maintain distance.",
        "Debris":     "Warning! Road debris ahead. Drive carefully.",
        "None":       ""
    }
    return road_alerts.get(hazard, f"Caution! {hazard} detected ahead.")


def get_driver_alert(driver_state):
    """Returns specific alert based on driver condition"""
    driver_alerts = {
        "Drowsy":     "Alert! You are drowsy. Please wake up and stay focused.",
        "Phone":      "Warning! Put your phone down. Focus on the road.",
        "Angry":      "Caution! You seem stressed. Take a deep breath and calm down.",
        "Fearful":    "Stay calm. Focus on the road ahead.",
        "Distracted": "Alert! You are distracted. Keep your eyes on the road.",
        "Alert":      ""
    }
    return driver_alerts.get(driver_state, f"Alert! {driver_state} detected.")


def get_combined_alert(hazard, driver_state):
    """
    Returns combined alert using Groq LLaMA 3
    when both road and driver danger exist
    """
    try:
        prompt = f"""
        You are a car safety AI assistant.
        Give exactly 2 short sentences of safety advice.
        Current situation:
        - Road hazard: {hazard}
        - Driver state: {driver_state}
        Rules:
        - Be direct and urgent
        - Mention both the hazard and driver state
        - Never suggest sudden braking
        - Keep it under 25 words total
        """

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60
        )

        advice = response.choices[0].message.content.strip()
        return advice

    except Exception as e:
        return f"Critical danger! {hazard} ahead and driver is {driver_state}. Pull over immediately!"


def give_voice_advice(risk_level, hazard, driver_state):
    """
    Main function called every few seconds
    Gives appropriate voice alert based on situation
    """
    message = ""

    if risk_level == "SAFE":
        return "All clear."

    elif risk_level == "MEDIUM":
        if hazard != "None":
            message = get_road_alert(hazard)
        elif driver_state != "Alert":
            message = get_driver_alert(driver_state)

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


# Test the voice coach
if __name__ == "__main__":
    print("Testing Voice Coach...")
    print()

    print("Test 1 - Pothole only:")
    give_voice_advice("HIGH", "Pothole", "Alert")
    time.sleep(4)

    print("Test 2 - Drowsy driver:")
    give_voice_advice("HIGH", "None", "Drowsy")
    time.sleep(4)

    print("Test 3 - Phone usage:")
    give_voice_advice("HIGH", "None", "Phone")
    time.sleep(4)

    print("Test 4 - CRITICAL both dangers:")
    give_voice_advice("CRITICAL", "Pedestrian", "Drowsy")
    time.sleep(5)

    print("All tests done!")