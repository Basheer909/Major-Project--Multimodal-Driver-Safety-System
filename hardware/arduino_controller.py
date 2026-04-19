# hardware/arduino_controller.py
# Controls Arduino hardware via USB serial
# Controls: Buzzer, LEDs, Vibration Motor, External LED

import serial
import serial.tools.list_ports
import time

class ArduinoController:
    def __init__(self):
        self.arduino = None
        self.connected = False
        self.connect()

    def connect(self):
        """Automatically finds and connects to Arduino"""
        print("Looking for Arduino...")
        ports = serial.tools.list_ports.comports()

        for port in ports:
            if 'Arduino' in port.description or \
               'CH340' in port.description or \
               'USB Serial' in port.description or \
               'COM3' in port.device:
                try:
                    self.arduino = serial.Serial(
                        port.device,
                        9600,
                        timeout=1
                    )
                    time.sleep(2)
                    self.connected = True
                    print(f"Arduino connected on {port.device}! ✅")
                    return
                except:
                    continue

        print("Arduino not found! Running in simulation mode.")
        self.connected = False

    def send_command(self, command):
        """Sends command string to Arduino"""
        if self.connected and self.arduino:
            try:
                self.arduino.write(f"{command}\n".encode())
                print(f"Arduino: {command}")
            except:
                print(f"Simulation: {command}")
        else:
            print(f"Simulation: {command}")

    def trigger_alert(self, risk_level):
        """
        Triggers hardware alert based on risk level
        SAFE     -> Green LED only
        MEDIUM   -> Yellow LED + gentle beep
        HIGH     -> Red LED flash + buzzer
        CRITICAL -> Red LED rapid + buzzer 3x + vibration
        """
        self.send_command(risk_level)

    def trigger_external_led(self, mode):
        """
        Controls external LED on RC car rear
        PULSE -> slow pulsing (10-20 sec)
        SOLID -> solid red (20-30 sec)
        OFF   -> turn off
        """
        if mode == "PULSE":
            self.send_command("EXT_PULSE")
        elif mode == "SOLID":
            self.send_command("EXT_SOLID")
        elif mode == "OFF":
            self.send_command("EXT_OFF")

    def close(self):
        """Closes serial connection"""
        if self.arduino:
            self.arduino.close()
            print("Arduino disconnected.")


# Test Arduino controller
if __name__ == "__main__":
    print("Testing Arduino Controller...")
    controller = ArduinoController()

    print("\nTesting SAFE...")
    controller.trigger_alert("SAFE")
    time.sleep(1)

    print("Testing MEDIUM...")
    controller.trigger_alert("MEDIUM")
    time.sleep(1)

    print("Testing HIGH...")
    controller.trigger_alert("HIGH")
    time.sleep(1)

    print("Testing CRITICAL...")
    controller.trigger_alert("CRITICAL")
    time.sleep(1)

    print("\nTesting External LED PULSE...")
    controller.trigger_external_led("PULSE")
    time.sleep(2)

    print("Testing External LED SOLID...")
    controller.trigger_external_led("SOLID")
    time.sleep(2)

    print("Testing External LED OFF...")
    controller.trigger_external_led("OFF")

    controller.close()
    print("\nAll tests done! ✅")