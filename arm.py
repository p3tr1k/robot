# /// script
# dependencies = [
#   "adafruit-circuitpython-servokit",
# ]
# ///

from adafruit_servokit import ServoKit
import time
import logging
import threading

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
PAN_CHANNEL = 0
TILT_CHANNEL = 1 # Opravene podla realneho spravania

# Nastavenie rozsahov
if kit:
    kit.servo[ROTATE_CHANNEL].set_pulse_width_range(800, 2550)
    kit.servo[SHOULDER_A].set_pulse_width_range(500, 2550)
    kit.servo[SHOULDER_B].set_pulse_width_range(500, 2550)
    kit.servo[ELBOW_CHANNEL].set_pulse_width_range(500, 2550)
    kit.servo[WRIST_CHANNEL].set_pulse_width_range(500, 2550)
    kit.servo[GRIP_CHANNEL].set_pulse_width_range(500, 2500) # Rozšírené na štandard pre väčší rozsah pohybu
    kit.servo[PAN_CHANNEL].set_pulse_width_range(500, 2500)
    kit.servo[TILT_CHANNEL].set_pulse_width_range(500, 2500)

# Bezpečné limity pre MG996R (prevencia bzučania a mechanického namáhania)
SAFE_MIN = 0 # Odomknuté na absolútne minimum
SAFE_MAX = 180 # Odomknuté na absolútne maximum

# Špecifické limity pre Gripper (aby sa nezasekával v extrémoch a vládal sa vrátiť)
# Obmedzené na 80 stupňov dráhy, pretože väčšina 3D tlačených mechanizmov sa pri viac ako 90° prevráti cez mŕtvy bod
GRIP_SAFE_MIN = 80 
GRIP_SAFE_MAX = 150 # Zvýšené zo 140 na 150 pre pevnejšie zovretie

# Špecifické limity pre Lakeť (aby pri down pohybe netlačil do samotného ramena)
# 180 je horná (vystretá) poloha. Dolnú polohu obmedzíme, aby neschádzal príliš nízko.
ELBOW_SAFE_MIN = 30 # Upraviteľný limit, aby lakeť neschádzal príliš dole
ELBOW_SAFE_MAX = 180

# Špecifické limity pre Rotáciu základne (aby nenarážalo do kamery na chrbte)
ROTATE_SAFE_MIN = 90 # Ešte viac skrátené o 15 stupňov doľava (na 90)
ROTATE_SAFE_MAX = 155 # Posunuté o 10 stupňov doprava

# Limity pre rotáciu kamery (PAN) - obmedzené na 110 stupňov, posunuté o 10° vľavo
PAN_SAFE_MIN = 45 # (100 - 55) Zmenšili sme dosah doprava
PAN_SAFE_MAX = 155 # (100 + 55) Zväčšili sme dosah doľava

