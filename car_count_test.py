import json
import os
import cv2
from ultralytics import YOLO

def car_counter(results, ROI_X1, ROI_Y1, ROI_X2, ROI_Y2, original_json='lot_data.json'):
    car_count = 0

    for box, cls, conf in zip(results[0].boxes.xyxy,
                              results[0].boxes.cls,
                              results[0].boxes.conf):
        if int(cls) != 2:
            continue

        if conf < 0.5:
            continue

        x1, y1, x2, y2 = map(int, box)
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        if 0 <= cx <= (ROI_X2 - ROI_X1) and 0 <= cy <= (ROI_Y2 - ROI_Y1):
            car_count += 1


    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, original_json)

    print(f"Reading from: {json_path}")  # debug line

    with open(original_json, 'r') as file:
        data = json.load(file)

    for lot in data["parking_lots"]:
        lot["occupancy"] = car_count

    return data