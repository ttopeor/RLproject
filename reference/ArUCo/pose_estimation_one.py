#!/usr/bin/python
# -*- coding: UTF-8 -*-
import numpy as np
import time
import cv2, math
import cv2.aruco as aruco


def rotationVectorToEulerAngles(rvec):
    R = np.zeros((3, 3), dtype=np.float64)
    cv2.Rodrigues(rvec, R)
    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
    singular = sy < 1e-6
    if not singular:  # 偏航，俯仰，滚动
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0
    # 偏航，俯仰，滚动换成角度
    rx = x * 180.0 / 3.141592653589793
    ry = y * 180.0 / 3.141592653589793
    rz = z * 180.0 / 3.141592653589793
    return rx, ry, rz


mtx = np.array([[1.85742992e+03, 0.00000000e+00, 1.89633031e+03],
 [0.00000000e+00, 1.86806341e+03, 1.08966563e+03],
 [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist = np.array(([[ 0.11238687,-0.11429915,-0.00124426,0.00161879,0.05449028]]))
# mtx=np.load(r'C:\Users\Admin\Desktop\ArUCo-Markers-Pose-Estimation-Generation-Python-main\npy\calibration_matrix.npy')
# dist=np.load((r'C:\Users\Admin\Desktop\ArUCo-Markers-Pose-Estimation-Generation-Python-main\npy\distortion_coefficients.npy'))

cap = cv2.VideoCapture(2)
font = cv2.FONT_HERSHEY_SIMPLEX #font for displaying text (below)
#num = 0
while True:
    ret, frame = cap.read()
    h1, w1 = frame.shape[:2]
    # print(h1, w1)
    # 读取摄像头画面
    # 纠正畸变
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (h1, w1), 0, (h1, w1))
    dst1 = cv2.undistort(frame, mtx, dist, None, newcameramtx)
    x, y, w1, h1 = roi
    dst1 = dst1[y:y + h1, x:x + w1]
    frame = dst1
    # print(newcameramtx)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
    parameters = aruco.DetectorParameters()
    dst1 = cv2.undistort(frame, mtx, dist, None, newcameramtx)
    detector = aruco.ArucoDetector(aruco_dict,parameters)
    '''
    detectMarkers(...)
        detectMarkers(image, dictionary[, corners[, ids[, parameters[, rejectedI
        mgPoints]]]]) -> corners, ids, rejectedImgPoints
    '''

    #使用aruco.detectMarkers()函数可以检测到marker，返回ID和标志板的4个角点坐标
    corners, ids, rejectedImgPoints = detector.detectMarkers(gray)
    objPoints = cv2.Mat(4, 1, cv2.CV_32FC3)
    # objPoints = cv2.Mat(4, 1)
 
#    如果找不打id
    if ids is not None:

        rvec, tvec= cv2.solvePnP(objPoints, corners, mtx, dist)
        # 估计每个标记的姿态并返回nt(值rvet和tvec ---不同
        # from camera coeficcients
        (rvec-tvec).any()# get rid of that nasty numpy value array error
        for i in range(rvec.shape[0]):
            aruco.drawAxis(frame, mtx, dist, rvec[i, :, :], tvec[i, :, :], 0.03)
            aruco.drawDetectedMarkers(frame, corners)
        ###### DRAW ID #####
        cv2.putText(frame, "Id: " + str(ids), (0, 40), font, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
        EulerAngles = rotationVectorToEulerAngles(rvec)
        EulerAngles = [round(i, 2) for i in EulerAngles]
        cv2.putText(frame, "Attitude_angle:" + str(EulerAngles), (0, 120), font, 0.6, (0, 255, 0), 2,
                    cv2.LINE_AA)
        tvec = tvec * 1000
        for i in range(3):
            tvec[0][0][i] = round(tvec[0][0][i], 1)
        tvec = np.squeeze(tvec)
        cv2.putText(frame, "Position_coordinates:" + str(tvec) + str('mm'), (0, 80), font, 0.6, (0, 255, 0), 2,
                    cv2.LINE_AA)
    else:
        ##### DRAW "NO IDS" #####
        cv2.putText(frame, "No Ids", (0, 40), font, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

    # cv2.namedWindow('frame', 0)
    # cv2.resizeWindow("frame", 960, 720)
    # 显示结果框架
    cv2.imshow("frame", frame)

    key = cv2.waitKey(1)

    if key == 27:         # 按esc键退出
        print('esc break...')
        cap.release()
        cv2.destroyAllWindows()
        break
    num = 0
    if key == ord(' '):   # 按空格键保存
        filename = "E:/code/" + str(time.time())[:10] + ".jpg"
        num += 1
        cv2.imwrite(filename, frame)
        print("ok")

