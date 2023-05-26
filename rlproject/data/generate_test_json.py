import json
import random

data = []

for _ in range(10000):
    data_point = {
        "stage": random.randint(1, 2),
        "observations": [random.random() for _ in range(5)],
        "actions": [random.random() for _ in range(3)],
        "rewards": round(random.uniform(0, 1000), 2),
        # "masks": round(random.uniform(0, 1), 2),
        "terminals": random.choice([True, False]),
        "next_observations": [random.random() for _ in range(5)]
    }
    data.append(data_point)

with open("data.json", "w") as file:
    json.dump(data, file, indent=4)
