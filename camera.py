from adafruit_servokit import ServoKit
import time

# Inicializácia PCA9685
kit = ServoKit(channels=16)

# Kanály pre ovládanie kamery
PAN_CHANNEL = 9    # Otáčanie kamery doľava/doprava
TILT_CHANNEL = 8   # Nakláňanie kamery hore/dolu

# Nastavenie pulzného rozsahu servomotorov
kit.servo[PAN_CHANNEL].set_pulse_width_range(500, 2500)
kit.servo[TILT_CHANNEL].set_pulse_width_range(500, 2500)

# Predvolené uhly
default_angles = {
    PAN_CHANNEL: 90,
    TILT_CHANNEL: 90
}

def initialize_camera():
    """
    Inicializuje polohu kamery na stredovú pozíciu.
    """
    move_smooth(PAN_CHANNEL, default_angles[PAN_CHANNEL])
    move_smooth(TILT_CHANNEL, default_angles[TILT_CHANNEL])

def move_smooth(channel, target_angle, step=1, delay=0.05):
    """
    Pomaly nastaví servo na požadovaný uhol.
    """
    current_angle = kit.servo[channel].angle if kit.servo[channel].angle is not None else default_angles[channel]
    if current_angle < target_angle:
        for angle in range(int(current_angle), int(target_angle) + 1, step):
            kit.servo[channel].angle = angle
            time.sleep(delay)
    else:
        for angle in range(int(current_angle), int(target_angle) - 1, -step):
            kit.servo[channel].angle = angle
            time.sleep(delay)

def pan_right():
    move_smooth(PAN_CHANNEL, max(0, kit.servo[PAN_CHANNEL].angle - 10))

def pan_left():
    move_smooth(PAN_CHANNEL, min(180, kit.servo[PAN_CHANNEL].angle + 10))

def tilt_up():
    move_smooth(TILT_CHANNEL, max(0, kit.servo[TILT_CHANNEL].angle - 10))

def tilt_down():
    move_smooth(TILT_CHANNEL, min(180, kit.servo[TILT_CHANNEL].angle + 10))

def release_camera():
    """
    Uvoľní servomotory pre kameru.
    """
    kit.servo[PAN_CHANNEL].angle = None
    kit.servo[TILT_CHANNEL].angle = None
