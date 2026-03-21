
from datetime import datetime
import json


with open("data.json", "r") as file:
    parking_data = json.load(file)

with open("data.json", "r") as file:
    capacity_data = json.load(file)


def get_status(percent_full):
    if percent_full >= 100:
        return "Full"
    else:
        return "Open"

def process_parking_data(raw_data, lot_capacities):
    processed = []

    for entry in raw_data:
        lot_id = entry["lot_id"]
        occupied = entry["count"]

        if lot_id not in lot_capacities:
            continue

        lot_info = lot_capacities[lot_id]
        capacity = lot_info["capacity"]
        available = max(capacity - occupied, 0)
        percent_full = (occupied / capacity)

        processed.append({
            "lot_id": lot_id,
            "lot_name": lot_info["name"],
            "total_capacity": capacity,
            "occupied_spaces": occupied,
            "available_spaces": available,
            "percent_full": round(percent_full, 2),
            "status": get_status(percent_full),
            "last_updated": datetime.now().isoformat()
        })

    return processed

results = process_parking_data(raw_data, lot_capacities)

for lot in results:
    print(lot)