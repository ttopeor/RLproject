import threading
from Cam_communication import pose_esitmation
from Robot_communication import action, cur, ws, ws_open, des, on_action, precise_sleep, stop_event
import cv2
import numpy as np
import time
from utils import ARUCO_DICT


class Robot:
    def __init__(self, ws):
        self.ws = ws

    def action(self, x_speed, y_speed, yaw_speed):
        global des
        action(x_speed, y_speed, yaw_speed)

    @property
    def cur(self):
        return cur


class Cam:
    def __init__(self, video, aruco_dict_type, matrix_coefficients, distortion_coefficients):
        self.video = video
        self.aruco_dict_type = aruco_dict_type
        self.matrix_coefficients = matrix_coefficients
        self.distortion_coefficients = distortion_coefficients
        self.current_frame = None

    def read(self):
        return pose_esitmation(self.current_frame, self.aruco_dict_type, self.matrix_coefficients, self.distortion_coefficients)


def cam_loop(cam):
    while True:
        start_time = time.time()
        ret, frame = cam.video.read()
        if not ret:
            break
        cam.current_frame = frame
        elapsed_time = time.time() - start_time
        remaining_time = (1/30) - elapsed_time
        if remaining_time > 0:
            precise_sleep(remaining_time)


def robot_loop(robot):
    while not stop_event.is_set():
        start_time = time.time()
        if ws_open:
            robot.on_action(ws, des)
        # Calculate remaining time and sleep until next iteration
        elapsed_time = time.time() - start_time
        remaining_time = (1/80) - elapsed_time
        if remaining_time > 0:
            precise_sleep(remaining_time)


if __name__ == '__main__':
    aruco_dict_type = ARUCO_DICT["DICT_6X6_250"]
    k = np.load('calibration_matrix.npy')
    d = np.load('distortion_coefficients.npy')
    video = cv2.VideoCapture(0)
    time.sleep(2.0)

    cam = Cam(video, aruco_dict_type, k, d)
    robot = Robot(ws)

    cam_thread = threading.Thread(target=cam_loop, args=(cam,))
    robot_thread = threading.Thread(target=robot_loop, args=(robot,))
    cam_thread.start()
    robot_thread.start()
