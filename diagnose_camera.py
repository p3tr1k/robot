#!/usr/bin/env python3
import sys
import subprocess
import os

print("=== Robot Camera Diagnostic Tool ===")

# 1. Check OS and Architecture
try:
    with open("/etc/os-release") as f:
        print("\n[OS Info]")
        for line in f:
            if line.startswith("PRETTY_NAME="):
                print("  " + line.strip().replace('"', ''))
except Exception as e:
    print(f"Could not read /etc/os-release: {e}")

# 2. Check User Groups
print("\n[User Groups]")
try:
    username = os.getlogin()
except Exception:
    username = os.environ.get("USER", "unknown")
print(f"  Current user: {username}")
try:
    groups_output = subprocess.check_output(["groups"]).decode().strip()
    print(f"  Groups: {groups_output}")
    for group in ["video", "render", "input"]:
        if group in groups_output:
            print(f"  - User is in '{group}' group: OK")
        else:
            print(f"  - WARNING: User is NOT in '{group}' group! Run 'sudo usermod -aG {group} {username}'")
except Exception as e:
    print(f"  Could not check groups: {e}")

# 3. Check video devices
print("\n[Video Devices]")
if os.path.exists("/dev/video0"):
    print("  /dev/video0 exists: YES")
else:
    print("  /dev/video0 exists: NO")

try:
    media_devices = [f for f in os.listdir("/dev") if f.startswith("media")]
    if media_devices:
        print(f"  Media devices found: {media_devices}")
    else:
        print("  No /dev/media* devices found. Camera driver might not be loaded.")
except Exception as e:
    print(f"  Could not list /dev: {e}")

# 4. Check libcamera / rpicam-apps
print("\n[libcamera / rpicam detection]")
for cmd in ["rpicam-hello", "libcamera-hello"]:
    try:
        res = subprocess.run([cmd, "--list-cameras"], capture_output=True, text=True, timeout=5)
        print(f"  Output of '{cmd} --list-cameras':")
        if res.stdout.strip():
            print(res.stdout)
        if res.stderr.strip():
            print(res.stderr)
        break
    except FileNotFoundError:
        continue
    except Exception as e:
        print(f"  Error running {cmd}: {e}")
else:
    print("  Neither 'rpicam-hello' nor 'libcamera-hello' was found in PATH.")

# 5. Check imports and hardware access
print("\n[Python Imports and Camera Initialization Test]")
try:
    import cv2
    print(f"  OpenCV (cv2) version: {cv2.__version__} - OK")
except ImportError:
    print("  OpenCV (cv2) - NOT installed / import failed")

picamera2_installed = False
try:
    from picamera2 import Picamera2
    print("  Picamera2 - Import OK")
    picamera2_installed = True
except ImportError:
    print("  Picamera2 - NOT installed / import failed")

if picamera2_installed:
    print("  Attempting to initialize Picamera2...")
    try:
        picam2 = Picamera2()
        config = picam2.create_video_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        picam2.start()
        print("  Picamera2 initialization: SUCCESS!")
        picam2.stop()
    except Exception as e:
        print(f"  Picamera2 initialization: FAILED! Error details: {e}")

try:
    import cv2
    import numpy as np
    print("  Attempting to initialize OpenCV VideoCapture(0)...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"  OpenCV VideoCapture: SUCCESS! Frame captured: {frame.shape}")
            cv2.imwrite("diag_frame.jpg", frame)
            print("  Saved a test frame as 'diag_frame.jpg'")
        else:
            print("  OpenCV VideoCapture: Opened, but failed to read a frame.")
        cap.release()
    else:
        print("  OpenCV VideoCapture: FAILED to open index 0.")
except Exception as e:
    print(f"  OpenCV VideoCapture/NumPy test failed with exception: {e}")

# 6. Check /boot/firmware/config.txt (or /boot/config.txt)
print("\n[Boot Config check]")
config_paths = ["/boot/firmware/config.txt", "/boot/config.txt"]
for path in config_paths:
    if os.path.exists(path):
        print(f"  Reading {path}...")
        try:
            with open(path) as f:
                content = f.read()
                # Check for camera settings
                found_lines = []
                for line in content.splitlines():
                    if "camera" in line or "imx" in line or "dtoverlay" in line:
                        found_lines.append(line.strip())
                if found_lines:
                    for l in found_lines:
                        print(f"    {l}")
                else:
                    print("    No camera-related overlay settings found.")
        except Exception as e:
            print(f"    Failed to read {path}: {e}")
        break
else:
    print("  No boot config file found at standard locations.")

print("\n=== Diagnosis Complete ===")
