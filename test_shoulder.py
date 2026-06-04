# /// script
# dependencies = [
#   "adafruit-circuitpython-servokit",
#   "RPi.GPIO",
# ]
# ///

from adafruit_servokit import ServoKit
import time

# Inicializácia
try:
    kit = ServoKit(channels=16)
    print("ServoKit inicializovaný.")
except Exception as e:
    print(f"Chyba: {e}")
    exit()

CH_A = 12
CH_B = 13

def test_servos():
    print(f"Nastavujem kanály {CH_A} a {CH_B} na stred (90°)...")
    kit.servo[CH_A].angle = 90
    kit.servo[CH_B].angle = 90
    time.sleep(2)

    print("Test pohybu: A ide na 110, B ide na 70 (synchrónne proti sebe)")
    kit.servo[CH_A].angle = 110
    kit.servo[CH_B].angle = 70
    time.sleep(1)

    print("Test pohybu: A ide na 70, B ide na 110")
    kit.servo[CH_A].angle = 70
    kit.servo[CH_B].angle = 110
    time.sleep(1)

    print("Návrat na stred (90°).")
    kit.servo[CH_A].angle = 90
    kit.servo[CH_B].angle = 90
    time.sleep(1)

    print("Uvoľňujem servá.")
    kit.servo[CH_A].angle = None
    kit.servo[CH_B].angle = None

if __name__ == "__main__":
    test_servos()
