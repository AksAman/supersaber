import time

import config
import digitalio
import neopixel
import wifi
from adafruit_debouncer import Button
from adafruit_led_animation.color import (
    calculate_intensity,
    colorwheel,
)
from decoders import (
    MQTTAudioDecoder,
    UDPAudioDecoder,
)
from fake_button import FakeButton

LED_PIN = config.LED_PIN
TONE = config.TONE
SPEED = config.SPEED
PAUSED = False
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


TONE_TO_COLOR = {
    "warm": lambda i: 256 * (1 - i),
    "cold": lambda i: 256 * i,
    "cool": lambda i: 256 * (i / 2),  # Cool tone
    "hot": lambda i: 256 * (1 - i / 2),  # Hot tone
    "red": lambda i: 0,
    "green": lambda i: 85 * config.TOTAL_PIXELS,
    "blue": lambda i: 170 * config.TOTAL_PIXELS,
    "yellow": lambda i: 42 * config.TOTAL_PIXELS,
    "purple": lambda i: 128 * config.TOTAL_PIXELS,
    "cyan": lambda i: 213 * config.TOTAL_PIXELS,
    "magenta": lambda i: 213 * config.TOTAL_PIXELS,
    "orange": lambda i: 21 * config.TOTAL_PIXELS,
    "change": lambda i: int(256 * ((time.monotonic() * SPEED) % 255)),
    "chase": lambda i: (int((i - time.monotonic() * SPEED) + (i) * (256 // config.TOTAL_PIXELS)) % 255)
    * config.TOTAL_PIXELS,
    "moving": lambda i: colorwheel(i + (time.monotonic() * SPEED // 2)),
}

DEFAULT_TONER = lambda i: 256 * i
TONE_KEYS_LIST = list(TONE_TO_COLOR.keys())


def toner(tone: str, pixel_index: int, total_pixels: int):
    wheel_index = TONE_TO_COLOR.get(tone, DEFAULT_TONER)(pixel_index)
    color = colorwheel(wheel_index // total_pixels)
    factor = (pixel_index / total_pixels) + 0.2
    color = calculate_intensity(color, factor)
    return color


def on_message_callback(topic, message):
    if topic == "saber/tone":
        global TONE, SPEED
        TONE, SPEED = config.parse_tone_and_speed(message)
        print("Tone changed to", TONE, "Speed:", SPEED)
        config.save_tone(message)


def fill_pixels(color):
    pixels.fill(color)
    pixels.show()


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
        pixels[i] = toner(TONE, i, total_pixels)

    pixels.show()

    # light_value = int(128 // value) if value > 0 else 0
    # pixels.fill((light_value, 0, light_value))
    # pixels.show()


BRIGHTNESS = config.BRIGHTNESS
BRIGHTNESS = 0.1
pixels = neopixel.NeoPixel(
    config.PIXEL_PIN,  # type: ignore
    config.TOTAL_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=False,
)

if config.USING_BUTTON:
    print("Using Real Button")
    button_pin = digitalio.DigitalInOut(config.BUTTON_PIN)  # type: ignore
    button_pin.direction = digitalio.Direction.INPUT
    button_pin.pull = digitalio.Pull.UP
    switch = Button(
        pin=button_pin,
        short_duration_ms=config.SHORT_PRESS_DURATION,
        long_duration_ms=config.LONG_PRESS_DURATION,
        value_when_pressed=False,
    )
else:
    print("Using FakeButton")
    switch = FakeButton()


def create_mqtt_decoder():
    return MQTTAudioDecoder(
        host=config.MQTT_HOST,
        port=config.MQTT_BROKER_PORT,
        topics=config.MQTT_TOPICS,
        on_value_callback=on_value_callback,
        on_message_callback=on_message_callback,
        use_smoothing=False,
    )


def create_udp_decoder():
    return UDPAudioDecoder(
        host=config.UDP_HOST,
        port=config.UDP_PORT,
        sleep_time=0.005,
        on_value_callback=on_value_callback,
    )


def reset_decoder(decoder: MQTTAudioDecoder):
    print("Double Pressed!")
    decoder.reset()


LAST_PRESS_TIME = time.monotonic()
PRESSED_COUNT = 0
DOUBLE_PRESS_THRESHOLD = 2


def handle_switch_listeners(decoder):
    global PRESSED_COUNT, LAST_PRESS_TIME, PAUSED
    switch.update()

    if switch.long_press:
        print("Long Press")
        # reset_decoder(decoder=decoder)
        PAUSED = not PAUSED

    # detect double press
    if PRESSED_COUNT == 2:
        print("Double Pressed!")
        PRESSED_COUNT = 0

    if switch.short_count == 1:
        global TONE
        if PAUSED:
            PAUSED = False
            return
        current_time = time.monotonic()
        time_diff = current_time - LAST_PRESS_TIME
        if time_diff <= DOUBLE_PRESS_THRESHOLD:
            PRESSED_COUNT += 1
        else:
            PRESSED_COUNT = 1
        LAST_PRESS_TIME = current_time

        print("******************************* >>>>>>> Pressed!", time_diff)
        TONE = TONE_KEYS_LIST[(TONE_KEYS_LIST.index(TONE) + 1) % len(TONE_KEYS_LIST)]
        print("Tone changed to", TONE)
        config.save_tone(f"{TONE}:{SPEED}")
        print("main loop", switch.short_count, switch.short_to_show, switch.short_counter)
        # on_single_press()


def with_decoder(decoder: MQTTAudioDecoder):
    pixels.fill((0, 0, 0))
    pixels.show()
    # last_time = time.monotonic()

    while True:
        time.sleep(0.01)
        # new_time = time.monotonic()
        # print(f"Passed: {new_time - last_time}")
        handle_switch_listeners(decoder)
        if PAUSED:
            continue
        decoder.loop()
        # print("main loop", switch.short_count, switch.short_to_show, switch.short_counter)
        # last_time = new_time


def main():
    if wifi.radio.connected:
        light_on()

    decoder_type = "mqtt"
    decoder = create_mqtt_decoder() if decoder_type == "mqtt" else create_udp_decoder()
    with_decoder(decoder=decoder)  # type: ignore


def test_switch():
    while True:
        switch.update()
        if switch.long_press:
            print("Long Press")
        if switch.short_count != 0:
            print("Short Press Count =", switch.short_count)
            print("main loop", switch.short_count, switch.short_to_show, switch.short_counter)
        if switch.long_press and switch.short_count == 1:
            print("That's a long double press !")


if __name__ == "__main__":
    main()
