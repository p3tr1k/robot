from adafruit_servokit import ServoKit
import time

# Inicializácia PCA9685
kit = ServoKit(channels=16)


# Kanály pre jednotlivé servomotory
ROTATE_CHANNEL = 11 # Otáčanie ruky
ARM1_CHANNEL = 12 # Prvá časť ruky hore/dolu
ARM2_CHANNEL = 13 # Druhá časť ruky hore/dolu
ARM3_CHANNEL = 14 # Tretia časť ruky hore/dolu
GRIP_CHANNEL = 15 # Uchop ruky

PAN_CHANNEL = 9    # Otáčanie kamery doľava/doprava
TILT_CHANNEL = 8   # Nakláňanie kamery hore/dolu

kit.servo[ROTATE_CHANNEL].set_pulse_width_range(800, 2550)
kit.servo[ARM2_CHANNEL].set_pulse_width_range(500, 2550)
kit.servo[ARM3_CHANNEL].set_pulse_width_range(500, 2550)
kit.servo[GRIP_CHANNEL].set_pulse_width_range(600, 1900)


default_angles = {
    ROTATE_CHANNEL: 90,
    ARM1_CHANNEL: 180,
    ARM2_CHANNEL: 0,
    ARM3_CHANNEL: 180,
    GRIP_CHANNEL: 90,
    PAN_CHANNEL: 90,
    TILT_CHANNEL: 90

}

def initialize_arm():
    """
    Inicializuje nastavenia pre servomotory pomaly.
    """
    def smooth_move(channel, target_angle, step=1, delay=0.05):
        """
        Pomaly nastaví servo na zadaný uhol.
        :param channel: Kanál serva
        :param target_angle: Cieľový uhol (0-180)
        :param step: Krok pohybu (v stupňoch)
        :param delay: Časový interval medzi krokmi (v sekundách)
        """
        #current_angle = kit.servo[channel].angle or 0 # Získa aktuálny uhol (alebo 0, ak je None)
        current_angle = kit.servo[channel].angle if kit.servo[channel].angle is not None else default_angles.get(channel, 0)
        if current_angle < target_angle:
            for angle in range(int(current_angle), int(target_angle) + 1, step):
                kit.servo[channel].angle = angle
                time.sleep(delay)
        else:
            for angle in range(int(current_angle), int(target_angle) - 1, -step):
                kit.servo[channel].angle = angle
                time.sleep(delay)

    # Nastavenie každej časti ramena na cieľový uhol (90 stupňov)
    smooth_move(ROTATE_CHANNEL, 90)
    smooth_move(ARM1_CHANNEL, 180)
    smooth_move(ARM2_CHANNEL, 0)
    smooth_move(ARM3_CHANNEL, 180)
    smooth_move(GRIP_CHANNEL, 90)
    smooth_move(PAN_CHANNEL, 90)
    smooth_move(TILT_CHANNEL, 90)

def release_servos():
    initialize_arm()
    kit.servo[ROTATE_CHANNEL].angle = None
    kit.servo[ARM1_CHANNEL].angle = None
    kit.servo[ARM2_CHANNEL].angle = None
    kit.servo[ARM3_CHANNEL].angle = None
    kit.servo[GRIP_CHANNEL].angle = None
    kit.servo[PAN_CHANNEL].angle = None
    kit.servo[TILT_CHANNEL].angle = None

# Funkcie pre ovládanie jednotlivých častí ruky
def rotate_left():
    for _ in range(4):
        #current_angle = kit.servo[ROTATE_CHANNEL].angle or 90
        current_angle = kit.servo[ROTATE_CHANNEL].angle if kit.servo[ROTATE_CHANNEL].angle is not None else default_angles.get(ROTATE_CHANNEL, 0)
        kit.servo[ROTATE_CHANNEL].angle = max(0, current_angle + 4)
#        time.sleep(0.01)

def rotate_right():
    for _ in range(4):
        #current_angle = kit.servo[ROTATE_CHANNEL].angle or 90
        current_angle = kit.servo[ROTATE_CHANNEL].angle if kit.servo[ROTATE_CHANNEL].angle is not None else default_angles.get(ROTATE_CHANNEL, 0)
        kit.servo[ROTATE_CHANNEL].angle = min(180, current_angle - 5)
 #       time.sleep(0.01)

def arm_up():
    for channel in [ARM1_CHANNEL, ARM2_CHANNEL, ARM3_CHANNEL]:
        for _ in range(4):
            #current_angle = kit.servo[channel].angle or 90
            current_angle = kit.servo[channel].angle if kit.servo[channel].angle is not None else default_angles.get(channel, 0)
            kit.servo[channel].angle = max(10, current_angle - 5)
 #          time.sleep(0.05)

def arm_down():
    for channel in [ARM1_CHANNEL, ARM2_CHANNEL, ARM3_CHANNEL]:
        for _ in range(4):
            #current_angle = kit.servo[channel].angle or 90
            current_angle = kit.servo[channel].angle if kit.servo[channel].angle is not None else default_angles.get(channel, 0)
            kit.servo[channel].angle = min(180, current_angle + 5)
 #          time.sleep(0.05)

def grip_open():
    for _ in range(4):
        #current_angle = kit.servo[GRIP_CHANNEL].angle or 90
        current_angle = kit.servo[GRIP_CHANNEL].angle if kit.servo[GRIP_CHANNEL].angle is not None else default_angles.get(GRIP_CHANNEL, 0)
        kit.servo[GRIP_CHANNEL].angle = max(0, current_angle + 4)
  #      time.sleep(0.05)

def grip_close():
    for _ in range(4):
        #current_angle = kit.servo[GRIP_CHANNEL].angle or 90
        current_angle = kit.servo[GRIP_CHANNEL].angle if kit.servo[GRIP_CHANNEL].angle is not None else default_angles.get(GRIP_CHANNEL, 0)
        kit.servo[GRIP_CHANNEL].angle = min(180, current_angle - 4)
   #     time.sleep(0.05)

# Funkcie pre ovládanie jednotlivých častí kamery
def cam_left():
    for _ in range(3):
        current_angle = kit.servo[PAN_CHANNEL].angle if kit.servo[PAN_CHANNEL].angle is not None else default_angles.get(PAN_CHANNEL, 0)
        kit.servo[PAN_CHANNEL].angle = max(0, current_angle + 1)
        time.sleep(0.05)

def cam_right():
    for _ in range(3):
        current_angle = kit.servo[PAN_CHANNEL].angle if kit.servo[PAN_CHANNEL].angle is not None else default_angles.get(PAN_CHANNEL, 0)
        kit.servo[PAN_CHANNEL].angle = min(180, current_angle - 1)
        time.sleep(0.05)

def cam_up():
    for _ in range(3):
        current_angle = kit.servo[TILT_CHANNEL].angle if kit.servo[TILT_CHANNEL].angle is not None else default_angles.get(TILT_CHANNEL, 0)
        kit.servo[TILT_CHANNEL].angle = max(0, current_angle - 1)
        time.sleep(0.05)

def cam_down():
    for _ in range(3):
        current_angle = kit.servo[TILT_CHANNEL].angle if kit.servo[TILT_CHANNEL].angle is not None else default_angles.get(TILT_CHANNEL, 0)
        kit.servo[TILT_CHANNEL].angle = min(180, current_angle + 1)
        time.sleep(0.05)

def cleanup():
    """
    Resetuje všetky servomotory do počiatočnej polohy.
    """
    initialize_arm()



