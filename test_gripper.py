from adafruit_servokit import ServoKit
import time

print("Inicializujem PCA9685...")
kit = ServoKit(channels=16)

GRIP_CHANNEL = 15

# Nastavenie pre Waveshare / štandardné SG90/MG90S
kit.servo[GRIP_CHANNEL].set_pulse_width_range(500, 2500)

print("Presúvam servo na stred (90 stupňov)...")
kit.servo[GRIP_CHANNEL].angle = 90
time.sleep(1)

print("Skok na 30 stupňov (zatvorené)...")
kit.servo[GRIP_CHANNEL].angle = 30
time.sleep(1)

print("Skok na 150 stupňov (otvorené)...")
kit.servo[GRIP_CHANNEL].angle = 150
time.sleep(1)

print("Späť na stred (90 stupňov)...")
kit.servo[GRIP_CHANNEL].angle = 90
time.sleep(1)

print("\nTeraz test plynulého pohybu (od 30 do 150 s krokom 5)...")
for angle in range(30, 151, 5):
    kit.servo[GRIP_CHANNEL].angle = angle
    time.sleep(0.05) # 50ms pauza
    
print("Hotovo. Uvoľňujem servo.")
kit.servo[GRIP_CHANNEL].angle = None
