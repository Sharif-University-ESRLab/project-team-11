import socket, threading
import json
import pyautogui
import os
import PySimpleGUI as sg

from message import Message


def read_message(client: socket.socket):
    msg = ""
    while True:
        ch = client.recv(1).decode("utf-8")
        msg += ch
        if ch == '}':
            break
    return msg


def handle_menu():
    print("HI")
    sg.theme('Black')  # Add a touch of color
    # All the stuff inside your window.
    layout = [[sg.Button('Voice', size=(7, 1)),
               sg.Button('Blink', size=(7, 1)),
               sg.Button('Mouse', size=(7, 1)),
               sg.Button('Keyboard', size=(7, 1))]]

    # Create the Window
    window = sg.Window('Tool Bar', layout, grab_anywhere=True)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        print(event, values)
        msg = Message()
        if event == sg.WIN_CLOSED:  # if user closes window
            break
        elif event == 'Voice':
            msg.type = 'Voice'
        elif event == 'Blink':
            msg.type = 'Blink'
        elif event == 'Mouse':
            msg.type = 'Mouse'
        elif event == 'Keyboard':
            msg.type = 'Keyboard'

        client.send(json.dumps(msg.__dict__).encode('utf-8'))




def read():
    while True:
        # try:
        data = read_message(client)
        M = json.loads(data)
        msg = Message(**M)
        print(msg.type)

        if msg.type == 'move mouse':
            pyautogui.moveRel(msg.move_y, msg.move_x)
        elif msg.type == 'right click':
            pyautogui.click(button='right')
        elif msg.type == 'left click':
            pyautogui.click()
        elif msg.type == 'double click':
            pyautogui.click(clicks=2)
        elif msg.type == 'shut down':
            os.system("shutdown /s")
        elif msg.type == 'restart':
            os.system("shutdown /r")
        elif msg.type == 'keyboard':
            # todo
            pass

        # except:
        # print("error has occured")
        # client.close()
        # break


host = '127.0.0.1'
port = 8550

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1)

client, address = server.accept()
print(f"connected with{address}")

thread = threading.Thread(target=read)
thread.start()

menu_thread = threading.Thread(target=handle_menu)
menu_thread.start()
