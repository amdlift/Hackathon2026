import json
import random

def update_json(original_json: str = 'lot_data.json', dest_json: str = 'data.json'):
    with open(original_json, 'r') as file:
        data = json.load(file)

    for lot in data["parking_lots"]:
        lot["occupancy"] = random.randrange(0, lot["capacity"])

    return data