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
ROTATE_CHANNEL = 8
SHOULDER_A = 10
SHOULDER_B = 11
ELBOW_CHANNEL = 12
WRIST_CHANNEL = 13
GRIP_CHANNEL = 15
PAN_CHANNEL = 9
TILT_CHANNEL = 7 # Posunuté z 8

# Nastavenie rozsahov
if kit:
    kit.servo[ROTATE_CHANNEL].set_pulse_width_range(800, 2550)
    kit.servo[SHOULDER_A].set_pulse_width_range(500, 2550)
    kit.servo[SHOULDER_B].set_pulse_width_range(500, 2550)
    kit.servo[ELBOW_CHANNEL].set_pulse_width_range(500, 2550)
    kit.servo[WRIST_CHANNEL].set_pulse_width_range(500, 2550)
    kit.servo[GRIP_CHANNEL].set_pulse_width_range(500, 2550)

# Bezpečné limity pre MG996R (prevencia bzučania a mechanického namáhania)
SAFE_MIN = 5
SAFE_MAX = 175

# Predvolené (stredové/oddychové) uhly
default_angles = {
    ROTATE_CHANNEL: 100,
    SHOULDER_A: 170, 
    SHOULDER_B: 10,  
    ELBOW_CHANNEL: 180,
    WRIST_CHANNEL: 90,
    GRIP_CHANNEL: 90,
    PAN_CHANNEL: 90,
    TILT_CHANNEL: 90
}

# Pamäť poslednej polohy (aby sme po release nezačínali vždy od 90)
current_angles = default_angles.copy()

def move_servo(channel, angle):
    """
    Nastaví servo na uhol s automatickým strážením bezpečných limitov.
    """
    if kit:
        safe_angle = max(SAFE_MIN, min(SAFE_MAX, angle))
        kit.servo[channel].angle = safe_angle
        current_angles[channel] = safe_angle # Uložíme do pamäte

def move_shoulder(angle):
    """
    Ovláda obe ramenové servá naraz (jedno invertovane).
    """
    safe_angle = max(SAFE_MIN, min(SAFE_MAX, angle))
    move_servo(SHOULDER_A, safe_angle)
    move_servo(SHOULDER_B, 180 - safe_angle)

def initialize_arm():
    # Už neposielame tvrdé uhly pri štarte. 
    # Necháme rameno uvoľnené (limp), kým používateľ nepošle prvý príkaz.
    pass

def release_servos():
    if not kit: return
    for i in range(16):
        kit.servo[i].angle = None
    
    # Odhad pádu ramena po vypnutí serv (Workaround pre gravitáciu)
    # Ak je kolmo (okolo 90°), predpokladáme, že zostane stáť.
    # Ak je naklonené dozadu, padne na chrbát (170°).
    # Ak je naklonené dopredu, padne na predný doraz (napr. 30°).
    shoulder = current_angles.get(SHOULDER_A, 170)
    if shoulder > 105:
        current_angles[SHOULDER_A] = 170
        current_angles[SHOULDER_B] = 180 - 170
        logger.info("Rameno uvoľnené. Odhad polohy: Padlo dozadu (170°).")
    elif shoulder < 75:
        current_angles[SHOULDER_A] = 30 # Uprav tento uhol podľa fyzického predného dorazu
        current_angles[SHOULDER_B] = 180 - 30
        logger.info("Rameno uvoľnené. Odhad polohy: Padlo dopredu (30°).")
    else:
        logger.info("Rameno uvoľnené. Odhad polohy: Zostalo stáť kolmo.")

# Krok pre plynulejší a pomalší pohyb
STEP = 1
GRIP_STEP = 3 # Znížené z 5 na 3, aby to nebolo až také trhavé, ale stále prekonalo mŕtve pásmo

def rotate_left():
    curr = current_angles.get(ROTATE_CHANNEL, 90)
    move_servo(ROTATE_CHANNEL, curr - STEP) # Invertované

def rotate_right():
    curr = current_angles.get(ROTATE_CHANNEL, 90)
    move_servo(ROTATE_CHANNEL, curr + STEP) # Invertované

def arm_up():
    curr_shoulder = current_angles.get(SHOULDER_A, 170)
    move_shoulder(curr_shoulder + STEP) # Invertované (hore ide uhol nahor)
    
    # Pridanie pohybu lakťa (inverzne k ramenu pre udržanie roviny)
    curr_elbow = current_angles.get(ELBOW_CHANNEL, 180)
    move_servo(ELBOW_CHANNEL, curr_elbow + STEP) # Opravená inverzia lakťa

def arm_down():
    curr_shoulder = current_angles.get(SHOULDER_A, 170)
    move_shoulder(curr_shoulder - STEP) # Invertované
    
    # Pridanie pohybu lakťa (inverzne k ramenu pre udržanie roviny)
    curr_elbow = current_angles.get(ELBOW_CHANNEL, 180)
    move_servo(ELBOW_CHANNEL, curr_elbow - STEP) # Opravená inverzia lakťa

def elbow_up():
    curr = current_angles.get(ELBOW_CHANNEL, 180)
    move_servo(ELBOW_CHANNEL, curr - STEP) # Invertované

def elbow_down():
    curr = current_angles.get(ELBOW_CHANNEL, 180)
    move_servo(ELBOW_CHANNEL, curr + STEP) # Invertované

def wrist_up():
    curr = current_angles.get(WRIST_CHANNEL, 90)
    move_servo(WRIST_CHANNEL, curr - STEP)

def wrist_down():
    curr = current_angles.get(WRIST_CHANNEL, 90)
    move_servo(WRIST_CHANNEL, curr + STEP)

def grip_open():
    curr = current_angles.get(GRIP_CHANNEL, 90)
    move_servo(GRIP_CHANNEL, curr - GRIP_STEP) # Vymenené: teraz zmenšuje uhol

def grip_close():
    curr = current_angles.get(GRIP_CHANNEL, 90)
    move_servo(GRIP_CHANNEL, curr + GRIP_STEP) # Vymenené: teraz zväčšuje uhol

# Proxy funkcie pre kameru (aby sme nemuseli prepisovať app.py)
def cam_left():
    curr = current_angles.get(PAN_CHANNEL, 90)
    move_servo(PAN_CHANNEL, curr + STEP)

def cam_right():
    curr = current_angles.get(PAN_CHANNEL, 90)
    move_servo(PAN_CHANNEL, curr - STEP)

def cam_up():
    curr = current_angles.get(TILT_CHANNEL, 90)
    move_servo(TILT_CHANNEL, curr - STEP)

def cam_down():
    curr = current_angles.get(TILT_CHANNEL, 90)
    move_servo(TILT_CHANNEL, curr + STEP)

def park_arm():
    """
    Pomaly zaparkuje rameno do oddychovej polohy (170°) pred vypnutím.
    """
    import time
    logger.info("Parkujem rameno do oddychovej polohy...")
    curr_shoulder = current_angles.get(SHOULDER_A, 170)
    target = 170
    
    if curr_shoulder < target:
        for angle in range(int(curr_shoulder), target + 1, 1):
            move_shoulder(angle)
            time.sleep(0.02) # Pomalý pohyb
    elif curr_shoulder > target:
        for angle in range(int(curr_shoulder), target - 1, -1):
            move_shoulder(angle)
            time.sleep(0.02)
            
    logger.info("Rameno zaparkované.")

def cleanup():
    park_arm()
    release_servos()
