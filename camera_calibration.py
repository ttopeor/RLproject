import cv2
import numpy as np

# Define the size of the chessboard pattern
pattern_size = (9, 6)

# Define the 3D coordinates of the corners of the chessboard pattern in meters
square_size = 0.025
object_points = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
object_points[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2) * square_size

# Create arrays to store the object points and image points for all calibration images
object_points_list = []
image_points_list = []

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

    # Find the corners of the chessboard pattern in the grayscale image
    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

    # If corners are found, add the object points and image points to the lists
    if ret:
        object_points_list.append(object_points)
        image_points_list.append(corners)

        # Draw the corners on the frame for visualization
        cv2.drawChessboardCorners(frame, pattern_size, corners, ret)

    # Display the frame in a window
    cv2.imshow("Camera Stream", frame)

    # Wait for a key press and check if the 'q' key was pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
cv2.destroyAllWindows()

# Calibrate the camera using the object points and image points
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(object_points_list, image_points_list, gray.shape[::-1], None, None)

# Print the camera matrix and distortion coefficients
print("Camera Matrix:\n", camera_matrix)
print("Distortion Coefficients:\n", dist_coeffs)

# import numpy as np
# import cv2 as cv
# import glob
# # termination criteria
# criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
# objp = np.zeros((6*7,3), np.float32)
# objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
# # Arrays to store object points and image points from all the images.
# objpoints = [] # 3d point in real world space
# imgpoints = [] # 2d points in image plane.
# # images = glob.glob('*.png')
# for i in range(1, 9):
#     # Load the calibration image
#     filename = "calibration/calibration{}.jpg".format(i)
#     img = cv.imread(filename)
#     gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#     # Find the chess board corners
#     ret, corners = cv.findChessboardCorners(gray, (7,6), None)
#     # If found, add object points, image points (after refining them)
#     if ret == True:
#         objpoints.append(objp)
#         corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
#         imgpoints.append(corners2)
#         # Draw and display the corners
#         cv.drawChessboardCorners(img, (7,6), corners2, ret)
#         cv.imshow('img', img)
#         cv.waitKey(500)
# cv.destroyAllWindows()