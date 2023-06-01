import threading
import websocket
from .Cam_communication import pose_esitmation
from .Robot_communication import precise_sleep
import cv2
import numpy as np
import time
from .utils import ARUCO_DICT
import json


class env:
    def __init__(self, robot_url, cam_port, k, d):
        self.robot_url = robot_url
        self.cam_port = cam_port
        self.k = k
        self.d = d

        self.robot = None
        self.cam = None

    def start(self):
        # CAM
        aruco_dict_type = ARUCO_DICT["DICT_6X6_250"]
        k = np.load(self.k)
        d = np.load(self.d)
        video = cv2.VideoCapture(self.cam_port)
        time.sleep(2.0)

        self.cam = Cam(video, aruco_dict_type, k, d)
        cam_thread = threading.Thread(target=cam_loop, args=(self.cam,))
        cam_thread.start()
        # print(cam.get_cam_pose())

        # ROBOT
        ws_url = self.robot_url
        self.robot = Robot(ws_url)
        robot_thread = threading.Thread(target=robot_loop, args=(self.robot,))
        robot_thread.start()
        # robot.action(2, 0, 0)
        # print(robot.get_robot_state())
        time.sleep(2.0)
        print("Environment Ready!!")

    def get_state(self):
        cube_pose = self.cam.get_cube_pose()
        xc, yc = cube_pose[0], cube_pose[1]

        robot_pose = self.robot.get_robot_state()
        x = robot_pose['x']
        y = robot_pose['y']
        yaw = robot_pose['yaw']

        # return [x, y, yaw, xc, yc]
        if xc is None:
            return np.array([x, y, yaw, 10.0, 10.0])
        return np.array([x, y, yaw, xc, yc])


class Cam:
    def __init__(self, video, aruco_dict_type, matrix_coefficients, distortion_coefficients):
        self.video = video
        self.aruco_dict_type = aruco_dict_type
        self.matrix_coefficients = matrix_coefficients
        self.distortion_coefficients = distortion_coefficients
        self.cube_pose = np.array([None, None, None])
        self.current_frame = None

    def read(self):
        return pose_esitmation(self.current_frame, self.aruco_dict_type, self.matrix_coefficients, self.distortion_coefficients)

    def get_cube_pose(self):
        return self.cube_pose


class Robot:
    def __init__(self, ws_url):
        self.ws = websocket.WebSocketApp(
            ws_url, on_message=self.on_message, on_open=self.on_open, on_close=self.on_close)
        self.cur = {
            'x': 0,
            'y': 0.221,
            'z': 0.070,
            'roll': 180,
            'pitch': 0,
            'yaw': -90
        }
        self.des = {
            'x': 0,
            'y': 0.221,
            'z': 0.070,
            'roll': 180,
            'pitch': 0,
            'yaw': -90
        }
        self.x_speed = 0.0
        self.y_speed = 0.0
        self.yaw_speed = 0.0

        self.ws_open = False
        self.stop_event = threading.Event()
        self.ws_thread = threading.Thread(
            target=self.run_websocket, args=(self.ws,))  # Here, no arguments are passed to the run_websocket method

    def on_message(self, ws, message):
        msg = json.loads(message)
        if msg['event'] == 'StatusUpdate':
            self.cur = msg['payload']['jointState']['cartesianPosition']

    def on_open(self, ws):
        self.ws_open = True
        msg = {
            'action': 'SetTask',
            'payload': {
                'type': 'ExternalPositionControlTask',
            }
        }
        ws.send(json.dumps(msg))

    def on_close(self, ws):
        self.ws_open = False

    def on_action(self, ws, des):
        self.ws.send(json.dumps({
            'action': 'ExternalPositionControl',
            'payload': des
        }))

    def run_websocket(self, ws):
        self.ws.run_forever()

    def stop_websocket(ws):
        msg = {
            'action': 'Stop',
        }
        ws.send(json.dumps(msg))
        ws.close()

    def update_des(self, x_speed, y_speed, yaw_speed):

        step_size = (1/80)*(1/1000)
        roll_size = (1/80)*(1)

        def is_within_bounds(value, lower_bound, upper_bound, direction):
            if direction == 1:  # moving towards upper_bound
                return value <= upper_bound
            else:  # moving towards lower_bound
                return value >= lower_bound

        current_x, current_y = self.des["x"], self.des["y"]

        new_y = current_y + y_speed * step_size
        y_direction = np.sign(y_speed)
        if is_within_bounds(new_y, 0.150, 0.280, y_direction):
            self.des["y"] = new_y

        new_x = current_x + x_speed * step_size
        x_direction = np.sign(x_speed)
        if is_within_bounds(new_x, -0.150, 0.150, x_direction):
            self.des["x"] = new_x

        if yaw_speed != 0:
            new_yaw = self.des["yaw"] + yaw_speed * roll_size
            if new_yaw <= 40 and new_yaw >= -220:
                self.des["yaw"] = new_yaw

        self.des["z"] = 0.070
        self.des["roll"] = 180
        self.des["pitch"] = 0

    def action(self, x_speed, y_speed, yaw_speed):
        self.x_speed = max(-1, min(1, x_speed))*50
        self.y_speed = max(-1, min(1, y_speed))*50
        self.yaw_speed = max(-1, min(1, yaw_speed))*50
        # print("action: ", self.x_speed, self.y_speed, self.yaw_speed)

    def start(self):
        self.ws_thread.start()
        time.sleep(1)
        self.des = self.cur

    def stop(self):
        print("Stopping...")
        self.stop_event.set()
        self.stop_websocket(self.ws)
        self.ws_thread.join()
        print("Stopped")

    def get_robot_state(self):
        return self.cur


def cam_loop(cam):
    while True:
        start_time = time.time()
        ret, frame = cam.video.read()
        if not ret:
            break
        cam.current_frame = frame
        cam.cube_pose = cam.read()
        elapsed_time = time.time() - start_time
        remaining_time = (1/30) - elapsed_time
        if remaining_time > 0:
            precise_sleep(remaining_time)


def robot_loop(robot):
    robot.start()
    try:
        while not robot.stop_event.is_set():
            start_time = time.time()
            if robot.ws_open:
                robot.update_des(robot.x_speed, robot.y_speed, robot.yaw_speed)
                robot.on_action(robot.ws, robot.des)
            # Calculate remaining time and sleep until next iteration
            elapsed_time = time.time() - start_time
            remaining_time = (1/80) - elapsed_time
            if remaining_time > 0:
                precise_sleep(remaining_time)

    except KeyboardInterrupt:
        robot.stop()


if __name__ == '__main__':
    robot_url = "ws://localhost:8080/api/ws"
    cam_port = 4
    k = "calibration_matrix.npy"
    d = "distortion_coefficients.npy"
    Env = env(robot_url, cam_port, k, d)
    Env.start()
    # Env.robot.action(1, 0, 0)
    while True:
        state = Env.get_state()
        print(state)
        time.sleep(1)
