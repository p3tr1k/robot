from flask import Flask, Response, render_template, jsonify
from picamera2 import Picamera2
import cv2
import threading

import arm
import motors

import time
import atexit


frame_lock = threading.Lock()
latest_frame = None

app = Flask(__name__)



picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()



#Inicializácia motorov a servomotorov
motors.initialize_motors()
#arm.initialize_arm()


def capture_frames():
    global latest_frame
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.rotate(frame, cv2.ROTATE_180)  # Otočenie o 180°
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        with frame_lock:
            latest_frame = buffer.tobytes()
        time.sleep(0.03)  # Odpovedá ~30 FPS



threading.Thread(target=capture_frames, daemon=True).start()

def generate_frames():
    while True:
        with frame_lock:
            if latest_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
        time.sleep(0.03)  # Odpovedá ~30 FPS


def cleanup():
    print("Server ukončený, spúšťam cleanup...")
    motors.cleanup()
    arm.cleanup()
    picam2.stop()
    print("Cleanup dokončený.")

atexit.register(cleanup)







@app.route('/')
def index():
    return render_template('index.html')  # Načítať index.html z template folderu


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/command/<action>', methods=['POST'])
def handle_command(action):
    """
    Spracovanie príkazov na ovládanie motorov a servomotorov.
    """
    try:
        # Motory robota
        if action in ['forward', 'backward', 'left', 'right', 'stop']:
            #speed = 100  # Predvolená rýchlosť
            if action == 'forward':
                motors.forward()
            elif action == 'backward':
                motors.backward()
            elif action == 'left':
                motors.left()
            elif action == 'right':
                motors.right()
            elif action == 'stop':
                motors.stop()
            return jsonify({"status": "success", "message": f"Motors {action}"}), 200

        # Servomotory ruky
        elif action in ['rotate_left', 'rotate_right', 'arm_up', 'arm_down', 'grip_open', 'grip_close', 'cam_up', 'cam_down', 'cam_left', 'cam_right']:
            if action == 'rotate_left':
                arm.rotate_left()
            elif action == 'rotate_right':
                arm.rotate_right()
            elif action == 'arm_up':
                arm.arm_up()
            elif action == 'arm_down':
                arm.arm_down()
            elif action == 'grip_open':
                arm.grip_open()
            elif action == 'grip_close':
                arm.grip_close()
            elif action == 'cam_up':
                arm.cam_up()
            elif action == 'cam_down':
                arm.cam_down()
            elif action == 'cam_left':
                arm.cam_left()
            elif action == 'cam_right':
                arm.cam_right()
            return jsonify({"status": "success", "message": f"Arm {action.replace('_', ' ')}"}), 200


        else:
            return jsonify({"status": "error", "message": "Invalid action"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/release_servos', methods=['POST'])
def release_servos():
    """
    Endpoint na uvoľnenie servomotorov.
    """
    arm.release_servos()
    return jsonify({'status': 'success', 'message': 'Servomotory boli uvoľnené.'})



if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        cleanup()

