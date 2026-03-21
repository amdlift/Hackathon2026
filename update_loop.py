import json
import time
import os
from json_generate import update_json

def get_status(percent_full):
    if percent_full >= 1:
        return "Full"
    elif percent_full >= .9:
        return "Nearly Full"
    else:
        return "Open"

def write_json_atomic(filename, data):
    temp_filename = filename + ".tmp"

    with open(temp_filename, "w") as file:
        json.dump(data, file, indent=2)

    os.replace(temp_filename, filename)

def process_parking_data(data):
    processed = []

    for entry in data["parking_lots"]:
        lot_name = entry["lot"]
        occupied = entry["occupancy"]
        capacity = entry["capacity"]

        available = max(capacity - occupied, 0)
        percent_full = (occupied / capacity)

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
    
    while True:
        data = update_json()

        results = process_parking_data(data)

        write_json_atomic("processed_data.json", results)

        # for lot in results:
        #     print(lot)

        # print("------------------------------------")

        time.sleep(1)

if __name__ == '__main__':
    main()