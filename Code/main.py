import threading

from speech_detection import main as speech_main
from video_controller import main as video_main
from network import main as network_main

# Start Speech Recognition
threading.Thread(target=speech_main).start()

# Start Video Capturing
# threading.Thread(target=video_main).start()

# Start Connecting to server
# threading.Thread(target=network_main).start()
