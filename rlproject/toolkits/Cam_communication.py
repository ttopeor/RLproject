'''
Sample Usage:-
python pose_estimation_more.py -t DICT_6X6_250
'''

import numpy as np
import cv2
import sys
from .utils import ARUCO_DICT
import argparse
import time


def pose_esitmation(frame, aruco_dict_type, matrix_coefficients, distortion_coefficients):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 1)  # for testing, delete me
    cv2.aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)
    parameters = cv2.aruco.DetectorParameters()

    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
        gray, cv2.aruco_dict, parameters=parameters)

    # If markers are detected
    if len(corners) > 0:
        rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(
                corners[0], 0.02, matrix_coefficients, distortion_coefficients)
        
        if tvec[0][0][0] is not None:
            #print(tvec[0][0])
            return tvec[0][0]

    #print(np.array([None, None, None]))
    return np.array([None, None, None])


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--type", type=str,
                    default="DICT_6X6_250", help="Type of ArUCo tag to detect")
    args = vars(ap.parse_args())

    if ARUCO_DICT.get(args["type"], None) is None:
        print(f"ArUCo tag type '{args['type']}' is not supported")
        sys.exit(0)

    aruco_dict_type = ARUCO_DICT[args["type"]]

    k = np.load('calibration_matrix.npy')
    d = np.load('distortion_coefficients.npy')

    video = cv2.VideoCapture(0)
    time.sleep(2.0)

    while True:
        ret, frame = video.read()

        if not ret:
            break

        output = pose_esitmation(frame, aruco_dict_type, k, d)

        #cv2.imshow('Estimated Pose', output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
