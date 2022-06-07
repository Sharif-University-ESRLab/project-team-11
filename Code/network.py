import socket, threading
import json
from message import Message
from config import Config


# Receive bytes from a server
def read_message(client: socket.socket):
    msg = ""
    while True:
        ch = client.recv(1).decode("utf-8")
        msg += ch
        if ch == '}':
            break
    return msg


# Receive a message from a server
def read():
    while True:
        # try:
        data = read_message(Config.client)
        M = json.loads(data)
        msg = Message(**M)

        if msg.type == 'Mouse':
            Config.mouse = not Config.mouse
        elif msg.type == 'Keyboard':
            Config.keyboard = not Config.keyboard
        elif msg.type == 'Blink':
            Config.blink = not Config.blink
        elif msg.type == 'Voice':
            Config.speech_recognition = not Config.speech_recognition


def main():
    # Specify the connection config
    host = '127.0.0.1'
    port = 8550

    # Create a socket, and connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    Config.client = client

    read()
