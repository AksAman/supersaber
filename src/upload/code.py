# import asyncio
import time

import config
import digitalio
import neopixel
from adafruit_debouncer import Button
from anim import create_blink_animation, init_animations
from colors import BLACK, COLORS, MUTED_COLORS, RED
from decoders import HttpAudioDecoder

POWER = False
CURRENT_COLOR_INDEX = 0
ANIMATION_INDEX = 0

button_pin = digitalio.DigitalInOut(config.BUTTON_PIN)  # type: ignore
button_pin.direction = digitalio.Direction.INPUT
button_pin.pull = digitalio.Pull.UP
switch = Button(
    pin=button_pin,
    short_duration_ms=config.SHORT_PRESS_DURATION,
    long_duration_ms=config.LONG_PRESS_DURATION,
    value_when_pressed=False,
)

pixels = neopixel.NeoPixel(
    config.PIXEL_PIN,  # type: ignore
    config.TOTAL_PIXELS,
    brightness=config.BRIGHTNESS,
    auto_write=False,
)

blink = create_blink_animation(pixels=pixels, color=RED, speed=0.02, period=2)


def on_decoder_error(decoder: HttpAudioDecoder):
    n = 6
    while n > 0:
        blink.animate()
        n -= 1
        time.sleep(0.2)
    global ANIMATION_INDEX
    ANIMATION_INDEX = (ANIMATION_INDEX + 1) % len(animations)
    print("Next Animation!", ANIMATION_INDEX)
    current_animation = get_current_animation()
    current_animation.resume()
    decoder.reset()


decoder = HttpAudioDecoder(
    endpoint=f"{config.AUDIO_SERVER_ENDPOINT}/audio-values",
    rms_level=0,
    alpha=config.AUDIO_VIS_SMOOTHING,
    on_error_callback=on_decoder_error,
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
    if hasattr(current_animation, "has_muted_colors") and current_animation.has_muted_colors:  # type: ignore
        current_color = current_color_muted
        bg_color = bg_color_muted

    if hasattr(current_animation, "_background_color"):
        current_animation._background_color = bg_color  # type: ignore
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
    for index in range(config.TOTAL_PIXELS):
        pixels[index] = current_color  # Set each LED to the current color
        pixels.show()  # Update the LED strip
        time.sleep(0.008)  # Short delay for the power-on effect
    POWER = True
    print("Powering On!")


def power_off():
    global POWER
    if not POWER:
        return
    for index in range(config.TOTAL_PIXELS - 1, -1, -1):
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


def main():
    power_on()
    # asyncio.run(update_decoder_rms(decoder))
    step = 0
    while True:
        step += 1
        handle_switch_listeners()
        on_loop(step)


main()


# async def update_decoder_rms_loop(decoder):
#     while True:
#         await update_decoder_rms(decoder)
#         await asyncio.sleep(0.02)  # Adjust the sleep time as needed


# async def main_loop():
#     step = 0
#     while True:
#         step += 1
#         handle_switch_listeners()
#         on_loop(step)
#         await asyncio.sleep(0)  # Yield control to the event loop


# async def main():
#     power_on()
#     task1 = asyncio.create_task(update_decoder_rms_loop(decoder))
#     task2 = asyncio.create_task(main_loop())
#     await asyncio.gather(task1, task2)


# # Start the main function
# asyncio.run(main())
