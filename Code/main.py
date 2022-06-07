import threading

from speech_detection import main as speech_main
from video_controller import main as video_main

threading.Thread(target=speech_main).start()
threading.Thread(target=video_main).start()