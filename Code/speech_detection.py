import logging
import speech_recognition as sr
import json,pyaudio,wave,os
from urllib.request import urlopen,Request
from config import Config
import pyautogui
import keyboard as kb

r = sr.Recognizer()
source = sr.Microphone()


def check_for_speech_recognition_enabling(text):
    if "صدا روشن" == text:
        Config.speech_recognition = True
        logging.info("speech recognition is activated")
    if "صدا خاموش" == text:
        Config.speech_recognition = False
        logging.info("speech recognition is deactivated")


def check_for_speech_commands(text):
    if "کلیک راست" == text:
        logging.info("right click")
        pyautogui.click(button='right')

    if "کلیک چپ" == text:
        logging.info("left click")
        pyautogui.click()

    if "کلیک جفت" == text:
        logging.info("double click")
        pyautogui.click(clicks=2)

    check_for_system_commands(text)
    check_for_keyboard_commands(text)

    if "موس روشن" == text:
        Config.mouse = True
    if "موس خاموش" == text:
        Config.mouse = False

    if "چشمک روشن" == text:
        Config.blink = True
    if "چشمک خاموش" == text:
        Config.blink = False


def check_for_system_commands(text):
    if "راه اندازی مجدد" == text:
        print('dare restart misheeee \n')
        # os.system("shutdown /r")
    if "خاموش" == text:
        print("dare shut down misheeee")
        # os.system("shutdown /s")  # shutdown

def check_for_keyboard_commands(text):
    if "کیبورد خاموش" ==  text:
        Config.keyboard = False

    if Config.keyboard:
        kb.write(text)

    if "کیبورد روشن" == text:
        Config.keyboard = True

def interpret_text(text):
    check_for_speech_recognition_enabling(text)

    if not Config.speech_recognition:
        return
    check_for_speech_commands(text)


def callback(recognizer, audio):  # this is called from the background thread
    try:
        print('------------------')
        print('The audio has been received.')
        print('Start processing:')
        text = recognizer.recognize_google(audio, language='fa')

        print(text)
        print('------------------')
        interpret_text(text)

    except sr.UnknownValueError:
        print("Oops! Didn't catch that")


def start_recognizer():
    r.listen_in_background(source, callback)
    while True:
        pass

def main():
    logging.basicConfig(filename='speech.log', level=logging.INFO)
    start_recognizer()
