import json
import ssl
import time

import board
import digitalio
import socketpool
import wifi
from websockets import Session

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

socket = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()

print(socket)
print(ssl_context)


def light_on():
    led.value = True


def light_off():
    led.value = False


def blink(n):
    for _ in range(n):
        light_on()
        time.sleep(0.5)
        light_off()
        time.sleep(0.5)


wsession = Session(socket, ssl=ssl_context, iface=None)

message = "Repeat this"


URL = "ws://192.168.0.100:8002/audio-values"


def main():
    blink(3)
    is_wifi_connected = wifi.radio.connected
    if is_wifi_connected:
        light_on()
    else:
        light_off()
        return
    with wsession.client(URL) as ws:
        while True:
            result = ws.recv()
            data = json.loads(result)
            print(f"RECEIVED: <{result}>")
            v = data.get("v", 0)
            print(f"\t parsed: v:{v}")
            time.sleep(0.05)


main()
