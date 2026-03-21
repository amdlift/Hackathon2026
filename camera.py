import cv2
from ultralytics import YOLO
import time

model = YOLO("yolov8n.pt")

TOTAL_SPOTS = 5

# Define your parking lot zone (x1, y1, x2, y2)
# These are pixel coordinates - we'll adjust them in a moment
ROI_X1, ROI_Y1 = 500, 500  # top left corner
ROI_X2, ROI_Y2 = 1000, 1000  # bottom right corner

cap = cv2.VideoCapture(1)  # your phone camera index

print("Press Q to quit, press S to print current ROI coordinates")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Draw the ROI box on screen in blue
    cv2.rectangle(frame, (ROI_X1, ROI_Y1), (ROI_X2, ROI_Y2), (255, 0, 0), 2)
    cv2.putText(frame, "Parking Lot Zone", (ROI_X1, ROI_Y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Only run YOLO inside the ROI
    roi_frame = frame[ROI_Y1:ROI_Y2, ROI_X1:ROI_X2]
    results = model(roi_frame, verbose=False)

    # Count cars only inside the ROI
    car_count = sum(1 for r in results[0].boxes.cls if int(r) == 2)
    available = max(TOTAL_SPOTS - car_count, 0)
    occupancy_pct = min(round((car_count / TOTAL_SPOTS) * 100), 100)
    is_full = car_count >= TOTAL_SPOTS

    # Draw detection boxes inside ROI
    annotated_roi = results[0].plot()
    frame[ROI_Y1:ROI_Y2, ROI_X1:ROI_X2] = annotated_roi

    # Display stats
    color = (0, 0, 255) if is_full else (0, 255, 0)
    cv2.putText(frame, f"Cars: {car_count}/{TOTAL_SPOTS}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, f"Occupancy: {occupancy_pct}%", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, f"Available: {available}", (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    if is_full:
        cv2.putText(frame, "LOT FULL!", (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow("Parking Lot Detection", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()