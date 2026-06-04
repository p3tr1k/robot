# /// script
# dependencies = [
#   "flask",
#   "opencv-python",
#   "gpiozero",
#   "adafruit-circuitpython-servokit",
#   "lgpio",
# ]
# ///

from flask import Flask, Response, render_template, jsonify
try:
    from picamera2 import Picamera2
    HAS_PICAMERA = True
except ImportError:
    HAS_PICAMERA = False
    print("Picamera2 nie je k dispozícii (ImportError).")

import cv2
import threading
import logging
import time
import atexit

import arm
import motors

# Nastavenie logovania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Globálny zámok a cache pre snímky
frame_lock = threading.Lock()
latest_frame = None

# Inicializácia kamery s hardvérovou rotáciou (vflip=True, hflip=True == 180°)
picam2 = None
if HAS_PICAMERA:
    try:
        picam2 = Picamera2()
        config = picam2.create_video_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        picam2.start()
        logger.info("Kamera úspešne spustená.")
    except Exception as e:
        logger.error(f"Zlyhanie kamery: {e}")
        picam2 = None
else:
    logger.warning("Spúšťam bez kamery (picamera2 chýba).")

# Inicializácia hardvéru
motors.initialize_motors()
arm.initialize_arm()

def capture_frames():
    global latest_frame
    if not picam2: return
    
    while True:
        try:
            frame = picam2.capture_array()
            # Rotácia 180° priamo v CV2, ak nefunguje v driveri (na RPi 4 je to bleskové)
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            with frame_lock:
                latest_frame = buffer.tobytes()
            time.sleep(0.03)
        except Exception as e:
            logger.error(f"Chyba pri snímaní: {e}")
            break

if picam2:
    threading.Thread(target=capture_frames, daemon=True).start()

def generate_frames():
    while True:
        with frame_lock:
            if latest_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
        time.sleep(0.04)

def cleanup():
    logger.info("Spúšťam bezpečné ukončenie hardvéru...")
    motors.cleanup()
    arm.cleanup()
    if picam2: picam2.stop()

atexit.register(cleanup)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/command/<action>', methods=['POST'])
def handle_command(action):
    try:
        # Mapovanie príkazov na funkcie
        motor_commands = {
            'forward': motors.forward, 'backward': motors.backward,
            'left': motors.left, 'right': motors.right, 'stop': motors.stop
        }
        
        arm_commands = {
            'rotate_left': arm.rotate_left, 'rotate_right': arm.rotate_right,
            'arm_up': arm.arm_up, 'arm_down': arm.arm_down,
            'grip_open': arm.grip_open, 'grip_close': arm.grip_close,
            'cam_up': arm.cam_up, 'cam_down': arm.cam_down,
            'cam_left': arm.cam_left, 'cam_right': arm.cam_right
        }

        if action in motor_commands:
            motor_commands[action]()
            return jsonify({"status": "success"}), 200
        elif action in arm_commands:
            arm_commands[action]()
            return jsonify({"status": "success"}), 200
        
        return jsonify({"status": "error", "message": "Neznámy príkaz"}), 400
    except Exception as e:
        logger.error(f"Chyba pri príkaze {action}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/release_servos', methods=['POST'])
def release_servos():
    arm.release_servos()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Na Trixie odporúčam vypnúť debug mód, ak nie je nevyhnutný
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
