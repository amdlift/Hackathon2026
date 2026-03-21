import json
import time
import os
print("Current directory:", os.getcwd())
print("Files here:", os.listdir())
import cv2
import requests
from ultralytics import YOLO
from car_count_test import car_counter

# Camera and YOLO setup
model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(1)  # phone camera index

# ROI coordinates - adjust to fit a lot in camera
ROI_X1, ROI_Y1 = 100, 100
ROI_X2, ROI_Y2 = 500, 400

def get_status(percent_full):
    if percent_full >= 1:
        return "Full"
    elif percent_full >= 0.9:
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
        percent_full = occupied / capacity

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

def send_to_flask(processed_data):
    try:
        requests.post("http://127.0.0.1:5000/api/update-occupancy", json=processed_data)
        print("Sent data to Flask")
    except Exception as e:
        print(f"Could not send to Flask: {e}")

def main():
    print("Starting parking detection... Press Q to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't read camera")
            break

        # Draw ROI box
        cv2.rectangle(frame, (ROI_X1, ROI_Y1), (ROI_X2, ROI_Y2), (255, 0, 0), 2)

        # Crop to ROI and run YOLO
        roi_frame = frame[ROI_Y1:ROI_Y2, ROI_X1:ROI_X2]
        results = model(roi_frame, verbose=False)

        # Paste detections back
        annotated_roi = results[0].plot()
        frame[ROI_Y1:ROI_Y2, ROI_X1:ROI_X2] = annotated_roi

        # Count cars and update JSON
        data = car_counter(results, ROI_X1, ROI_Y1, ROI_X2, ROI_Y2)
        processed = process_parking_data(data)
        write_json_atomic("processed_data.json", processed)
        send_to_flask(processed)

        for lot in processed:
            print(lot)
        print("------------------------------------")

        # Show camera window
        cv2.imshow("Parking Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

main()