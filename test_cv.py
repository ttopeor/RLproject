import cv2
import numpy as np
import cv2.aruco as aruco

# Read in calibration matrix and distortion matrix
calibration_matrix = np.load("calibration_matrix.npy")
distortion_matrix = np.load("distortion_coefficients.npy")

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

    # Undistort frame
    undistorted_frame = cv2.undistort(frame, calibration_matrix, distortion_matrix)

    # Check if the frame was successfully read
    if not ret:
        print("Failed to read frame")
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(undistorted_frame, cv2.COLOR_BGR2GRAY)

    # Detect the markers in the grayscale image
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    # If markers are detected
    if len(corners) > 0:
        rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, 0.05, calibration_matrix, distortion_matrix)
        for i in range(len(ids)):
            # Draw circle around marker
            center = tuple(corners[i][0][0])
            radius = 10
            color = (0, 255, 0)
            thickness = 2
            cv2.circle(undistorted_frame, center, radius, color, thickness)

            # Print marker ID and position
            print("Marker ID:", ids[i], "Position:", tvecs[i])

    # Display the frame in a window
    cv2.imshow("Camera Stream", undistorted_frame)

    # Wait for a key press and check if the 'q' key was pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
cv2.destroyAllWindows()