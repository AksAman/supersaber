import os

import board

USING_BUTTON = os.getenv("USING_BUTTON") == 1
# USING_BUTTON = True
if USING_BUTTON:
    BUTTON_PIN = board.D1
    PIXEL_PIN = board.D0
    TOTAL_PIXELS = 87
    # TOTAL_PIXELS = 56
    LED_PIN = None
else:
    BUTTON_PIN = None
    PIXEL_PIN = board.D5
    TOTAL_PIXELS = 56
    LED_PIN = board.LED
SHORT_PRESS_DURATION = 500
LONG_PRESS_DURATION = 2000
BRIGHTNESS = 0.2
AUDIO_VIS_SMOOTHING = 0.3

AUDIO_SERVER_IP = "192.168.0.100"
AUDIO_SERVER_PORT = 8002

AUDIO_SERVER_ENDPOINT = f"{AUDIO_SERVER_IP}:{AUDIO_SERVER_PORT}"
AUDIO_SERVER_ENDPOINT_HTTP = f"http://{AUDIO_SERVER_ENDPOINT}"
AUDIO_SERVER_ENDPOINT_WS = f"ws://{AUDIO_SERVER_ENDPOINT}"
REQUEST_TIMEOUT = 10

MQTT_HOST = AUDIO_SERVER_IP
MQTT_TOPICS = ["audio-values", "saber/tone"]
MQTT_BROKER_PORT = 1885

UDP_HOST = AUDIO_SERVER_IP
UDP_PORT = 1234


LED_BLINK_DELAY = 0.1

# PIXEL_PIN = board.D0
# TOTAL_PIXELS = 87


def save_tone(tone):
    with open("tone.txt", "w") as f:
        f.write(tone)


def read_tone():
    with open("tone.txt", "r") as f:
        return f.read().split(":")


def parse_tone_and_speed(payload):
    tone, *rest = payload.split(":")
    if rest:
        try:
            speed = int(rest[0])
        except Exception as e:
            print(e)
            speed = DEFAULT_SPEED
    else:
        speed = DEFAULT_SPEED

    return tone, speed


DEFAULT_TONE = "warm"
DEFAULT_SPEED = 50
try:
    TONE, SPEED = parse_tone_and_speed(read_tone())
except Exception as e:
    print(e)
    TONE = os.getenv("TONE", DEFAULT_TONE)
    SPEED = os.getenv("SPEED", DEFAULT_SPEED)
