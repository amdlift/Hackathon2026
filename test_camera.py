import cv2

for i in range(3):
    cap = cv2.VideoCapture(i)
    ret, frame = cap.read()
    if ret:
        cv2.imshow(f"Camera {i}", frame)

cv2.waitKey(5000)  # show all windows for 5 seconds
cv2.destroyAllWindows()