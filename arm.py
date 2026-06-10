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
    kit.servo[GRIP_CHANNEL].set_pulse_width_range(500, 2500) # Rozšírené na štandard pre väčší rozsah pohybu

# Bezpečné limity pre MG996R (prevencia bzučania a mechanického namáhania)
SAFE_MIN = 0 # Odomknuté na absolútne minimum
SAFE_MAX = 180 # Odomknuté na absolútne maximum

# Špecifické limity pre Gripper (aby sa nezasekával v extrémoch a vládal sa vrátiť)
# Obmedzené na 80 stupňov dráhy, pretože väčšina 3D tlačených mechanizmov sa pri viac ako 90° prevráti cez mŕtvy bod
GRIP_SAFE_MIN = 80 
GRIP_SAFE_MAX = 160

# Špecifické limity pre Lakeť (aby pri down pohybe netlačil do samotného ramena)
# Po zisteniach je smer opačný: menšie uhly idú dole, väčšie hore.
# Orezávame ho, aby pri zatváraní nenarazil do predlaktia.
ELBOW_SAFE_MIN = 0 
ELBOW_SAFE_MAX = 150 # Obmedzené z 180, aby sa nezapichol do ramena

# Predvolené (stredové/oddychové) uhly
default_angles = {
    ROTATE_CHANNEL: 100,
    SHOULDER_A: 10,  
    SHOULDER_B: 170, 
    ELBOW_CHANNEL: 0, # Zmenené na 0, čo je vystretá poloha v novom zrkadlovom nastavení
    WRIST_CHANNEL: 90,
    GRIP_CHANNEL: 120, # Nastavený na stred nového rozsahu
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
    curr = current_angles.get(ROTATE_CHANNEL, 90)
    move_servo(ROTATE_CHANNEL, curr - STEP) # Invertované

def rotate_right():
    curr = current_angles.get(ROTATE_CHANNEL, 90)
    move_servo(ROTATE_CHANNEL, curr + STEP) # Invertované

def arm_up():
    curr_shoulder = current_angles.get(SHOULDER_A, 10)
    move_shoulder(curr_shoulder - STEP) # Po výmene serv ide uhol pre UP nadol (smerom k 0)
    
    # Pridanie pohybu lakťa (inverzne k ramenu pre udržanie roviny)
    curr_elbow = current_angles.get(ELBOW_CHANNEL, 0)
    safe_elbow = max(ELBOW_SAFE_MIN, curr_elbow - STEP) # Smer dole (udržuje rovinu, keď rameno ide hore)
    move_servo(ELBOW_CHANNEL, safe_elbow)

def arm_down():
    curr_shoulder = current_angles.get(SHOULDER_A, 10)
    move_shoulder(curr_shoulder + STEP) # Po výmene serv ide uhol pre DOWN nahor (smerom k 180)
    
    # Pridanie pohybu lakťa (inverzne k ramenu pre udržanie roviny)
    curr_elbow = current_angles.get(ELBOW_CHANNEL, 0)
    safe_elbow = min(ELBOW_SAFE_MAX, curr_elbow + STEP) # Smer hore (udržuje rovinu, keď rameno ide dole)
    move_servo(ELBOW_CHANNEL, safe_elbow)

def elbow_up():
    curr = current_angles.get(ELBOW_CHANNEL, 0)
    safe_angle = max(ELBOW_SAFE_MIN, curr - STEP) # Pri lakti: menší uhol = hore
    move_servo(ELBOW_CHANNEL, safe_angle)

def elbow_down():
    curr = current_angles.get(ELBOW_CHANNEL, 0)
    safe_angle = min(ELBOW_SAFE_MAX, curr + STEP) # Väčší uhol = dole (rezeme na 150)
    move_servo(ELBOW_CHANNEL, safe_angle)

def wrist_up():
    curr = current_angles.get(WRIST_CHANNEL, 90)
    safe_angle = max(0, curr - STEP) # Extrémny limit, odomknuté z 5 na 0
    move_servo(WRIST_CHANNEL, safe_angle)

def wrist_down():
    curr = current_angles.get(WRIST_CHANNEL, 90)
    safe_angle = min(180, curr + STEP) # Extrémny limit, odomknuté z 175 na 180
    move_servo(WRIST_CHANNEL, safe_angle)

def grip_open():
    # Na tvrdo skok pre maximálny krútiaci moment, obmedzený na bezpečný limit 80, aby sa neprevrátil mechanizmus
    move_servo(GRIP_CHANNEL, GRIP_SAFE_MIN)

def grip_close():
    # Na tvrdo skok do zatvorenej polohy s maximálnou silou
    move_servo(GRIP_CHANNEL, GRIP_SAFE_MAX)

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
