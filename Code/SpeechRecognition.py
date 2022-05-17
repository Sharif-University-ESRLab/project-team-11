# import time
# import speech_recognition as sr
#
# r = sr.Recognizer()
#
# with sr.Microphone() as source:
#     # read the audio data from the default microphone
#     while True:
#         print('start')
#         audio_data = r.record(source, duration=2)
#         print('finish')
#         print("Recognizing...")
#     # convert speech to text
#     try:
#         text = r.recognize_google(audio_data)
#         print(text)
#     except:
#         print('project tamoom shod')
# # harvard = sr.AudioFile('mohammad.wav')
# # with harvard as source:
# #     audio = r.record(source)
# #     print('sa lam')
# #     t1 = time.time()
# #     print(r.recognize_google(audio))
# #     print(time.time() - t1)
# #     print('khodafez')
# # ...
# # print(r.recognize_google())
import speech_recognition as sr
import json,pyaudio,wave,os
from urllib.request import urlopen,Request

import pyautogui

r = sr.Recognizer()
source = sr.Microphone()
speech_recognition = False
mouse = False
keyboard = False

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


def interpret_text(text):
    global speech_recognition
    if "activate speech recognition" in text:
        speech_recognition = True
    if "deactivate speech recognition" in text:
        speech_recognition = False
    if not speech_recognition:
        return

    if "right-click" in text:
        pyautogui.click(button='right')
    if "left-click" in text:
        pyautogui.click()
    if "double click" in text:
        pyautogui.click(clicks=2)
    if "start keyboard" in text:
        pass
    if "exit keyboard" in text:
        pass
    if "start mouse" in text:
        pass
    if "exit mouse" in text:
        pass
    if "restart" in text:
        os.system("shutdown /r")
    if "shut down" in text:
        os.system("shutdown /s")  # shutdown


def callback(recognizer, audio):  # this is called from the background thread
    try:
        print('------------------')
        print('The audio has been received.')
        print('Start processing:')
        # text = recognizer.recognize_google(audio)
        # text = text.lower()
        text = RecognizerClass.sendRequest(audio)
        print(text)
        print('------------------')

        interpret_text(text)

    except sr.UnknownValueError:
        print("Oops! Didn't catch that")


def start_recognizer():
    r.listen_in_background(source, callback)
    while True:
        pass


start_recognizer()
