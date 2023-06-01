import json
from toolkits.reward import cal_reward
from toolkits.stage import stage_update

# Read the JSON data from the file
with open("data/data.json", "r") as file:
    data = json.load(file)

data_out = []
# Iterate over each dictionary in the list
for entry in data:
    observation = entry["observations"]
    action = entry["actions"]
    next_observation = entry["next_observations"]
    #get stage
    state, current_goal, stage = stage_update(next_observation)
    # get reward
    reward = cal_reward(state, current_goal)
    terminals = False

    data_point = {
            "stage": int(stage),
            "observations": observation,
            "actions": action,
            "rewards": float(reward),
            "terminals": bool(terminals),
            "next_observations": next_observation
        }
    data_out.append(data_point)
# Write the updated data back to the file
with open("data/data2.json", "w") as file:
    json.dump(data, file, indent=4)
