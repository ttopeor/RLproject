import cv2
import numpy as np

# Define the dictionary of ArUco markers
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)

# Define the size of the markers in pixels
marker_size = 200

# Generate a marker image for each surface of the cube
marker_images = []
for i in range(6):
    marker_image = np.zeros((marker_size, marker_size), dtype=np.uint8)
    marker_image = cv2.aruco.drawMarker(aruco_dict, i, marker_size, marker_image, 1)
    marker_images.append(marker_image)

# Generate a marker image for each corner of the frame
corner_marker_images = []
for i in range(4):
    corner_marker_image = np.zeros((marker_size, marker_size), dtype=np.uint8)
    corner_marker_image = cv2.aruco.drawMarker(aruco_dict, i+100, marker_size, corner_marker_image, 1)
    corner_marker_images.append(corner_marker_image)

# Save the marker images to files
cv2.imwrite("marker0.png", marker_images[0])
cv2.imwrite("marker1.png", marker_images[1])
cv2.imwrite("marker2.png", marker_images[2])
cv2.imwrite("marker3.png", marker_images[3])
cv2.imwrite("marker4.png", marker_images[4])
cv2.imwrite("marker5.png", marker_images[5])
cv2.imwrite("corner_marker0.png", corner_marker_images[0])
cv2.imwrite("corner_marker1.png", corner_marker_images[1])
cv2.imwrite("corner_marker2.png", corner_marker_images[2])
cv2.imwrite("corner_marker3.png", corner_marker_images[3])