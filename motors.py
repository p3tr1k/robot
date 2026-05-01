# /// script
# dependencies = [
#   "gpiozero",
# ]
# ///

from gpiozero import Robot
import logging
import time

# Logovanie
logger = logging.getLogger(__name__)

# Definícia pinov (BCM)
L_IN1, L_IN2 = 23, 24
R_IN3, R_IN4 = 27, 22

# Inicializácia robota
robot = None

def initialize_motors():
    global robot
    try:
        # Na Trixie/RPi 5 je lgpio predvolený backend pre gpiozero
        robot = Robot(left=(L_IN1, L_IN2), right=(R_IN3, R_IN4))
        logger.info("Motory inicializované.")
    except Exception as e:
        logger.error(f"Chyba pri inicializácii motorov: {e}")

def forward():
    if robot: robot.forward()

def backward():
    if robot: robot.backward()

def left():
    if robot: robot.left()

def right():
    if robot: robot.right()

def stop():
    if robot: robot.stop()

def cleanup():
    if robot:
        robot.stop()
        robot.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initialize_motors()
    if robot:
        logger.info("Test motorov: Vpred na 2 sekundy...")
        forward()
        time.sleep(2)
        stop()
        cleanup()
