import json
import time
import os
from json_generate import update_json
from camera_manager import get_lot_counts



def get_status(percent_full):
    if percent_full >= 100:
        return "Full"
    elif percent_full >= 90:
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
        lot_name = entry["name"]
        lot_id = entry["lot"]
        occupied = entry["occupancy"]
        capacity = entry["capacity"]

        available = max(capacity - occupied, 0)
        percent_full = (occupied / capacity) * 100 

        processed.append({
            "lot_id": lot_id,
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

        # real counts only for lots that currently have cameras
        lot_counts = get_lot_counts()

        # hybrid fill: real counts where available, random elsewhere
        data = update_json(lot_counts)

        results = process_parking_data(data)

        write_json_atomic("processed_data.json", data)

        for lot in results:
            print(lot)

        print("------------------------------------")

        time.sleep(10)

main()