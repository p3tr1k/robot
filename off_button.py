import RPi.GPIO as GPIO
import os
import time

BUTTON_PIN = 18  # GPIO pin, kam je pripojené tlačidlo

# Nastavenie GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        button_state = GPIO.input(BUTTON_PIN)
        if button_state == GPIO.LOW:  # Tlačidlo stlačené
            #print("Vypínam systém...")
            os.system("sudo shutdown -h now")
            time.sleep(1)  # Zamedzenie opakovaného stlačenia
except KeyboardInterrupt:
    GPIO.cleanup()