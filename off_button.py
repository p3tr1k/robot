# /// script
# dependencies = [
#   "gpiozero",
#   "lgpio",
# ]
# ///

from gpiozero import Button
import os
from signal import pause
import logging

logger = logging.getLogger(__name__)

BUTTON_PIN = 18

def shutdown():
    logger.warning("Tlačidlo stlačené! Vypínam systém...")
    os.system("sudo shutdown -h now")

try:
    # pull_up=True je predvolené pre Button
    button = Button(BUTTON_PIN)
    button.when_pressed = shutdown
    
    logger.info(f"Monitor vypínacieho tlačidla spustený na pine {BUTTON_PIN}")
    # pause() zabráni ukončeniu skriptu a nezaťažuje CPU
    pause()
except Exception as e:
    logger.error(f"Chyba v off_button skripte: {e}")
