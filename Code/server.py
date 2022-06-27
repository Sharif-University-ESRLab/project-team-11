import socket, threading
import json
import pyautogui
import os
import PySimpleGUI as sg
import keyboard as kb

from message import Message

window = None

class ServerConfig:
    def __init__(self):
        self.mouse = False
        self.keyboard = False
        self.blink = False
        self.voice = False



# Receive bytes from a client
def read_message(client: socket.socket):
    msg = ""
    while True:
        ch = client.recv(1).decode("utf-8")
        msg += ch
        if ch == '}':
            break
    return msg


# Connect to the client and send messages from GUI
def handle_menu():
    print("Connected To Client")
    # sg.theme('Black')  # Add a touch of color
    # All the stuff inside your window.
    layout = [[sg.Button('Voice', button_color=('black', 'white'), key='voice but', size=(7, 1)),
               sg.Button('Blink', button_color=('black', 'white'), key='blink but', size=(7, 1)),
               sg.Button('Mouse', button_color=('black', 'white'), key='mouse but', size=(7, 1)),
               sg.Button('Keyboard', button_color=('black', 'white'), key='keyboard but', size=(7, 1))]]


    global window
    # Create the Window
    window = sg.Window('Tool Bar', layout, grab_anywhere=True)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        print(event, values)
        msg = Message()
        if event == sg.WIN_CLOSED:  # if user closes window
            break
        elif event == 'voice but':
            msg.type = 'Voice'
        elif event == 'blink but':
            msg.type = 'Blink'
        elif event == 'mouse but':
            msg.type = 'Mouse'
        elif event == 'keyboard but':
            msg.type = 'Keyboard'

        client.send(json.dumps(msg.__dict__).encode('utf-8'))



def update_buts():
    global window
    if window == None: return
    if server_config.blink:
        window.find_element('blink but').Update(button_color=('white', 'black'))
    else:
        window.find_element('blink but').Update(button_color=('black', 'white'))

    if server_config.mouse:
        window.find_element('mouse but').Update(button_color=('white', 'black'))
    else:
        window.find_element('mouse but').Update(button_color=('black', 'white'))

    if server_config.keyboard:
        window.find_element('keyboard but').Update(button_color=('white', 'black'))
    else:
        window.find_element('keyboard but').Update(button_color=('black', 'white'))

    if server_config.voice:
        window.find_element('voice but').Update(button_color=('white', 'black'))
    else:
        window.find_element('voice but').Update(button_color=('black', 'white'))

# Receive a message

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
            print("Shutdown instruction is called")
            # os.system("shutdown /s")
        elif msg.type == 'restart':
            print("restart instruction is called")
            # os.system("shutdown /r")
        elif msg.type == 'keyboard':
            kb.write(msg.typed_text)
        elif msg.type == 'change mouse':
            server_config.mouse = msg.is_on
        elif msg.type == 'change blink':
            server_config.blink = msg.is_on
        elif msg.type == 'change keyboard':
            server_config.keyboard = msg.is_on
        elif msg.type == 'change voice':
            server_config.voice = msg.is_on

        update_buts()



server_config = ServerConfig()

# Specify the connection settings
host = '0.0.0.0'
port = 8550

# Connect to a client
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1)

print("The server is waiting ...")

client, address = server.accept()
print(f"connected with{address}")

# Read messages from the client
thread = threading.Thread(target=read)
thread.start()

# Start GUI
menu_thread = threading.Thread(target=handle_menu)
menu_thread.start()
