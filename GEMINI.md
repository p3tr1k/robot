# Gemini AI System Instructions for Robot Project

This file contains memory, context, and specific instructions for Gemini CLI when working on this project.

## Current Hardware State (As of June 2026)
*   **Motors:** Connected and working (`gpiozero`).
*   **Arm (Shoulder):** Two MG996R servos. Connected to channels 10 (`SHOULDER_A`) and 11 (`SHOULDER_B`).
*   **Arm (Elbow):** Connected to channel 12 (`ELBOW_CHANNEL`).
*   **Wrist (Zapastie):** **INSTALLED**. Connected to channel 13 (`WRIST_CHANNEL`).
*   **Gripper:** **INSTALLED**. Connected to channel 15 (`GRIP_CHANNEL`).
*   **Base Rotation:** Connected to channel 8 (`ROTATE_CHANNEL`).
*   **Camera:** **PENDING HARDWARE**. Pan/Tilt servos are on channels 9 and 7 (Tilt moved from 8).
*   **Power:** The PCA9685 and MG996R servos draw significant current. Stalling them (e.g., lifting heavy loads) can cause a voltage drop leading to a servo lockout. **Fix:** Hard physical reset of the servo power supply.

## Software Design Rules implemented
*   **Movement Smoothing:** Web UI sends commands every 50ms. `arm.py` uses `STEP = 1` for ultra-smooth, slow movement.
*   **State Tracking:** `arm.py` uses `current_angles` to remember servo positions because RC servos lack feedback.
*   **Gravity Workaround:** Upon `release_servos`, the code estimates if the arm fell forward, backward, or stayed balanced, and updates `current_angles` accordingly to prevent jumping on the next command.
*   **Park Sequence:** On shutdown (caught via `atexit` in `app.py`), `arm.py` slowly lowers the arm to 170° before cutting PWM.

## Future Tasks / TODOs
1.  **Hardware Integration:** Integrate the 3D-printed wrist and gripper. Update `arm.py` channels and limits accordingly.
2.  **Camera Setup:** Connect the camera, install the mount, and re-enable `picamera2`/`cv2` dependencies in the run command if necessary. Test Pan/Tilt.
3.  **Pre-programmed Poses:** Implement functions in `arm.py` (and corresponding UI buttons) for complex poses. E.g., `pose_rest()`, `pose_ready()`, `pose_grab()`. These should use loops to slowly transition all joints to the target angles simultaneously.
