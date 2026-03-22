import time
import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime
import sqlite3
from pathlib import Path

# ───────────────────────────────────────────────
# CONFIG – change these!
# ───────────────────────────────────────────────

DB_PATH          = Path("instance/parking.db")   # adjust if needed
MODEL            = YOLO("yolov8n.pt")            # or "yolov11n.pt" if you have it
VIDEO_SOURCE     = 0                             # 0=webcam, RTSP URL, or "test.mp4"
CONF_THRESH      = 0.45
CAR_CLASS_ID     = 2                             # COCO: 2 = car
UPDATE_INTERVAL  = 5                             # seconds

# One-time crop definition (x, y, width, height) – parking area only
# Run once, look at a frame, note rough coordinates (top-left + size)
CROP_RECT = (120, 180, 800, 500)                 # ← CHANGE THIS after testing!

# Your lot name in DB (must match exactly)
LOT_NAME = "Intermodal Facility"

# ───────────────────────────────────────────────
def point_in_rect(cx, cy, rect):
    x, y, w, h = rect
    return x <= cx <= x + w and y <= cy <= y + h

# ───────────────────────────────────────────────

cap = cv2.VideoCapture(VIDEO_SOURCE)
if not cap.isOpened():
    print("Cannot open video source")
    exit(1)

print(f"Starting single-lot counter – lot: {LOT_NAME}")
print(f"Crop area: {CROP_RECT}")
print(f"Updating DB every ~{UPDATE_INTERVAL} s. Ctrl+C to stop.\n")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame read failed – reconnecting...")
        cap.release()
        cap = cv2.VideoCapture(VIDEO_SOURCE)
        time.sleep(2)
        continue

    # Crop to parking area (removes irrelevant parts of image)
    x, y, w, h = CROP_RECT
    crop = frame[y:y+h, x:x+w]

    # Run YOLO only on crop (faster + ignores outside cars)
    results = MODEL(crop, conf=CONF_THRESH, classes=[CAR_CLASS_ID], verbose=False)

    count = 0
    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy().astype(int)
        for box in boxes:
            x1, y1, x2, y2 = box[:4]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            # Center must be inside crop (already cropped, but double-check)
            if point_in_rect(cx, cy, (0, 0, w, h)):
                count += 1

                # Optional debug: draw on crop
                # cv2.rectangle(crop, (x1,y1), (x2,y2), (0,255,0), 2)

    # Update DB
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE lot
            SET occupancy = ?
            WHERE name = ?
        """, (count, LOT_NAME))
        conn.commit()
        print(f"[{now_str}] {LOT_NAME}: {count} cars detected")

    except Exception as e:
        print("DB error:", e)
    finally:
        conn.close()

    # Optional: show debug window (only if running with display)
    # cv2.imshow(f"{LOT_NAME} – {count} cars", crop)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

    time.sleep(UPDATE_INTERVAL)

cap.release()
cv2.destroyAllWindows()