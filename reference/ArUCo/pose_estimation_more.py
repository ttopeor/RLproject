'''
Sample Usage:-
python pose_estimation_more.py -t DICT_6X6_250
'''

import numpy as np
import cv2
import sys
from utils import ARUCO_DICT
import argparse
import time


def pose_esitmation(frame, aruco_dict_type, matrix_coefficients, distortion_coefficients):

    '''
    frame - Frame from the video stream
    matrix_coefficients - Intrinsic matrix of the calibrated camera
    distortion_coefficients - Distortion coefficients associated with your camera

    return:-
    frame - The frame with the axis drawn on it
    '''

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)
    parameters = cv2.aruco.DetectorParameters()


    #corners, ids, rejected_img_points = cv2.aruco.detectMarkers(gray, cv2.aruco_dict,parameters=parameters,
    #    cameraMatrix=matrix_coefficients,
    #    distCoeff=distortion_coefficients)
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, cv2.aruco_dict, parameters=parameters)

        # If markers are detected
    if len(corners) > 0:
        tvec_list = [[None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None],\
                     [None,None,None],[None,None,None],[None,None,None],[None,None,None],[None,None,None]]
        for i in range(0, len(ids)):
            # Estimate pose of each marker and return the values rvec and tvec---(different from those of camera coefficients)
            rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 0.02, matrix_coefficients,
                                                                       distortion_coefficients)
            #for j in range(rvec.shape[0]):
                #cv2.drawFrameAxes(frame, matrix_coefficients, distortion_coefficients, rvec[j, :, :], tvec[j, :, :], 0.01)
            cv2.aruco.drawDetectedMarkers(frame, corners)
            tvec_list[i]=np.round(tvec[0][0],3)
        print("ID_0:", tvec_list[0],"ID_1:", tvec_list[1],"ID_2:", tvec_list[2],"ID_3:", tvec_list[3],"ID_4:", tvec_list[4], \
              "ID_5:", tvec_list[5],"ID_6:", tvec_list[6],"ID_7:", tvec_list[7],"ID_8:", tvec_list[8],"ID_9:", tvec_list[9])
    # np.savetxt('./corners',corners)
    # print(type(corners))
    #print(corners)
    return frame

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--type", type=str, default="DICT_ARUCO_ORIGINAL", help="Type of ArUCo tag to detect")
    args = vars(ap.parse_args())

    
    if ARUCO_DICT.get(args["type"], None) is None:
        print(f"ArUCo tag type '{args['type']}' is not supported")
        sys.exit(0)

    aruco_dict_type = ARUCO_DICT[args["type"]]

    
    k=np.load('calibration_matrix.npy')
    d=np.load('distortion_coefficients.npy')

    video = cv2.VideoCapture(2)
    time.sleep(2.0)

    while True:
        ret, frame = video.read()

        if not ret:
            break
        
        output = pose_esitmation(frame, aruco_dict_type, k, d)

        cv2.imshow('Estimated Pose', output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()