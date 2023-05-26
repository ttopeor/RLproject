import json
import time
import keyboard
import math
from toolkits.communication import env


def process_key_events(env):
    x_speed, y_speed, yaw_speed = 0, 0, 0
    state = env.get_state()
    print(state)
    if keyboard.is_pressed("w"):
        y_speed += math.sin(((-state[2])/180)*math.pi)
        x_speed += math.cos(((-state[2])/180)*math.pi)

    if keyboard.is_pressed("s"):
        y_speed -= math.sin(((-state[2])/180)*math.pi)
        x_speed -= math.cos(((-state[2])/180)*math.pi)

    if keyboard.is_pressed("q"):
        y_speed -= math.sin(((-state[2]-90)/180)*math.pi)
        x_speed -= math.cos(((-state[2]-90)/180)*math.pi)

    if keyboard.is_pressed("e"):
        y_speed += math.sin(((-state[2]-90)/180)*math.pi)
        x_speed += math.cos(((-state[2]-90)/180)*math.pi)

    if keyboard.is_pressed("d"):
        yaw_speed += 1
    if keyboard.is_pressed("a"):
        yaw_speed -= 1
    env.robot.action(x_speed, y_speed, yaw_speed)


def precise_sleep(delay):
    start = time.perf_counter()
    while time.perf_counter() - start < delay:
        pass


# main thread
if __name__ == "__main__":
    robot_url = "ws://localhost:8080/api/ws"
    k = "toolkits/calibration_matrix.npy"
    d = "toolkits/distortion_coefficients.npy"
    cam_port = 0
    Env = env(robot_url, cam_port, k, d)
    Env.start()
    # Main event loop
    while True:
        # process_key_events(Env)
        # Consider adding a delay to prevent the loop from running too fast
        Env.robot.action(1, 0, 0)
        print(Env.get_state())
        precise_sleep(0.1)
