import cv2
from blink_detection import check_frame_for_blink
from head_orientation_triangles import get_frame_direction
from config import Config

from message import Message

import pyautogui
import threading
import time
import json

ESCAPE_KEY_CODE = 27

face_direction = ""

last_blink = 0
blink_th = 2

# Update the coordination of the mouse with respect to the current orientation of the user's face
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
            dy = -d
        elif direction == "Left":
            dy = +d

        if Config.mouse:
            msg = Message()
            msg.type = 'move mouse'
            msg.move_y = dy
            msg.move_x = dx

            Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))


        time.sleep(0.1)

# According to the eyes, the user is controlling the clicks (left / right / double)
def interpret_blink(blink_found):
    if not Config.blink:
        return
    if blink_found[0] and blink_found[1]:
        msg = Message()
        msg.type = 'double click'
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))

    elif blink_found[1]:
        msg = Message()
        msg.type = 'left click'
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))

    elif blink_found[0]:
        msg = Message()
        msg.type = 'right click'
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))



def main():
    global last_blink
    global blink_th
    global face_direction

    threading.Thread(target=move_mouse).start()

    # Initialize the video
    cv2.namedWindow('controller')
    cap = cv2.VideoCapture(0)
    while True:
        retval, frame = cap.read()
        if retval == False:
            break
        cv2.imshow('controller', frame)

        # If the user is controlling the mouse with his head, then find the orientation of the head
        if Config.mouse:
            face_direction = get_frame_direction(frame)

        # If user is controlling clicks with his eyes, then check if he is blinking
        if Config.blink and time.time() - last_blink > blink_th:
            blink_found = check_frame_for_blink(frame)
            if any(blink_found):
                last_blink = time.time()
                interpret_blink(blink_found)

        key = cv2.waitKey(1)
        if key == ESCAPE_KEY_CODE:
            break

    cap.release()
    cv2.destroyAllWindows()