# Predvolené (stredové/oddychové) uhly
default_angles = {
    ROTATE_CHANNEL: 100,
    SHOULDER_A: 10,  # Zmenené z 170 na 10 kvôli prehodeniu ľavého/pravého serva
    SHOULDER_B: 170, # Zmenené z 10 na 170 
    ELBOW_CHANNEL: 180,
    WRIST_CHANNEL: 90,
    GRIP_CHANNEL: 120, # Nastavený na stred nového rozsahu
    PAN_CHANNEL: 100,  # Posunutý stred o 10° doľava kvôli mechanickému posunu
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
    # Zabezpečíme, že po štarte (alebo reštarte aplikácie) sa do serv neposiela žiadny "duch" PWM signál, 
    # ktorý by ich mohol držať v napätí a prehrievať, kým užívateľ nevydá prvý príkaz.
    logger.info("Inicializujem rameno: Vypínam všetky PWM signály (Release).")
    release_servos()

def release_servos():
    if not kit: return
    logger.info("Uvoľňujem všetky servá (vypínam PWM)...")
    for i in range(16):
        try:
            kit.servo[i].angle = None
            time.sleep(0.005) # Malá pauza pre zbernicu
        except Exception as e:
            logger.error(f"Chyba pri uvoľňovaní kanálu {i}: {e}")
    
    # Odhad pádu ramena po vypnutí serv (Workaround pre gravitáciu)
    # Ak je kolmo (okolo 90°), predpokladáme, že zostane stáť.
    # Ak je naklonené dozadu, padne na chrbát (170°).
    # Ak je naklonené dopredu, padne na predný doraz (napr. 30°).
    shoulder = current_angles.get(SHOULDER_A, 10)
    if shoulder > 105:
        current_angles[SHOULDER_A] = 150 # Predný doraz (zrkadlovo k pôvodným 30)
        current_angles[SHOULDER_B] = 180 - 150
        logger.info("Rameno uvoľnené. Odhad polohy: Padlo dopredu (150°).")
    elif shoulder < 75:
        current_angles[SHOULDER_A] = 10 # Zadný doraz/chrbát (zrkadlovo k 170)
        current_angles[SHOULDER_B] = 180 - 10
        logger.info("Rameno uvoľnené. Odhad polohy: Padlo dozadu (10°).")
    else:
        logger.info("Rameno uvoľnené. Odhad polohy: Zostalo stáť kolmo.")

# Krok pre plynulejší a pomalší pohyb
STEP = 2 # Zvýšené z 1 na 2 kvôli pomalšiemu intervalu na webe (100ms)
GRIP_STEP = 5 # Umiernený krok, 10 bolo po odstránení lagov priveľa

def rotate_left():
    curr = current_angles.get(ROTATE_CHANNEL, 100)
    safe_angle = max(ROTATE_SAFE_MIN, curr - STEP)
    move_servo(ROTATE_CHANNEL, safe_angle)

def rotate_right():
    curr = current_angles.get(ROTATE_CHANNEL, 100)
    safe_angle = min(ROTATE_SAFE_MAX, curr + STEP)
    move_servo(ROTATE_CHANNEL, safe_angle)

def arm_up():
    curr_shoulder = current_angles.get(SHOULDER_A, 10)
    move_shoulder(curr_shoulder - STEP) # Po výmene serv ide uhol pre UP nadol (smerom k 0)
    
    # Pridanie pohybu lakťa (inverzne k ramenu pre udržanie roviny)
    curr_elbow = current_angles.get(ELBOW_CHANNEL, 180)
    safe_elbow = min(ELBOW_SAFE_MAX, curr_elbow + STEP)
    move_servo(ELBOW_CHANNEL, safe_elbow)

def arm_down():
    curr_shoulder = current_angles.get(SHOULDER_A, 10)
    move_shoulder(curr_shoulder + STEP) # Po výmene serv ide uhol pre DOWN nahor (smerom k 180)
    
    # Pridanie pohybu lakťa (inverzne k ramenu pre udržanie roviny)
    curr_elbow = current_angles.get(ELBOW_CHANNEL, 180)
    safe_elbow = max(ELBOW_SAFE_MIN, curr_elbow - STEP)
    move_servo(ELBOW_CHANNEL, safe_elbow)

def elbow_up():
    curr = current_angles.get(ELBOW_CHANNEL, 180)
    safe_angle = max(ELBOW_SAFE_MIN, curr - STEP) # Zamedzenie prejdenia za limit
    move_servo(ELBOW_CHANNEL, safe_angle)

def elbow_down():
    curr = current_angles.get(ELBOW_CHANNEL, 180)
    safe_angle = min(ELBOW_SAFE_MAX, curr + STEP) # Zamedzenie prejdenia za limit
    move_servo(ELBOW_CHANNEL, safe_angle)

def wrist_up():
    curr = current_angles.get(WRIST_CHANNEL, 90)
    safe_angle = max(0, curr - STEP) # Extrémny limit, odomknuté z 5 na 0
    move_servo(WRIST_CHANNEL, safe_angle)

def wrist_down():
    curr = current_angles.get(WRIST_CHANNEL, 90)
    safe_angle = min(180, curr + STEP) # Extrémny limit, odomknuté z 175 na 180
    move_servo(WRIST_CHANNEL, safe_angle)

grip_timer = None

def _auto_release_gripper():
    if not kit: return
    try:
        kit.servo[GRIP_CHANNEL].angle = None
        logger.info("Gripper automaticky uvoľnený (PWM vypnuté).")
    except Exception as e:
        logger.error(f"Chyba pri automatickom uvoľňovaní grippera: {e}")

def schedule_gripper_release():
    global grip_timer
    if grip_timer:
        grip_timer.cancel()
    # Nastavíme časovač na 0.5 sekundy. Kým užívateľ drží tlačidlo, časovač sa neustále posúva.
    # Až keď tlačidlo pustí, ubehne 0.5s a servo sa uvoľní.
    grip_timer = threading.Timer(0.5, _auto_release_gripper)
    grip_timer.start()

def grip_open():
    # Na tvrdo skok pre maximálny krútiaci moment, obmedzený na bezpečný limit 80, aby sa neprevrátil mechanizmus
    move_servo(GRIP_CHANNEL, GRIP_SAFE_MIN)
    schedule_gripper_release()

def grip_close():
    # Na tvrdo skok do zatvorenej polohy s maximálnou silou
    move_servo(GRIP_CHANNEL, GRIP_SAFE_MAX)
    schedule_gripper_release()

cam_timer = None

def _auto_release_camera():
    if not kit: return
    try:
        kit.servo[PAN_CHANNEL].angle = None
        kit.servo[TILT_CHANNEL].angle = None
        logger.info("Servá kamery automaticky uvoľnené proti traseniu.")
    except Exception as e:
        logger.error(f"Chyba pri uvoľňovaní kamery: {e}")

def schedule_camera_release():
    global cam_timer
    if cam_timer:
        cam_timer.cancel()
    # 0.3 sekundy po uvoľnení tlačidla sa vypne PWM signál do serva
    cam_timer = threading.Timer(0.3, _auto_release_camera)
    cam_timer.start()

# Proxy funkcie pre kameru (aby sme nemuseli prepisovať app.py)
def cam_left():
    curr = current_angles.get(PAN_CHANNEL, 100)
    safe_angle = min(PAN_SAFE_MAX, curr + STEP)
    move_servo(PAN_CHANNEL, safe_angle)
    schedule_camera_release()

def cam_right():
    curr = current_angles.get(PAN_CHANNEL, 100)
    safe_angle = max(PAN_SAFE_MIN, curr - STEP)
    move_servo(PAN_CHANNEL, safe_angle)
    schedule_camera_release()

def cam_up():
    curr = current_angles.get(TILT_CHANNEL, 90)
    move_servo(TILT_CHANNEL, curr - STEP)
    schedule_camera_release()

def cam_down():
    curr = current_angles.get(TILT_CHANNEL, 90)
    move_servo(TILT_CHANNEL, curr + STEP)
    schedule_camera_release()

def park_arm():
    """
    Pomaly zaparkuje rameno, lakeť a zápästie do oddychovej polohy pred vypnutím.
    """
    import time
    logger.info("Parkujem celé rameno do oddychovej polohy...")
    
    targets = {
        SHOULDER_A: default_angles[SHOULDER_A],
        ELBOW_CHANNEL: default_angles[ELBOW_CHANNEL],
        WRIST_CHANNEL: default_angles[WRIST_CHANNEL]
    }
    
    moving = True
    while moving:
        moving = False
        
        # Rameno (Shoulder)
        curr_s = current_angles.get(SHOULDER_A, targets[SHOULDER_A])
        if int(curr_s) < targets[SHOULDER_A]:
            move_shoulder(curr_s + 1)
            moving = True
        elif int(curr_s) > targets[SHOULDER_A]:
            move_shoulder(curr_s - 1)
            moving = True
            
        # Lakeť (Elbow)
        curr_e = current_angles.get(ELBOW_CHANNEL, targets[ELBOW_CHANNEL])
        if int(curr_e) < targets[ELBOW_CHANNEL]:
            move_servo(ELBOW_CHANNEL, curr_e + 1)
            moving = True
        elif int(curr_e) > targets[ELBOW_CHANNEL]:
            move_servo(ELBOW_CHANNEL, curr_e - 1)
            moving = True
            
        # Zápästie (Wrist)
        curr_w = current_angles.get(WRIST_CHANNEL, targets[WRIST_CHANNEL])
        if int(curr_w) < targets[WRIST_CHANNEL]:
            move_servo(WRIST_CHANNEL, curr_w + 1)
            moving = True
        elif int(curr_w) > targets[WRIST_CHANNEL]:
            move_servo(WRIST_CHANNEL, curr_w - 1)
            moving = True
            
        if moving:
            time.sleep(0.02)
            
    logger.info("Rameno úspešne zaparkované.")

def cleanup():
    # park_arm() # Nateraz ZAKÁZANÉ. Spôsobuje mechanické kolízie pri vypínaní.
    release_servos()
