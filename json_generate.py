import json

with open('lot_data.json', 'r') as file:
    data = json.load(file)

for lot in data["parking_lots"]:
    lot["occupancy"] = 20

output = json.dumps(data, indent=2)
print(output)