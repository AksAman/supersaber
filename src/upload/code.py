import asyncio
from adafruit_debouncer import Button
import time
import board
import neopixel
import digitalio


from colors import COLORS, BLACK, MUTED_COLORS
from anim import init_animations
from decoders import HttpAudioDecoder, update_decoder_rms


# RED = (255, 0, 0)
# YELLOW = (255, 150, 0)
# GREEN = (0, 255, 0)
# CYAN = (0, 255, 255)
# BLUE = (0, 0, 255)
# PURPLE = (180, 0, 255)
# BLACK = (0, 0, 0)
# COLORS = [RED, YELLOW, GREEN, CYAN, BLUE, PURPLE]


PIXEL_PIN = board.D0
BUTTON_PIN = board.D1
SHORT_PRESS_DURATION = 500
LONG_PRESS_DURATION = 2000
BRIGHTNESS = 0.2
TOTAL_PIXELS = 87
POWER = False
CURRENT_COLOR_INDEX = 0
ANIMATION_INDEX = 0

button_pin = digitalio.DigitalInOut(BUTTON_PIN)
button_pin.direction = digitalio.Direction.INPUT
button_pin.pull = digitalio.Pull.UP
switch = Button(
    pin=button_pin,
    short_duration_ms=SHORT_PRESS_DURATION,
    long_duration_ms=LONG_PRESS_DURATION,
    value_when_pressed=False,
)

pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    TOTAL_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=False,
)
decoder = HttpAudioDecoder(
    endpoint="http://192.168.0.106:8002/audio-values", rms_level=0
)


current_color = COLORS[CURRENT_COLOR_INDEX]
current_color_muted = MUTED_COLORS[CURRENT_COLOR_INDEX]
bg_color = MUTED_COLORS[(CURRENT_COLOR_INDEX + 1) % len(MUTED_COLORS)]
bg_color_muted = MUTED_COLORS[(CURRENT_COLOR_INDEX + 1) % len(MUTED_COLORS)]


def change_color(*args, **kwargs):
    global CURRENT_COLOR_INDEX
    CURRENT_COLOR_INDEX = (CURRENT_COLOR_INDEX + 1) % len(COLORS)
    current_animation = get_current_animation()
    current_color = COLORS[CURRENT_COLOR_INDEX]
    current_color_muted = MUTED_COLORS[CURRENT_COLOR_INDEX]
    bg_color = MUTED_COLORS[(CURRENT_COLOR_INDEX + 2) % len(MUTED_COLORS)]
    bg_color_muted = MUTED_COLORS[(CURRENT_COLOR_INDEX + 2) % len(MUTED_COLORS)]
    if (
        hasattr(current_animation, "has_muted_colors")
        and current_animation.has_muted_colors
    ):
        current_color = current_color_muted
        bg_color = bg_color_muted

    if hasattr(current_animation, "_background_color"):
        current_animation._background_color = bg_color
    current_animation.color = current_color


animations = init_animations(
    pixels=pixels,
    fg_color=current_color,
    bg_color=bg_color,
    fg_color_muted=current_color_muted,
    bg_color_muted=bg_color_muted,
    callbacks=[change_color],
    decoder=decoder,
)


def get_current_animation():
    return animations[ANIMATION_INDEX]


def animate(step: int):
    current_animation = get_current_animation()
    current_animation.animate()


def next_animation():
    global ANIMATION_INDEX
    ANIMATION_INDEX = (ANIMATION_INDEX + 1) % len(animations)
    print("Next Animation!", ANIMATION_INDEX)
    current_animation = get_current_animation()
    current_animation.resume()


def power_on():
    global POWER, CURRENT_COLOR_INDEX
    if POWER:
        return

    current_color = MUTED_COLORS[CURRENT_COLOR_INDEX % len(MUTED_COLORS)]
    for index in range(TOTAL_PIXELS):
        pixels[index] = current_color  # Set each LED to the current color
        pixels.show()  # Update the LED strip
        time.sleep(0.008)  # Short delay for the power-on effect
    POWER = True
    print("Powering On!")


def power_off():
    global POWER
    if not POWER:
        return
    for index in range(TOTAL_PIXELS - 1, -1, -1):
        pixels[index] = BLACK  # Set each LED to the current color
        pixels.show()  # Update the LED strip
        time.sleep(0.008)  # Short delay for the power-on effect
    POWER = False
    print("Powered Off!")


def toggle_power():
    global POWER
    if POWER:
        power_off()
    else:
        power_on()


def on_long_press():
    print("Long Pressed!")
    toggle_power()


def on_double_press():
    print("Double Pressed!")
    if not POWER:
        power_on()
    next_animation()


def on_single_press():
    if not POWER:
        power_on()
    current_animation = get_current_animation()
    if current_animation._paused:
        current_animation.resume()
    else:
        current_animation.freeze()


def on_loop(step):
    if POWER:
        animate(step=step)

    time.sleep(0.01)


def handle_switch_listeners():
    switch.update()
    if switch.long_press:
        on_long_press()

    if switch.short_count == 2:
        on_double_press()

    if switch.pressed:
        on_single_press()


# def main():
#     power_on()
#     asyncio.run(update_decoder_rms(decoder))
#     step = 0
#     while True:
#         step += 1
#         handle_switch_listeners()
#         on_loop(step)


# main()


async def update_decoder_rms_loop(decoder):
    while True:
        await update_decoder_rms(decoder)
        await asyncio.sleep(0.01)  # Adjust the sleep time as needed


async def main_loop():
    step = 0
    while True:
        step += 1
        handle_switch_listeners()
        on_loop(step)
        await asyncio.sleep(0)  # Yield control to the event loop


async def main():
    power_on()
    task1 = asyncio.create_task(update_decoder_rms_loop(decoder))
    task2 = asyncio.create_task(main_loop())
    await asyncio.gather(task1, task2)


# Start the main function
asyncio.run(main())
