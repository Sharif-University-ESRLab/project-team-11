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

r = sr.Recognizer()
source = sr.Microphone()
speech_recognition = False
mouse = False
keyboard = False


def interpret_text(text):
    global speech_recognition
    if "activate speech recognition" in text:
        speech_recognition = True
    if "deactivate speech recognition" in text:
        speech_recognition = False
    if not speech_recognition:
        return

    if "right-click" in text:
        pass
    if "left-click" in text:
        pass
    if "double click" in text:
        pass
    if "start keyboard" in text:
        pass
    if "exit keyboard" in text:
        pass
    if "start mouse" in text:
        pass
    if "exit mouse" in text:
        pass
    if "restart" in text:
        pass
    if "shut down" in text:
        pass


def callback(recognizer, audio):  # this is called from the background thread
    try:
        print('------------------')
        print('The audio has been received.')
        print('Start processing:')
        text = recognizer.recognize_google(audio)
        text = text.lower()
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
