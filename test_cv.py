import cv2
import numpy as np

# Define the dictionary of ArUco markers
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)

# Define the parameters for detecting the markers
parameters = cv2.aruco.DetectorParameters_create()

# Create a VideoCapture object to read from the USB camera
cap = cv2.VideoCapture(2)

# Check if the camera was successfully opened
if not cap.isOpened():
    print("Failed to open camera")
    exit()

# Loop over frames from the camera stream
while True:
    # Read a frame from the camera stream
    ret, frame = cap.read()

    # Check if the frame was successfully read
    if not ret:
        print("Failed to read frame")
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect the markers in the grayscale image
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    # If markers are detected, draw a bounding box around them and show the center of each marker
    if ids is not None:
        # Draw a bounding box around the markers for visualization
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # Loop over the detected markers and show the center of each marker
        for i in range(len(ids)):
            # Get the center of the marker
            center = np.mean(corners[i][0], axis=0).astype(int)

            # Draw a circle at the center of the marker for visualization
            cv2.circle(frame, tuple(center), 5, (0, 0, 255), -1)

    # Display the frame in a window
    cv2.imshow("Camera Stream", frame)

    # Wait for a key press and check if the 'q' key was pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
cv2.destroyAllWindows()