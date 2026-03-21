import json
import random

def update_json(lot_counts, original_json="lot_data.json"):
    with open(original_json, "r") as file:
        data = json.load(file)

    for lot in data["parking_lots"]:
        lot_code = lot["lot"]
        capacity = lot["capacity"]

        if lot_code in lot_counts:
            lot["occupancy"] = lot_counts[lot_code]
        else:
            lot["occupancy"] = random.randrange(0, capacity)

    return data