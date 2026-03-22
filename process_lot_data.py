import json
import time
import os
import cv2
from collections import deque
from ultralytics import YOLO
from json_generate import update_json
from camera_manager import get_frame, get_lot_counts, SSTL_ROI

CAPACITY = 5
recent_counts = deque(maxlen=5)
last_update = time.time()

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
        percent_full = (occupied / capacity) * 100 if capacity > 0 else 0
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
    global last_update
    print("Starting... Press Q to quit")

    while True:
        # Grab frame from camera
        frame = get_frame()
        if frame is None:
            print("Can't read camera")
            break

        # Run YOLO on full frame for display
        from camera_manager import model
        results = model(frame, verbose=False)
        annotated_frame = results[0].plot()

        # Draw ROI box
        x1, y1, x2, y2 = SSTL_ROI
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(annotated_frame, "Parking Zone", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Count cars in ROI
        lot_counts = get_lot_counts(frame)
        car_count = lot_counts.get("SSL", 0)
        recent_counts.append(car_count)
        smoothed = round(sum(recent_counts) / len(recent_counts))

        # Display stats
        available = max(CAPACITY - smoothed, 0)
        pct = min(round((smoothed / CAPACITY) * 100), 100)
        is_full = smoothed >= CAPACITY
        color = (0, 0, 255) if is_full else (0, 255, 0)

        cv2.putText(annotated_frame, f"Cars: {smoothed}/{CAPACITY}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(annotated_frame, f"Occupancy: {pct}%", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(annotated_frame, f"Available: {available}", (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        if is_full:
            cv2.putText(annotated_frame, "LOT FULL!", (20, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        cv2.imshow("SSL Parking Lot", annotated_frame)

        # Update JSON every 5 seconds
        if time.time() - last_update >= 5:
            data = update_json({"SSL": smoothed})
            results_processed = process_parking_data(data)
            write_json_atomic("processed_data.json", {"parking_lots": results_processed})
            for lot in results_processed:
                print(lot)
            print("------------------------------------")
            last_update = time.time()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

main()