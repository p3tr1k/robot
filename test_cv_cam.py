import cv2
print("OpenCV version:", cv2.__version__)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit(1)
ret, frame = cap.read()
if ret:
    print("Successfully captured a frame of shape:", frame.shape)
    cv2.imwrite("test_frame.jpg", frame)
    print("Saved test_frame.jpg")
else:
    print("Error: Could not read frame.")
cap.release()
