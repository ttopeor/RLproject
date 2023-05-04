import cv2
import numpy as np
import time

t0 = time.monotonic()
cap = cv2.VideoCapture(1)
t1 = time.monotonic()

t2 = time.monotonic()
ret, frame = cap.read()
t3 = time.monotonic()

print("size = ", np.shape(frame))
cv2.imshow('frame', frame)
cv2.waitKey(0)
cap.release()
cv2.destroyAllWindows()

print(t1-t0, t2-t1, t3 - t2)