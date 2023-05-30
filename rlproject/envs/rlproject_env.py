import gym
from gym import error, spaces, utils
import numpy as np
from rlproject.toolkits.communication import *
from rlproject.toolkits.reward import cal_reward
import random

class RLprojectEnv(gym.Env):
    
    def __init__(self):
        
        # robot handling
        robot_url = "ws://localhost:8080/api/ws"
        cam_port = 0
        # k = "calibration_matrix.npy"
        k = "/home/howard/RLproject/rlproject/toolkits/calibration_matrix.npy"
        # d = "distortion_coefficients.npy"
        d = "/home/howard/RLproject/rlproject/toolkits/distortion_coefficients.npy"
        self.Env = env(robot_url, cam_port, k, d)
        self.Env.start()

        self.seed() # initialize the random number generator, if needed
        # define the action space
        action_low = -1
        action_high = 1
        action_dim = 3
        self.action_space = spaces.Box(low=action_low, high=action_high, shape=(action_dim,), dtype=float)
        
        # define the observation space
        self.observation_space = spaces.Box(low=-10, high=10, shape=(5,), dtype=float) # TBD
        
        print('CustomEnv Environment initialized')
        
    def step(self, action):
        
        # take action
        self.Env.robot.action(action[0], action[1], action[2])
        
        # get state
        x, y, yaw, xc, yc = self.Env.get_state()
        
        # get reward
        reward = cal_reward(x, y, yaw, xc, yc, 0, 0)
        
        
        observation = [random.random() for _ in range(5)]
        reward = round(random.uniform(0, 1000), 2)
        done = False
        info = None #not sure about this one. Assign None temporaly
        
        return observation, reward, done, info
    
    def reset(self):
        
        
        print('CustomEnv Environment reset')
        
    # def render(self):
    #     # visualize the agent, no need in our case