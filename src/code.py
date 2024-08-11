from adafruit_debouncer import Button
import time
import board
import neopixel
import digitalio
from adafruit_led_animation.animation.comet import Comet

# from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle

# from adafruit_led_animation.color import (
#     RED,
#     YELLOW,
#     GREEN,
#     CYAN,
#     BLUE,
#     PURPLE,
#     BLACK,
#     JADE,
#     AQUA,
#     GOLD,
#     PINK,
#     AMBER,
# )
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
BLACK = (0, 0, 0)
COLORS = [RED, YELLOW, GREEN, CYAN, BLUE, PURPLE]


# COLORS = [RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, BLACK, JADE, AQUA, GOLD, PINK, AMBER]
PIXEL_PIN = board.D1
BUTTON_PIN = board.D5
SHORT_PRESS_DURATION = 500
LONG_PRESS_DURATION = 2000
BRIGHTNESS = 0.3
TOTAL_PIXELS = 144


button_pin = digitalio.DigitalInOut(BUTTON_PIN)
button_pin.direction = digitalio.Direction.INPUT
button_pin.pull = digitalio.Pull.UP
switch = Button(
    pin=button_pin,
    short_duration_ms=SHORT_PRESS_DURATION,
    long_duration_ms=LONG_PRESS_DURATION,
    value_when_pressed=False,
)

POWER = False
pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    TOTAL_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=False,
)


def update_colors_brightness(factor: float):
    global COLORS
    COLORS = [(int(r * factor), int(g * factor), int(b * factor)) for r, g, b in COLORS]


CURRENT_COLOR_INDEX = 0
current_color = COLORS[CURRENT_COLOR_INDEX]
comet = Comet(
    pixels,
    speed=0.02,
    color=current_color,
    tail_length=4,
    bounce=True,
    background_color=COLORS[(CURRENT_COLOR_INDEX + 1) % len(COLORS)],
)

# rainbow_sparkle = RainbowSparkle(
#     pixels,
#     speed=0.1,
#     color=current_color,
#     num_sparkles=10,
# )
ANIMATIONS = [
    comet,
    # rainbow_sparkle,
]
ANIMATION_INDEX = 0


def animate():
    # current_animation = ANIMATIONS[ANIMATION_INDEX]
    comet.animate()


def next_animation():
    global ANIMATION_INDEX
    ANIMATION_INDEX = (ANIMATION_INDEX + 1) % len(ANIMATIONS)
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
    comet.color = color
    print("Filling Pixels!", color)


def change_color(*args, **kwargs):
    global CURRENT_COLOR_INDEX
    CURRENT_COLOR_INDEX = (CURRENT_COLOR_INDEX + 1) % len(COLORS)
    # fill_pixels(0, TOTAL_PIXELS - 1, COLORS[CURRENT_COLOR_INDEX])
    # comet._background_color = COLORS[(CURRENT_COLOR_INDEX + 1) % len(COLORS)]
    comet._set_color(COLORS[CURRENT_COLOR_INDEX])


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
    comet.add_cycle_complete_receiver(change_color)
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
        # animate()
        comet.animate()
        # if step % 12 == 0:
        #     change_color()


main()
