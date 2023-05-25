import json
import random

data = []

for _ in range(100):
    data_point = {
        "stage": random.randint(1, 2),
        "state": [random.random() for _ in range(5)],
        "action": [random.random() for _ in range(3)],
        "rewards": round(random.uniform(0, 1000), 2),
        "Mask": round(random.uniform(0, 1), 2),
        "Done": random.choice([True, False]),
        "Next State": [random.random() for _ in range(5)]
    }
    data.append(data_point)

with open("data.json", "w") as file:
    json.dump(data, file, indent=4)
