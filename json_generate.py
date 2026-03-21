import json
import random

def update_json(original_json: str = 'lot_data.json', dest_json: str = 'data.json'):
    with open(original_json, 'r') as file:
        data = json.load(file)

    for lot in data["parking_lots"]:
        lot["occupancy"] = random.randrange(0, lot["capacity"])

    output = json.dumps(data, indent=2)
    print(output)

    with open(dest_json, "w") as file:
        json.dump(data, file, indent=2)

update_json()