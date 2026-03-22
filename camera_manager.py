import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

SSTL_CAMERA_INDEX = 1
SSTL_ROI = (500, 500, 1000, 1000)

cap = cv2.VideoCapture(SSTL_CAMERA_INDEX)

if not cap.isOpened():
    print(f"WARNING: Could not open camera at index {SSTL_CAMERA_INDEX}")

def count_cars_in_roi(frame, roi):
    x1, y1, x2, y2 = roi
    roi_frame = frame[y1:y2, x1:x2]
    results = model(roi_frame, verbose=False)

    car_count = 0
    roi_width = x2 - x1
    roi_height = y2 - y1

    for box, cls, conf in zip(
        results[0].boxes.xyxy,
        results[0].boxes.cls,
        results[0].boxes.conf
    ):
        if int(cls) != 2:
            continue
        if float(conf) < 0.5:
            continue

        bx1, by1, bx2, by2 = map(int, box)
        cx = (bx1 + bx2) // 2
        cy = (by1 + by2) // 2

        if 0 <= cx <= roi_width and 0 <= cy <= roi_height:
            car_count += 1

    return car_count

def get_frame():
    ret, frame = cap.read()
    if not ret:
        return None
    return frame

def get_lot_counts(frame):
    if frame is None:
        return {"SSL": 0}
    return {"SSL": count_cars_in_roi(frame, SSTL_ROI)}