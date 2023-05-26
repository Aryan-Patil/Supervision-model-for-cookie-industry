from subprocess import call
import cv2


def circle_rejected():
    call(["python", "circle_rejected.py"])


def circle_size():
    call(["python", "circle-size.py"])


def circle_accepted():
    call(["python", "circle_accepted.py"])


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    _, frame = cap.read()
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    height, width, _ = frame.shape

    cx = int(width / 2)
    cy = int(height / 2)

    # Pick pixel value
    pixel_center = hsv_frame[cy, cx]
    hue_value = pixel_center[0]
    color = "Undefined"
    if hue_value < 2:
        color = "BROWN"
        circle_rejected()
    else:
        color = "YELLOW"
        circle_accepted()


    pixel_center_bgr = frame[cy, cx]
    cv2.rectangle(frame, (cx - 220, 10), (cx + 200, 120), (255, 255, 255), -1)
    cv2.putText(frame, color, (cx - 200, 100), 0, 3, (0, 0, 0), 5)
    cv2.circle(frame, (cx, cy), 5, (25, 25, 25), 3)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
cap.release()
cv2.destroyAllWindows()

