# /// script
# dependencies = [
#   "adafruit-circuitpython-servokit",
# ]
# ///

from adafruit_servokit import ServoKit
import time
import logging

logger = logging.getLogger(__name__)

# Singleton inštancia pre celého robota
try:
    kit = ServoKit(channels=16)
except Exception as e:
    logger.error(f"Nepodarilo sa inicializovať ServoKit: {e}")
    kit = None

# Kanály
ROTATE_CHANNEL = 11
ARM1_CHANNEL = 12
ARM2_CHANNEL = 13
ARM3_CHANNEL = 14
GRIP_CHANNEL = 15
PAN_CHANNEL = 9
TILT_CHANNEL = 8

# Nastavenie rozsahov
if kit:
    kit.servo[ROTATE_CHANNEL].set_pulse_width_range(800, 2550)
    kit.servo[ARM2_CHANNEL].set_pulse_width_range(500, 2550)
    kit.servo[ARM3_CHANNEL].set_pulse_width_range(500, 2550)
    kit.servo[GRIP_CHANNEL].set_pulse_width_range(600, 1900)

# Bezpečné limity pre MG996R (prevencia bzučania a mechanického namáhania)
SAFE_MIN = 5
SAFE_MAX = 175

# Predvolené (stredové) uhly - upravené podľa tvojej kalibrácie
default_angles = {
    ROTATE_CHANNEL: 100,  # Tvoj "rovno" stred
    ARM1_CHANNEL: 180,
    ARM2_CHANNEL: 0,
    ARM3_CHANNEL: 180,
    GRIP_CHANNEL: 90,
    PAN_CHANNEL: 90,
    TILT_CHANNEL: 90
}

def move_servo(channel, angle):
    """
    Nastaví servo na uhol s automatickým strážením bezpečných limitov.
    """
    if kit:
        # Aplikujeme bezpečné limity 5 - 175
        safe_angle = max(SAFE_MIN, min(SAFE_MAX, angle))
        kit.servo[channel].angle = safe_angle

def initialize_arm():
    if not kit: return
    for ch, ang in default_angles.items():
        move_servo(ch, ang)

def release_servos():
    if not kit: return
    for i in range(16):
        kit.servo[i].angle = None

def rotate_left():
    curr = kit.servo[ROTATE_CHANNEL].angle or 90
    move_servo(ROTATE_CHANNEL, curr + 10)

def rotate_right():
    curr = kit.servo[ROTATE_CHANNEL].angle or 90
    move_servo(ROTATE_CHANNEL, curr - 10)

def arm_up():
    for ch in [ARM1_CHANNEL, ARM2_CHANNEL, ARM3_CHANNEL]:
        curr = kit.servo[ch].angle or 90
        move_servo(ch, curr - 10)

def arm_down():
    for ch in [ARM1_CHANNEL, ARM2_CHANNEL, ARM3_CHANNEL]:
        curr = kit.servo[ch].angle or 90
        move_servo(ch, curr + 10)

def grip_open():
    curr = kit.servo[GRIP_CHANNEL].angle or 90
    move_servo(GRIP_CHANNEL, curr + 10)

def grip_close():
    curr = kit.servo[GRIP_CHANNEL].angle or 90
    move_servo(GRIP_CHANNEL, curr - 10)

# Proxy funkcie pre kameru (aby sme nemuseli prepisovať app.py)
def cam_left():
    curr = kit.servo[PAN_CHANNEL].angle or 90
    move_servo(PAN_CHANNEL, curr + 5)

def cam_right():
    curr = kit.servo[PAN_CHANNEL].angle or 90
    move_servo(PAN_CHANNEL, curr - 5)

def cam_up():
    curr = kit.servo[TILT_CHANNEL].angle or 90
    move_servo(TILT_CHANNEL, curr - 5)

def cam_down():
    curr = kit.servo[TILT_CHANNEL].angle or 90
    move_servo(TILT_CHANNEL, curr + 5)

def cleanup():
    release_servos()
