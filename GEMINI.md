# Gemini AI System Instructions for Robot Project

This file contains memory, context, and specific instructions for Gemini CLI when working on this project.

## Current Hardware State (As of June 2026)
*   **Motors:** Connected and working (`gpiozero`).
*   **Arm (Shoulder):** Two MG996R servos. Connected to channels 10 (`SHOULDER_A`) and 11 (`SHOULDER_B`). Note: Left and Right were physically swapped, so 10° is now back/parked, and 170° is forward.
*   **Arm (Elbow):** Connected to channel 12 (`ELBOW_CHANNEL`).
*   **Wrist:** Connected to channel 13 (`WRIST_CHANNEL`).
*   **Gripper:** Connected to channel 15 (`GRIP_CHANNEL`). Replaced during session. Requires absolute angle jumps (80° to 160°) for maximum torque to overcome mechanical friction.
*   **Base Rotation:** Connected to channel 8 (`ROTATE_CHANNEL`).
*   **Camera:** **PENDING HARDWARE**. Pan/Tilt servos are on channels 9 and 7.
*   **Power / Hardware Lock:** The PCA9685 and DC Motors share a power supply. Simultaneous operation causes severe brownouts and I2C corruption, which previously destroyed a servo. **Fix:** A `hardware_lock` (Threading Lock) is implemented in `app.py` to serialize all motor and servo commands. Never operate wheels and arms concurrently.

## Software Design Rules implemented
*   **Movement Smoothing:** Web UI sends commands via an async fetch lock every 100ms (preventing backlog). `arm.py` uses `STEP = 2` for the arm.
*   **Safety Constraints:** Explicit `SAFE_MIN` and `SAFE_MAX` bounds are implemented for specific joints (e.g., Elbow: 30-180, Gripper: 80-160) to prevent mechanical singularities, self-collisions, and servo stalls.
*   **State Tracking:** `arm.py` uses `current_angles` to remember servo positions.
*   **Gravity Workaround:** Upon `release_servos`, the code estimates if the arm fell forward (150°) or backward (10°), updating `current_angles` for both `SHOULDER_A` and `SHOULDER_B` to prevent jumping on the next command.
*   **Park Sequence:** **CURRENTLY DISABLED.** Simultaneous parking caused physical self-collision between the wrist and arm. Future task: Calibrate a sequential, step-by-step parking procedure.

## Future Tasks / TODOs
1.  **Safe Park Sequence:** Manually move the arm into a safe resting pose, record the specific angles for all 4 joints, and implement a sequential `park_arm()` routine (e.g., Wrist straight -> Elbow tucked -> Shoulder back) to avoid self-collision.
2.  **Camera Setup:** Connect the camera, install the mount, and re-enable `picamera2`/`cv2` dependencies in the run command if necessary. Test Pan/Tilt.
3.  **Pre-programmed Poses:** Implement functions in `arm.py` (and corresponding UI buttons) for complex poses. E.g., `pose_rest()`, `pose_ready()`, `pose_grab()`.
