# /// script
# dependencies = [
#   "gpiozero",
#   "lgpio",
# ]
# ///

from gpiozero import Robot
import logging

# Logovanie
logger = logging.getLogger(__name__)

# Definícia pinov (BCM)
L_IN1, L_IN2 = 23, 24
R_IN3, R_IN4 = 27, 22

# Inicializácia robota
# Používame gpiozero, ktorá automaticky rieši cleanup a optimalizáciu na RPi 4
robot = None

def initialize_motors():
    global robot
    try:
        robot = Robot(left=(L_IN1, L_IN2), right=(R_IN3, R_IN4))
        logger.info("Motory inicializované cez gpiozero.")
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
