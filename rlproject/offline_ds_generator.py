import json
import time
import keyboard
import math
from toolkits.communication import env
from toolkits.reward import cal_reward
from toolkits.stage import stage_update
import numpy as np

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

conter = 0
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

        observation = Env.get_state()
        action = process_key_events(Env)
        next_observation = Env.get_state()
        #get stage
        state, current_goal, stage = stage_update(next_observation)
        # get reward
        reward = cal_reward(state, current_goal)
        terminals = False

        data_point = {
            "stage": int(stage),
            "observations": observation.tolist(),
            "actions": action,
            "rewards": float(reward),
            "terminals": bool(terminals),
            "next_observations": next_observation.tolist()
        }
        data.append(data_point)  # append data point to data list
        if conter % 10 == 0:
            print("reward: ", reward)
            # print("state: ", state)
            print("stage: ", stage)
        time.sleep(0.1)

    print("data list: ", len(data))

    # Once out of the loop, write data to JSON
    with open("data/data.json", "w") as file:
        print("writing data to JSON")
        json.dump(data, file, indent=4)
