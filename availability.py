import json
from datetime import datetime
from json_generate import update_json   # 👈 import your generator


def get_status(percent_full):
    if percent_full >= 100:
        return "Full"
    elif percent_full >= 90:
        return "Nearly Full"
    else:
        return "Open"


def build_lot_capacities(lot_data):
    lot_capacities = {}

    for lot in lot_data["parking_lots"]:
        lot_name = lot["lot"]
        lot_capacities[lot_name] = lot["capacity"]

    return lot_capacities


def process_parking_data(occupancy_data, lot_capacities):
    processed = []

    for entry in occupancy_data["parking_lots"]:
        lot_name = entry["lot"]
        occupied = entry["occupancy"]

        if lot_name not in lot_capacities:
            continue

        capacity = lot_capacities[lot_name]
        available = max(capacity - occupied, 0)
        percent_full = (occupied / capacity) 

        processed.append({
            "lot_id": lot_name,
            "lot_name": lot_name,
            "total_capacity": capacity,
            "occupied_spaces": occupied,
            "available_spaces": available,
            "percent_full": round(percent_full, 2),
            "status": get_status(percent_full),
        })

    return processed


def main():

    update_json()   

    
    with open("lot_data.json", "r") as file:
        lot_data = json.load(file)

    with open("data.json", "r") as file:
        occupancy_data = json.load(file)

   
    lot_capacities = build_lot_capacities(lot_data)

    
    results = process_parking_data(occupancy_data, lot_capacities)

    
    with open("processed_data.json", "w") as file:
        json.dump(results, file, indent=2)

    
    for lot in results:
        print(lot)


main()