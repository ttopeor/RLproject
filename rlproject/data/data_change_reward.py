import json
from toolkits.stage import stage_update
from toolkits.reward import cal_reward

# Load data from JSON file
with open("data.json", "r") as file:
    data = json.load(file)

# Iterate over each data point and update stage and reward
for data_point in data:
    next_observation = data_point["next_observations"]
    
    # Get stage and reward using next_observation
    state, current_goal, stage = stage_update(next_observation)
    reward = cal_reward(state, current_goal)
    
    # Update stage and reward in the data point
    data_point["stage"] = stage
    data_point["rewards"] = reward

# Write updated data back to JSON file
with open("data.json", "w") as file:
    json.dump(data, file, indent=4)