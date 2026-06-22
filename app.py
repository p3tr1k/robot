from flask import Flask, Response, render_template, jsonify
try:
    from picamera2 import Picamera2
    HAS_PICAMERA = True
except ImportError:
    HAS_PICAMERA = False
    print("Picamera2 nie je k dispozícii.")

HAS_NUMPY = False
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
    HAS_NUMPY = True
except ImportError:
    HAS_CV2 = False
    HAS_NUMPY = False
    print("OpenCV (cv2) alebo NumPy nie je k dispozícii.")

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
hardware_lock = threading.Lock() # Zámok na prevenciu súbežného behu motorov a serv
latest_frame = None

# Inicializácia kamery
picam2 = None
cap = None
use_opencv_cam = False

if HAS_PICAMERA:
    try:
        picam2 = Picamera2()
        config = picam2.create_video_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        picam2.start()
        logger.info("Kamera úspešne spustená cez Picamera2.")
    except Exception as e:
        logger.warning(f"Zlyhanie Picamera2: {e}. Skúšam OpenCV...")
        picam2 = None

if picam2 is None and HAS_CV2:
    try:
        cap = cv2.VideoCapture(0)
        # Nastavenie rozlíšenia na 640x480 pre konzistentnosť a rýchlosť
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if cap.isOpened():
            use_opencv_cam = True
            logger.info("Kamera úspešne spustená cez OpenCV (VideoCapture).")
        else:
            logger.error("Nepodarilo sa otvoriť kameru cez OpenCV.")
            cap = None
    except Exception as e:
        logger.error(f"Zlyhanie OpenCV kamery: {e}")
        cap = None

if picam2 is None and not use_opencv_cam:
    logger.warning("Spúšťam bez aktívnej kamery (žiadna kamera nebola detegovaná).")

# Inicializácia hardvéru
motors.initialize_motors()
arm.initialize_arm()

def generate_placeholder_frame(message="Kamera offline"):
    if not HAS_CV2 or not HAS_NUMPY:
        return None
    try:
        # Vytvorí čierny obrázok 640x480
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(message, font, 0.8, 2)[0]
        text_x = (img.shape[1] - text_size[0]) // 2
        text_y = (img.shape[0] + text_size[1]) // 2
        cv2.putText(img, message, (text_x, text_y), font, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 70])
        return buffer.tobytes()
    except Exception as e:
        logger.error(f"Chyba pri generovaní placeholderu: {e}")
        return None

def capture_frames():
    global latest_frame
    if not HAS_CV2:
        return
    if not picam2 and not use_opencv_cam:
        # Ak nie je kamera, vygenerujeme statický placeholder raz na začiatku
        placeholder = generate_placeholder_frame("Kamera offline")
        if placeholder:
            with frame_lock:
                latest_frame = placeholder
        return
    
    while True:
        try:
            if picam2:
                frame = picam2.capture_array()
                # Rotácia 180° priamo v CV2
                frame = cv2.rotate(frame, cv2.ROTATE_180)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            elif use_opencv_cam and cap:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Nepodarilo sa načítať snímku z OpenCV kamery.")
                    time.sleep(0.1)
                    continue
                # Prehodenie 180° (ak je kamera namontovaná hore nohami na pan/tilt)
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            else:
                break
            
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            with frame_lock:
                latest_frame = buffer.tobytes()
            time.sleep(0.03)
        except Exception as e:
            logger.error(f"Chyba pri snímaní: {e}")
            time.sleep(0.5) # Krátky sleep pred ďalším pokusom

# Spustenie snímania v samostatnom vlákne
threading.Thread(target=capture_frames, daemon=True).start()

def generate_frames():
    while True:
        with frame_lock:
            frame_to_send = latest_frame
        
        if frame_to_send:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_to_send + b'\r\n')
            time.sleep(0.04)
        else:
            # Ak snímka ešte nie je k dispozícii, vygenerujeme placeholder
            placeholder = generate_placeholder_frame("Nacitavam kameru...")
            if placeholder:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + placeholder + b'\r\n')
            time.sleep(0.1)

def cleanup():
    logger.info("Spúšťam bezpečné ukončenie hardvéru...")
    motors.cleanup()
    arm.cleanup()
    if picam2:
        try:
            picam2.stop()
        except Exception as e:
            logger.error(f"Chyba pri zastavení Picamera2: {e}")
    if cap:
        try:
            cap.release()
        except Exception as e:
            logger.error(f"Chyba pri uvoľnení OpenCV kamery: {e}")

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
            'elbow_up': arm.elbow_up, 'elbow_down': arm.elbow_down,
            'wrist_up': arm.wrist_up, 'wrist_down': arm.wrist_down,
            'grip_open': arm.grip_open, 'grip_close': arm.grip_close,
            'cam_up': arm.cam_up, 'cam_down': arm.cam_down,
            'cam_left': arm.cam_left, 'cam_right': arm.cam_right
        }

        if action in motor_commands:
            with hardware_lock:
                motor_commands[action]()
            return jsonify({"status": "success"}), 200
        elif action in arm_commands:
            with hardware_lock:
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
