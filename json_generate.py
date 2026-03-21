import json
import random

with open('lot_data.json', 'r') as file:
    data = json.load(file)

for lot in data["parking_lots"]:
    lot["occupancy"] = random.randrange(0, lot["capacity"])

output = json.dumps(data, indent=2)
print(output)

with open("data.json", "w") as file:
    json.dump(data, file, indent=2)