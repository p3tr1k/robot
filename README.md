# Project Robot

Flask-based web interface and control software for a custom Raspberry Pi 4 powered robot.

## Hardware Architecture
*   **Brain:** Raspberry Pi 4 (Running Debian 13 / Trixie)
*   **Motor Controller (Wheels):** L298N (or similar dual H-bridge) controlled via GPIO using the `gpiozero` library.
*   **Servo Controller (Arm/Camera):** PCA9685 16-channel I2C PWM driver using the `adafruit-circuitpython-servokit` library.
*   **Arm Servos:** MG996R (Metal gear)
*   **Camera:** Raspberry Pi Camera Module (controlled via `picamera2`)

## Software Architecture
*   `app.py`: Main Flask application. Provides the web server, handles API endpoints for control, and manages the video feed. Runs via `uv` using system site-packages.
*   `arm.py`: Logic for the robotic arm. Includes safe limits, state tracking, inverse kinematics (shoulder/elbow), and a safe parking sequence on shutdown.
*   `motors.py`: Logic for the wheeled base.
*   `templates/index.html`: The frontend UI. Sends commands via fetch API every 50ms while buttons are held. Contains logic to prevent duplicate touch/mouse events and runaway intervals.

## Running the Application
The project relies on system-level packages (like `lgpio` and `picamera2`) that cannot be easily built in an isolated virtual environment on this architecture. Therefore, it is run using `uv` with the system Python:

```bash
uv run --with adafruit-circuitpython-servokit --with flask --python /usr/bin/python3 app.py
```
