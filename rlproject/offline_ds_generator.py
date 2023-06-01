import json
import time
import keyboard
import math
from toolkits.communication import env


def process_key_events(env):
    x_speed, y_speed, yaw_speed = 0, 0, 0
    state = env.get_state()
    #print([round(x, 2) if isinstance(x, (int, float)) else x for x in state])
    if keyboard.is_pressed("w"):
        y_speed += math.sin(((-state[2]) / 180) * math.pi)
        x_speed += math.cos(((-state[2]) / 180) * math.pi)

    if keyboard.is_pressed("s"):
        y_speed -= math.sin(((-state[2]) / 180) * math.pi)
        x_speed -= math.cos(((-state[2]) / 180) * math.pi)

    if keyboard.is_pressed("q"):
        y_speed -= math.sin(((-state[2] - 90) / 180) * math.pi)
        x_speed -= math.cos(((-state[2] - 90) / 180) * math.pi)

    if keyboard.is_pressed("e"):
        y_speed += math.sin(((-state[2] - 90) / 180) * math.pi)
        x_speed += math.cos(((-state[2] - 90) / 180) * math.pi)

    if keyboard.is_pressed("d"):
        yaw_speed += 1
    if keyboard.is_pressed("a"):
        yaw_speed -= 1
    env.robot.action(x_speed, y_speed, yaw_speed)
    return [x_speed, y_speed, yaw_speed]


# main thread
if __name__ == "__main__":
    robot_url = "ws://localhost:8080/api/ws"
    k = "toolkits/calibration_matrix.npy"
    d = "toolkits/distortion_coefficients.npy"
    cam_port = 0
    Env = env(robot_url, cam_port, k, d)
    Env.start()
    # Main event loop
    data = []
    while True:
        # Check if 'p' is pressed
        if keyboard.is_pressed('p'):
            break

        observation = env.get_state()
        action = process_key_events(Env)
        next_observation = env.get_stage()
        stage = get_stage(observations)
        reward = get_reward(next_observations)
        terminals = False

        data_point = {
            "stage": stage,
            "observations": observation,
            "actions": action,
            "rewards": reward,
            "terminals": terminals,
            "next_observation": next_observation
        }
        data.append(data_point)  # append data point to data list
        time.sleep(0.1)

    # Once out of the loop, write data to JSON
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)
