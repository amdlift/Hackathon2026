import json
import random
import cv2
from ultralytics import YOLO
import time

def update_json(original_json: str = 'lot_data.json', dest_json: str = 'data.json'):
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

    with open(original_json, 'r') as file:
        data = json.load(file)

    for lot in data["parking_lots"]:
        lot["occupancy"] = car_count

    return data


