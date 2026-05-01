# /// script
# dependencies = [
#   "gpiozero",
# ]
# ///

from gpiozero import OutputDevice
import logging
import time

# Logovanie
logger = logging.getLogger(__name__)

# Definícia pinov (BCM)
# L_IN1, L_IN2 = 23, 24
# R_IN3, R_IN4 = 27, 22

l_in1 = None
l_in2 = None
r_in3 = None
r_in4 = None

def initialize_motors():
    global l_in1, l_in2, r_in3, r_in4
    try:
        l_in1 = OutputDevice(23)
        l_in2 = OutputDevice(24)
        r_in3 = OutputDevice(27)
        r_in4 = OutputDevice(22)
        logger.info("Motory inicializované ako digitálne výstupy (bez PWM).")
    except Exception as e:
        logger.error(f"Chyba pri inicializácii motorov: {e}")

def forward():
    if l_in1: l_in1.on(); l_in2.off()
    if r_in3: r_in3.on(); r_in4.off()

def backward():
    if l_in1: l_in1.off(); l_in2.on()
    if r_in3: r_in3.off(); r_in4.on()

def left():
    if l_in1: l_in1.off(); l_in2.on()
    if r_in3: r_in3.on(); r_in4.off()

def right():
    if l_in1: l_in1.on(); l_in2.off()
    if r_in3: r_in3.off(); r_in4.on()

def stop():
    if l_in1: l_in1.off(); l_in2.off()
    if r_in3: r_in3.off(); r_in4.off()

def cleanup():
    stop()
    if l_in1: l_in1.close()
    if l_in2: l_in2.close()
    if r_in3: r_in3.close()
    if r_in4: r_in4.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initialize_motors()
    try:
        logger.info("Test motorov (FULL POWER): Vpred na 5 sekúnd...")
        forward()
        time.sleep(5)
        logger.info("Stop.")
        stop()
    finally:
        cleanup()
