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

        if Config.mouse:
            # print("salam")
            msg = Message()
            msg.type = 'move mouse'
            msg.move_y = dy
            msg.move_x = dx

            Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))



        time.sleep(0.1)
        # time.sleep(1)

def interpret_blink(blink_found):
    if not Config.blink:
        return
    if blink_found[0] and blink_found[1]:
        msg = Message()
        msg.type = 'double click'
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))
        # pyautogui.click(clicks=2)
    elif blink_found[1]:
        msg = Message()
        msg.type = 'left click'
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))
        # pyautogui.click()
    elif blink_found[0]:
        msg = Message()
        msg.type = 'right click'
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))
        # pyautogui.click(button='right')


def main():
    global last_blink
    global blink_th
    global face_direction

    threading.Thread(target=move_mouse).start()

    cv2.namedWindow('controller')
    cap = cv2.VideoCapture(0)
    while True:
        retval, frame = cap.read()
        if retval == False:
            break
        cv2.imshow('controller', frame)

        blink_found = check_frame_for_blink(frame)
        # face_direction = get_frame_direction(frame)


        if Config.blink and time.time() - last_blink > blink_th:

            if any(blink_found):
                last_blink = time.time()
                interpret_blink(blink_found)

        key = cv2.waitKey(1)
        if key == ESCAPE_KEY_CODE:
            break

    cap.release()
    cv2.destroyAllWindows()
