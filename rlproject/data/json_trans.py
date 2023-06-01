import json

# Read the JSON data from the file
with open("data.json", "r") as file:
    data = json.load(file)

# Iterate over each dictionary in the list
for entry in data:
    # Check if "next_observation" exists in the dictionary
    if "next_observation" in entry:
        # Rename the key to "next_observations"
        entry["next_observations"] = entry.pop("next_observation")

# Write the updated data back to the file
with open("data2.json", "w") as file:
    json.dump(data, file, indent=4)
