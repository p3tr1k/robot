import RPi.GPIO as GPIO

# Definícia globálnych premenných pre piny
L_IN1 = 23
L_IN2 = 24

R_IN3 = 27
R_IN4 = 22

def initialize_motors():
    """
    Inicializuje GPIO piny
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(L_IN1, GPIO.OUT)
    GPIO.setup(L_IN2, GPIO.OUT)

    GPIO.setup(R_IN3, GPIO.OUT)
    GPIO.setup(R_IN4, GPIO.OUT)

def forward():
    """
    Spustí motory dopredu
    """
    GPIO.output(L_IN1, GPIO.HIGH)
    GPIO.output(L_IN2, GPIO.LOW)
    GPIO.output(R_IN3, GPIO.LOW)
    GPIO.output(R_IN4, GPIO.HIGH)

def backward():
    """
    Spustí motory dozadu
    """
    GPIO.output(L_IN1, GPIO.LOW)
    GPIO.output(L_IN2, GPIO.HIGH)
    GPIO.output(R_IN3, GPIO.HIGH)
    GPIO.output(R_IN4, GPIO.LOW)

def left():
    """
    Otočí robota doľava.
    """
    GPIO.output(L_IN1, GPIO.LOW)  # Ľavý motor dozadu
    GPIO.output(L_IN2, GPIO.HIGH)
    GPIO.output(R_IN3, GPIO.LOW)  # Pravý motor dopredu
    GPIO.output(R_IN4, GPIO.HIGH)

def right():
    """
    Otočí robota doprava.
    """
    GPIO.output(L_IN1, GPIO.HIGH)  # Ľavý motor dopredu
    GPIO.output(L_IN2, GPIO.LOW)
    GPIO.output(R_IN3, GPIO.HIGH)  # Pravý motor dozadu
    GPIO.output(R_IN4, GPIO.LOW)

def stop():
    """
    Zastaví motory.
    """
    GPIO.output(L_IN1, GPIO.LOW)
    GPIO.output(L_IN2, GPIO.LOW)
    GPIO.output(R_IN3, GPIO.LOW)
    GPIO.output(R_IN4, GPIO.LOW)

def cleanup():
    """
    Uvoľní všetky GPIO piny.
    """
    GPIO.cleanup()


