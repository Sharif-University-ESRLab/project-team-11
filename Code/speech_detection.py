import logging
import speech_recognition as sr
import json,pyaudio,wave,os
from urllib.request import urlopen,Request

import pyautogui

r = sr.Recognizer()
source = sr.Microphone()
# speech_recognition = False
speech_recognition = True
mouse = False
# keyboard = False
keyboard = True

class RecognizerClass:
    def sendRequest(fileContent):
        GOOGLEAPIKEY = "INSERT GOOGLE API KEY HERE :)"
        APIURL = 'https://www.google.com/speech-api/v2/recognize?xierr=1&client=chromium&lang=fa-IR&key=' + GOOGLEAPIKEY
        headerParameters = {'Content-Type': 'audio/x-flac; rate=12000'}
        # fileContent = open(audioFile, 'rb')
        fileData = fileContent.read()
        requestParam = Request(APIURL, data=fileData, headers=headerParameters)
        response = urlopen(requestParam)
        responseByte = response.read()
        responseString = responseByte.decode("utf-8")
        if len(responseString) > 16:
            responseString = responseString.split('\n', 1)[1]
            a = json.loads(responseString)['result'][0]
            transcript = ""
            confidence = 0
            if 'confidence' in a['alternative'][0]:
                confidence = a['alternative'][0]['confidence']
                confidence = confidence * 100
            if 'transcript' in a['alternative'][0]:
                transcript = a['alternative'][0]['transcript']
                return transcript

def check_for_speech_recognition_enabling(text):
    global speech_recognition
    if "صدا روشن" in text:
        speech_recognition = True
        logging.info("speech recognition is activated")
    if "صدا خاموش" in text:
        speech_recognition = False
        logging.info("speech recognition is deactivated")


def check_for_speech_commands(text):
    if "کلیک راست" in text:
        logging.info("right click")
        pyautogui.click(button='right')

    if "کلیک چپ" in text:
        logging.info("left click")
        pyautogui.click()

    if "کلیک جفت" in text:
        logging.info("double click")
        pyautogui.click(clicks=2)

    check_for_system_commands(text)
    check_for_keyboard_commands(text)

    if "start mouse" in text:
        pass
    if "exit mouse" in text:
        pass


def check_for_system_commands(text):
    if "راه اندازی مجدد" in text:
        print('dare restart misheeee \n')
        # os.system("shutdown /r")
    if "خاموش" in text:
        print("dare shut down misheeee")
        # os.system("shutdown /s")  # shutdown


def check_for_keyboard_commands(text):
    global keyboard
    # if keyboard:
    #     print(text)
    #     pyautogui.typewrite('سلام')

    if "کیبورد روشن" in text:
        keyboard = True

    if "کیبورد خاموش" in text:
        keyboard = False



def interpret_text(text):
    check_for_speech_recognition_enabling(text)

    if not speech_recognition:
        return
    check_for_speech_commands(text)


def callback(recognizer, audio):  # this is called from the background thread
    try:
        print('------------------')
        print('The audio has been received.')
        print('Start processing:')
        text = recognizer.recognize_google(audio, language='fa')
        # text = text.lower()
        # text = RecognizerClass.sendRequest(audio)
        print(text)
        print('------------------')

        interpret_text(text)

    except sr.UnknownValueError:
        print("Oops! Didn't catch that")


def start_recognizer():
    r.listen_in_background(source, callback)
    while True:
        pass

if __name__ == "__main__":
    logging.basicConfig(filename='speech.log', level=logging.INFO)
    start_recognizer()

