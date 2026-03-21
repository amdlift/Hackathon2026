import json
from json_generate import update_json


def get_status(percent_full):
    if percent_full >= 1:
        return "Full"
    elif percent_full >= 0.90:
        return "Nearly Full"
    else:
        return "Open"


def process_parking_data(data):
    processed = []

    for entry in data["parking_lots"]:
        lot_name = entry["lot"]
        occupied = entry["occupancy"]
        capacity = entry["capacity"]

        available = max(capacity - occupied, 0)
        percent_full = (occupied / capacity) if capacity > 0 else 0

        processed.append({
            "lot_id": lot_name,
            "lot_name": lot_name,            
            "capacity": capacity,
            "occupied": occupied,
            "available": available,
            "percent_full": round(percent_full, 2),
            "status": get_status(percent_full),
        })

    return processed


def main():
    
    data = update_json()

    
    results = process_parking_data(data)

    with open("processed_data.json", "w") as file:
        json.dump(results, file, indent=2)

    # 🖥 print
    for lot in results:
        print(lot)


main()