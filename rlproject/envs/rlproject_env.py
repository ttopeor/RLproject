import gym
from gym import error, spaces, utils
import numpy as np

class RLprojectEnv(gym.Env):
    
    def __init__(self):
        
        self.seed() # initialize the random number generator, if needed
        # define the action space
        action_low = -1
        action_high = 1
        action_dim = 3
        self.action_space = spaces.Box(low=action_low, high=action_high, shape=(action_dim,), dtype=float)
        
        # define the observation space
        self.observation_space = spaces.Dict(
            {
                "example": spaces.Box(0, 1, shape=(2,), dtype=float),   
            }
        )
        
        print('CustomEnv Environment initialized')
        
    def step(self, action):
        
        
        return observation, reward, done, info
    
    def reset(self):
        
        
        print('CustomEnv Environment reset')
        
    def render(self):
        # visualize the agent, no need in our case