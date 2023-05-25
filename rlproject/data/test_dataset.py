import d4rl
import gym
import numpy as np
from d4rl_datasets import D4RLDataset

env = gym.make("halfcheetah-expert-v2")

ds = D4RLDataset(env)

print(type(ds))