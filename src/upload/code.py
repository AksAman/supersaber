from adafruit_debouncer import Button
import time
import board
import neopixel
import digitalio
import sys

print(sys.path)
import os

print(os.listdir("lib/adafruit_led_animation"))

from colors import COLORS, BLACK
from anim import init_animations


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
BRIGHTNESS = 0.35
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
current_color = COLORS[CURRENT_COLOR_INDEX]
bg_color = COLORS[(CURRENT_COLOR_INDEX + 1) % len(COLORS)]


def update_colors_brightness(factor: float):
    global COLORS
    COLORS = [(int(r * factor), int(g * factor), int(b * factor)) for r, g, b in COLORS]


def change_color(*args, **kwargs):
    global CURRENT_COLOR_INDEX
    CURRENT_COLOR_INDEX = (CURRENT_COLOR_INDEX + 1) % len(COLORS)
    # fill_pixels(0, TOTAL_PIXELS - 1, COLORS[CURRENT_COLOR_INDEX])
    # comet._background_color = COLORS[(CURRENT_COLOR_INDEX + 1) % len(COLORS)]
    current_animation = get_current_animation()
    current_animation.color = COLORS[CURRENT_COLOR_INDEX]
    # comet._set_color(COLORS[CURRENT_COLOR_INDEX])


animations = init_animations(
    pixels=pixels, fg_color=current_color, bg_color=bg_color, callbacks=[change_color]
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


def fill_pixels(start: int, end: int, color: tuple[int, int, int]):
    # for i in range(start, end):
    #     print(i)
    #     pixels[i] = color
    # pixels.show()
    global CURRENT_COLOR_INDEX

    color = COLORS[CURRENT_COLOR_INDEX]
    if not POWER:
        return
    current_animation = get_current_animation()
    current_animation.color = color
    print("Filling Pixels!", color)


def power_on():
    global POWER, CURRENT_COLOR_INDEX
    if POWER:
        return
    for index in range(TOTAL_PIXELS):
        pixels[index] = COLORS[CURRENT_COLOR_INDEX]  # Set each LED to the current color
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


def main():

    update_colors_brightness(0.2)
    power_on()
    step = 0
    while True:
        step += 1
        switch.update()  # Check the status of the button
        # rainbow.animate()

        if switch.long_press:
            # Handle long press
            print("Long Pressed!")
            toggle_power()

        if switch.short_count == 2:
            # Handle double press
            print("Double Pressed!")

        if switch.pressed:
            # Handle single press
            print("Pressed!")
            next_animation()
            # power_on()
            # change_color()
            # comet.reverse = not comet.reverse
        # if POWER:
        animate(step=step)

        # if step % 12 == 0:
        #     change_color()


main()
