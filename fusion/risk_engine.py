# fusion/risk_engine.py
# This is the brain of our project
# It combines road score and driver score
# and calculates the final risk level

def calculate_risk(road_score, driver_score):
    """
    Combines road and driver scores
    Applies 1.5x compounding when both exist
    Returns final score and risk level
    """

    # Apply compounding formula
    if road_score > 0 and driver_score > 0:
        # BOTH dangers exist — multiply by 1.5
        raw_score = (road_score + driver_score) * 1.5
    else:
        # Only one danger — no compounding
        raw_score = road_score + driver_score

    # Cap at 100
    final_score = min(100, int(raw_score))

    # Determine risk level
    if final_score <= 25:
        level = "SAFE"
    elif final_score <= 50:
        level = "MEDIUM"
    elif final_score <= 75:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return final_score, level


def get_alert_message(level, hazard, driver_state):
    """
    Returns alert message based on risk level
    Used as fallback when Groq API unavailable
    """
    messages = {
        "SAFE":     "All clear. Drive safely.",
        "MEDIUM":   f"Caution! {hazard} detected. Stay alert.",
        "HIGH":     f"Warning! {hazard} ahead. {driver_state}. Slow down!",
        "CRITICAL": f"CRITICAL DANGER! {hazard} ahead and {driver_state}. Pull over immediately!"
    }
    return messages[level]


# Test the engine
if __name__ == "__main__":
    print("Testing Risk Fusion Engine...")
    print()

    score, level = calculate_risk(70, 0)
    print(f"Test 1 - Only road danger:")
    print(f"Road=70, Driver=0 -> Score={score}, Level={level}")
    print()

    score, level = calculate_risk(0, 60)
    print(f"Test 2 - Only driver danger:")
    print(f"Road=0, Driver=60 -> Score={score}, Level={level}")
    print()

    score, level = calculate_risk(70, 60)
    print(f"Test 3 - Both dangers (compounding):")
    print(f"Road=70, Driver=60 -> (70+60)x1.5={int((70+60)*1.5)} -> capped at {score}, Level={level}")
    print()

    score, level = calculate_risk(100, 100)
    print(f"Test 4 - Maximum danger:")
    print(f"Road=100, Driver=100 -> Score={score}, Level={level}")