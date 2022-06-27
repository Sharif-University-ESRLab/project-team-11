import socket, threading
import json
from message import Message
from config import Config

#send a message to server in order to show some config is changed
def announce_config_change(changed_config, is_on):
    print('from announce:', changed_config, is_on)
    msg = Message()
    msg.type = changed_config
    msg.is_on = is_on
    Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))

# Receive bytes from a server
def read_message(client: socket.socket):
    msg = ""
    while True:
        ch = client.recv(1).decode("utf-8")
        msg += ch
        if ch == '}':
            break
    return msg


# Receive a message from a server/
def read():
    while True:
        # try:
        data = read_message(Config.client)
        M = json.loads(data)
        msg = Message(**M)

        if msg.type == 'Mouse':
            Config.mouse = not Config.mouse
            announce_config_change("change mouse", Config.mouse)
        elif msg.type == 'Keyboard':
            Config.keyboard = not Config.keyboard
            announce_config_change("change keyboard", Config.keyboard)
        elif msg.type == 'Blink':
            Config.blink = not Config.blink
            announce_config_change("change blink", Config.blink)
        elif msg.type == 'Voice':
            Config.speech_recognition = not Config.speech_recognition
            announce_config_change("change voice", Config.speech_recognition)


def main():
    # Specify the connection config
    f = open("server-config.txt", "r")
    lines = f.readlines()
    host_address = lines[0]

    print(host_address)
    host = '192.168.9.109'
    host = host_address

    port = 8550

    print("The client is searching ...")

    # Create a socket, and connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    print("The client is connected.")

    Config.client = client

    read()
