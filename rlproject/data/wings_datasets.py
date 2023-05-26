# import d4rl
# import gym
import numpy as np
import json

from rlproject.data.dataset import Dataset


class WingsDataset(Dataset):
    def __init__(self, file_path: 'r', clip_to_eps: bool = True, eps: float = 1e-5):
        with open(file_path, 'r') as f:
            raw_data = json.load(f)
            dataset_dict = self.transform_json_data(raw_data)
            # print(dataset_dict) #delete me

        if clip_to_eps:
            lim = 1 - eps
            dataset_dict["actions"] = np.clip(dataset_dict["actions"], -lim, lim)

        dones = np.full_like(dataset_dict["rewards"], False, dtype=bool)

        for i in range(len(dones) - 1):
            if (
                np.linalg.norm(
                    dataset_dict["observations"][i + 1]
                    - dataset_dict["next_observations"][i]
                )
                > 1e-6
                or dataset_dict["terminals"][i] == 1.0
            ):
                dones[i] = True

        dones[-1] = True

        dataset_dict["masks"] = 1.0 - dataset_dict["terminals"]
        del dataset_dict["terminals"]

        for k, v in dataset_dict.items():
            dataset_dict[k] = v.astype(np.float32)

        dataset_dict["dones"] = dones

        super().__init__(dataset_dict)

    def transform_json_data(self, json_data):
        transformed_data = {}

        # Convert observations, actions, and next_observations to numpy arrays
        transformed_data['observations'] = np.array([item['observations'] for item in json_data], dtype=np.float32)
        transformed_data['actions'] = np.array([item['actions'] for item in json_data], dtype=np.float32)
        transformed_data['next_observations'] = np.array([item['next_observations'] for item in json_data], dtype=np.float32)

        # Convert rewards to a numpy array
        transformed_data['rewards'] = np.array([item['rewards'] for item in json_data], dtype=np.float32)

        # Convert terminals to a numpy array
        transformed_data['terminals'] = np.array([item['terminals'] for item in json_data], dtype=bool)
  
        return transformed_data
