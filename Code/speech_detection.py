import logging
import speech_recognition as sr
import json,pyaudio,wave,os
from config import Config


from message import Message

# Config the Microphone and its sensitivity
r = sr.Recognizer()
r.energy_threshold = 1000
source = sr.Microphone()

def get_similarity(a, b):
    s = list(set(a) & set(b))
    return len(s) / (len(a) + len(b))


def correct_input(inp):
    if Config.keyboard:
        return inp, 1
    commands = ["صدا روشن", "صدا خاموش", "کلیک راست", "کلیک چپ", "کلیک جفت", "موس روشن", "موس خاموش",
                "چشمک روشن", "چشمک خاموش", "راه اندازی مجدد", "خاموش", "کیبورد روشن", "کیبورد خاموش"]

    best_match = ""
    best_score = 0

    for cmd in commands:
        score = get_similarity(cmd, inp)
        if score > best_score:
            best_match = cmd
            best_score = score

    return best_match, best_score


# Check if the given text is activating/deactivating the voice assistant
def check_for_speech_recognition_enabling(text):
    if "صدا روشن" == text:
        Config.speech_recognition = True
        logging.info("speech recognition is activated")
    if "صدا خاموش" == text:
        Config.speech_recognition = False
        logging.info("speech recognition is deactivated")


# Interpret the given text
def check_for_speech_commands(text):
    #  Right Click
    if "کلیک راست" == text:
        logging.info("right click")
        msg = Message()
        msg.type = 'right click'
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))

    # Left Click
    if "کلیک چپ" == text:
        logging.info("left click")
        msg = Message()
        msg.type = 'left click'
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))

    # Double Click
    if "کلیک جفت" == text:
        logging.info("double click")
        msg = Message()
        msg.type = 'double click'
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))

    # Restart / Shutdown
    check_for_system_commands(text)

    # Activating / Deactivating the keyboard
    check_for_keyboard_commands(text)

    # Activating / Deactivating the Mouse
    if "موس روشن" == text:
        Config.mouse = True
    if "موس خاموش" == text:
        Config.mouse = False

    # Activating / Deactivating the blink detector
    if "چشمک روشن" == text:
        Config.blink = True
    if "چشمک خاموش" == text:
        Config.blink = False


def check_for_system_commands(text):
    if "راه اندازی مجدد" == text:
        msg = Message()
        msg.type = 'restart'
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))

    if "خاموش" == text:
        msg = Message()
        msg.type = 'shut down'
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))


def check_for_keyboard_commands(text):
    if "کیبورد خاموش" ==  text:
        Config.keyboard = False

    if Config.keyboard:
        msg = Message()
        msg.type = 'keyboard'
        msg.typed_text = text
        Config.client.send(json.dumps(msg.__dict__).encode('utf-8'))
        # kb.write(text)

    if "کیبورد روشن" == text:
        Config.keyboard = True

# This Function checks if the given text is activating the voice assistant
# If the voice assistant is enabled, then the given text will be interpreted
def interpret_text(text):
    check_for_speech_recognition_enabling(text)

    if not Config.speech_recognition:
        return
    check_for_speech_commands(text)


# Whenever a user speaks, the listener recognizes the audio, and gives it to this function
# This function is called from the background thread
def callback(recognizer, audio):
    try:
        print('------------------')
        print('The audio has been received.')
        print('Start processing:')
        text = recognizer.recognize_google(audio, language='fa')
        print(f"initial text is : {text}")

        text, similarity = correct_input(text)
        print(f"improved text :{text}")

        print('------------------')

        if similarity > 0.3:
            interpret_text(text)

    except sr.UnknownValueError:
        print("Oops! Didn't catch that")


def start_recognizer():
    print("The microphone is working")

    # Initialize a listener which activates when a user speaks
    r.listen_in_background(source, callback)

    # The program should be continued for ever
    while True:
        pass

# Start Speech Recognition
def main():
    logging.basicConfig(filename='speech.log', level=logging.INFO)
    start_recognizer()
