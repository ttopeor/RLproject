import gym
from gym import error, spaces, utils
import numpy as np
from rlproject.toolkits.communication import *
from rlproject.toolkits.reward import cal_reward
from rlproject.toolkits.stage import stage_update
import random
from typing import Tuple

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
        action_low = -10
        action_high = 10
        action_dim = 3
        self.action_space = spaces.Box(low=action_low, high=action_high, shape=(action_dim,), dtype=float)
        # self.action_space = spaces.Box(low=-float('inf'), high=float('inf'), shape=(action_dim,), dtype=float)
        
        # define the observation space
        # self.observation_space = spaces.Box(low=-float('inf'), high=float('inf'), shape=(5,), dtype=float) # TBD
        self.observation_space = spaces.Box(low=-1000.0, high=1000.0, shape=(5,), dtype=float) # TBD
        print('CustomEnv Environment initialized')
        
    def step(self, action) -> Tuple[np.array, float, bool, dict]:
        
        # take action
        self.Env.robot.action(action[0], action[1], action[2])
        
        # get state
        state = self.Env.get_state()
        # print("For debug - state(in step)", state, np.shape(state), type(state)) #delete me


        #get stage
        state, current_goal, current_stage = stage_update(state)

        # get reward
        reward = cal_reward(state, current_goal)
        
        
        # observation = [random.random() for _ in range(5)]
        # reward = round(random.uniform(0, 1000), 2)
        # done = False
        # info = None #not sure about this one. Assign None temporaly

        observation = state
        # print("For debug - observation(in step)", observation, np.shape(observation), type(observation)) #delete me
        done = False
        info = None #not sure about this one. Assign None temporaly
        
        return observation, reward, done, info
    
    def reset(self):
        # print("For debug - env reset") #delete me
        # get the first observation
        state = self.Env.get_state()
        # print("For debug - env reset state = ", state, np.shape(state)) #delete me
        #check if the state is None
        if any(element is None for element in state):
            # print("error from stage.py - No state yet")
            # print("using fake random state ")
            state = np.array([random.random() for _ in range(5)])
        # print("For debug - env reset state = ", state, np.shape(state)) #delete me

        return state
        # print('CustomEnv Environment reset')
        
    # def render(self):
    #     # visualize the agent, no need in our case