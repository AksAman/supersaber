import time

import config
import digitalio
import neopixel
from adafruit_led_animation.color import calculate_intensity, colorwheel
from decoders import MQTTAudioDecoder

LED_PIN = config.LED_PIN


if LED_PIN:
    led = digitalio.DigitalInOut(config.LED_PIN)  # type: ignore
    led.direction = digitalio.Direction.OUTPUT
else:
    led = None


def light_on():
    if not led:
        return
    led.value = True


def light_off():
    if not led:
        return
    led.value = False


def blink():
    if not led:
        return
    light_on()
    time.sleep(config.LED_BLINK_DELAY)
    light_off()
    time.sleep(config.LED_BLINK_DELAY)


def main():
    blink()
    # while True:
    #     blink()


TONE = config.TONE


def on_value_callback(value):
    if value > 0.75:
        light_on()
    else:
        light_off()

    total_pixels = config.TOTAL_PIXELS
    if value <= 0:
        pixels.fill((0, 0, 0))
        pixels.show()
        return

    pixels_to_light = min(int(total_pixels // value) if value > 1 else int(total_pixels * value), total_pixels)
    pixels.fill((0, 0, 0))

    for i in range(pixels_to_light):
        index = i * 256 if TONE == "cold" else 256 - i * 256
        color = colorwheel(index // total_pixels)
        factor = (i / total_pixels) + 0.01
        color = calculate_intensity(color, factor)
        pixels[i] = color

    pixels.show()

    # light_value = int(128 // value) if value > 0 else 0
    # pixels.fill((light_value, 0, light_value))
    # pixels.show()


pixels = neopixel.NeoPixel(
    config.PIXEL_PIN,  # type: ignore
    config.TOTAL_PIXELS,
    brightness=config.BRIGHTNESS,
    auto_write=False,
)


def with_decoder():
    print(config)
    pixels.fill((0, 0, 0))
    pixels.show()
    mqtt_decoder = MQTTAudioDecoder(
        host=config.MQTT_HOST,
        port=config.MQTT_BROKER_PORT,
        topic=config.MQTT_TOPIC,
        on_value_callback=on_value_callback,
        use_smoothing=False,
    )
    while True:
        mqtt_decoder.loop()


with_decoder()
