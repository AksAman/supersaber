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
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1885


SONG_TYPE: Literal["slow", "fast"] = "fast"
if SONG_TYPE == "slow":
    FPS = 120
    FFT_STEP = 2
    SMOOTHING_ALPHA = 0.2
elif SONG_TYPE == "fast":
    FPS = 120
    FFT_STEP = 2
    SMOOTHING_ALPHA = 0.4
