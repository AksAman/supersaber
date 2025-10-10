from typing import Literal

import pyaudio

sleep_between_frames = False
RMS_THRESHOLD = 7
# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
AUDIO_DEVICE = 0
FPS = 120
FFT_STEP = 20
SMOOTHING_ALPHA = 0.3

MQTT_TOPIC = "audio-values"

WLED_TOPIC = "wled/154cef"
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1885

UDP_BROKER_HOST = "192.168.0.102"
UDP_BROKER_PORT = 1234

BOOSTER = 10
SONG_TYPE: Literal["slow", "fast"] = "fast"
if SONG_TYPE == "slow":
    FPS = 120
    FFT_STEP = 2
    SMOOTHING_ALPHA = 0.1
elif SONG_TYPE == "fast":
    FPS = 120
    FFT_STEP = 4
    SMOOTHING_ALPHA = 0.4
