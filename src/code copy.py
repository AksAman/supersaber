# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials NeoPixel example"""
import time
import board
from rainbowio import colorwheel
import neopixel

PIXEL_PIN = board.D1
TOTAL_PIXELS = 144

pixels = neopixel.NeoPixel(PIXEL_PIN, TOTAL_PIXELS, brightness=0.1, auto_write=False)
segments = []
N_ARRAYS = 3

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

COLORS = [RED, YELLOW, GREEN, CYAN, BLUE, PURPLE]


num_pixels_per_segment = TOTAL_PIXELS // N_ARRAYS

for i in range(N_ARRAYS):
    start = i * num_pixels_per_segment
    end = start + num_pixels_per_segment
    color = COLORS[i % len(COLORS)]
    segments.append((start, end, color))

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)


def breathing_effect(
    current_seg,
    next_segment,
    previous_segment,
    min_brightness,
    max_brightness,
    speed,
):
    start, end, color = current_seg
    prev_start, prev_end, prev_color = previous_segment
    next_start, next_end, next_color = next_segment
    for brightness in range(min_brightness, max_brightness):
        for i in range(start, end):
            pixels[i] = [int(c * (brightness / 255.0)) for c in color]
        pixels.show()
        # time.sleep(speed)

    # Gradually decrease brightness
    for brightness in range(max_brightness, min_brightness, -1):
        for i in range(start, end):
            index_in_prev_segment = i - start
            if index_in_prev_segment >= 0:
                pixels[index_in_prev_segment] = [
                    int(c * (brightness / 255.0)) for c in prev_color
                ]

            pixels[i] = [int(c * (brightness / 255.0)) for c in color]

            index_in_next_segment = i + end
            if index_in_next_segment < TOTAL_PIXELS:
                pixels[index_in_next_segment] = [
                    int(c * (brightness / 255.0)) for c in next_color
                ]
        pixels.show()
        # time.sleep(speed)


def color_chase(segment_id: int, color: tuple[int, int, int], wait: int):
    if segment_id >= N_ARRAYS:
        return
    start, end = segments[segment_id]
    for i in range(start, end):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(0.1)


def fill_pixels(start: int, end: int, color: tuple[int, int, int]):
    for i in range(start, end):
        pixels[i] = color
    pixels.show()


def color_chase_og(color, wait, n_pixels, brightness=1):
    color = [int(c * brightness) for c in color]
    for i in range(n_pixels):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    # time.sleep(0.5)


def rainbow_cycle(
    segment_id: int,
    wait: float,
):
    if segment_id >= N_ARRAYS:
        return
    start, end = segments[segment_id]
    for j in range(255):
        for i in range(start, end):
            rc_index = (i * 256 // num_pixels_per_segment) + j
            pixels[i] = colorwheel(rc_index & 255)
        pixels.show()
        time.sleep(wait)


def main():
    color_index = 0
    while True:
        color = COLORS[(color_index + 2) % len(COLORS)]
        color_index += 1
        # color_chase_og(color, 0.0, TOTAL_PIXELS, 0.2)
        for segment_id in range(N_ARRAYS):
            fill_pixels(0, TOTAL_PIXELS, color)
            current_segment = segments[segment_id]
            start, end, color = current_segment
            next_segment = segments[(segment_id + 1) % N_ARRAYS]
            next_start, next_end, next_color = next_segment
            previous_segment = segments[(segment_id - 1) % N_ARRAYS]
            previous_start, previous_end, previous_color = previous_segment

            breathing_effect(
                current_seg=current_segment,
                next_segment=next_segment,
                previous_segment=previous_segment,
                min_brightness=0,
                max_brightness=255,
                speed=0.005,
            )

            fill_pixels(start, end, color)

    return
    while True:
        for segment_id in range(N_ARRAYS):
            # pixels.fill(RED)
            # pixels.show()
            # # Increase or decrease to change the speed of the solid color change.
            # time.sleep(1)
            # pixels.fill(GREEN)
            # pixels.show()
            # time.sleep(1)
            # pixels.fill(BLUE)
            # pixels.show()
            # time.sleep(1)

            color_chase(
                segment_id, RED, 0.1
            )  # Increase the number to slow down the color chase
            # color_chase(segment_id, YELLOW, 0.1)
            # color_chase(segment_id, GREEN, 0.1)
            # color_chase(segment_id, CYAN, 0.1)
            # color_chase(segment_id, BLUE, 0.1)
            # color_chase(segment_id, PURPLE, 0.1)

            # rainbow_cycle(
            #     segment_id, 0.1
            # )  # Increase the number to slow down the rainbow


# main()
fill_pixels(0, TOTAL_PIXELS, RED)
# print("hello")
