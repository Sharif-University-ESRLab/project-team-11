import cv2
from blink_detection import check_frame_for_blink
from head_orientation_triangles import get_frame_direction
from speech_detection import start_recognizer

import pyautogui
import threading
import time


ESCAPE_KEY_CODE = 27

face_direction = ""

def move_mouse():
    while True:
        direction = face_direction
    
        dx = 0
        dy = 0
        d = 8
        if direction == "Up":
            dx = -d
        elif direction == "Down":
            dx = d
        elif direction == "Right":
            dy = d
        elif direction == "Left":
            dy = -d

        pyautogui.moveRel(dy, dx)

        # print(direction)

        time.sleep(0.001)

threading.Thread(target=move_mouse).start()
threading.Thread(target=start_recognizer).start()


cv2.namedWindow('controller')
cap = cv2.VideoCapture(0)
while True:
    retval, frame = cap.read()
    if retval == False:
        break
    cv2.imshow('controller', frame)

    blink_found = check_frame_for_blink(frame)
    direction = get_frame_direction(frame)

    print(blink_found, direction)

    key = cv2.waitKey(1)
    if key == ESCAPE_KEY_CODE:
        break

cap.release()
cv2.destroyAllWindows()
