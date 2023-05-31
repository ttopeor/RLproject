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

        T_base_inv = np.linalg.inv(T_base)
        tvec_rels = []
        # Compute relative positions for IDs 1-6
        for i, id in enumerate(ids):
            if id == 0:
                rvec_target, tvec_target, _ = cv2.aruco.estimatePoseSingleMarkers(
                    corners[i], 0.02, matrix_coefficients, distortion_coefficients)
                R_target, _ = cv2.Rodrigues(rvec_target)
                rvec_target = rvec_target[0]
                T_target = np.hstack((R_target, rvec_target.reshape(3, 1)))
                T_target = np.vstack((T_target, [0, 0, 0, 1]))
                T_rel = np.dot(T_base_inv, T_target)
                tvec_rels.append(T_rel[:3, 3])

        # Return relative position with maximum z value
        if tvec_rels:
            max_tvec_rel = max(tvec_rels, key=lambda tvec: tvec[2])
            max_tvec_rel[1] = 0.29 - max_tvec_rel[1]
            #print(np.array(max_tvec_rel))
            return max_tvec_rel
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

    video = cv2.VideoCapture(8)
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
