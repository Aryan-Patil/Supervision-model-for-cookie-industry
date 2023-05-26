from subprocess import call
import cv2


def triangle_rejected():
    call(["python", "triangle_rejected.py"])


def triangle_size():
    call(["python", "triangle-size.py"])


def triangle_accepted():
    call(["python", "triangle_accepted.py"])


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
    if hue_value < 12:
        color = "BROWN"
        triangle_rejected()
    elif hue_value < 33:
        color = "YELLOW"
        triangle_accepted()


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
