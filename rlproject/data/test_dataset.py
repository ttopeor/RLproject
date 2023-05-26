# import d4rl
# import gym
import numpy as np
from wings_datasets import WingsDataset

path = "/home/howard/rlpd/data_test/data.json"

ds = WingsDataset(path)
print(type(ds))
print(ds)


sample_ds = ds.sample(1)

print(type(sample_ds))
print(sample_ds)