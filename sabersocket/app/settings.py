import pyaudio

sleep_between_frames = False
RMS_THRESHOLD = 5
# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
AUDIO_DEVICE = 7
FPS = 90
