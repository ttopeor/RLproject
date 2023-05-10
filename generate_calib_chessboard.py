import cv2
import numpy as np

# Define the size of the chessboard pattern
pattern_size = (9, 6)

# Define the size of each square in the pattern in pixels
square_size = 100

# Generate the chessboard pattern image
pattern = np.zeros((pattern_size[1] * square_size, pattern_size[0] * square_size), np.uint8)
for i in range(pattern_size[1]):
    for j in range(pattern_size[0]):
        if (i + j) % 2 == 0:
            pattern[i * square_size:(i + 1) * square_size, j * square_size:(j + 1) * square_size] = 255

# Save the chessboard pattern image
cv2.imwrite("chessboard.png", pattern)