import json
from stage import stage_update
from reward import cal_reward
# from toolkits.stage import stage_update


file_path = "/home/howard/RLproject/rlproject/data/data_find_cube.json"
file_path_destination = "/home/howard/RLproject/rlproject/data/data.json"
# Load data from JSON file
with open(file_path, "r") as file:
    data = json.load(file)

# Iterate over each data point and update stage and reward
for data_point in data:
    next_observation = data_point["next_observations"]
    print(next_observation)
    
    # Get stage and reward using next_observation
    state, current_goal, stage = stage_update(next_observation)
    reward = cal_reward(state, current_goal)
    
    # Update stage and reward in the data point
    data_point["stage"] = stage
    print("stage: ", stage)
    data_point["rewards"] = reward

# Write updated data back to JSON file
with open(file_path_destination, "w") as file:
    json.dump(data, file, indent=4)