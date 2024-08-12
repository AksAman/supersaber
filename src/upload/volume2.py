# SPDX-FileCopyrightText: 2020 Gamblor21
#
# SPDX-License-Identifier: MIT
"""
`adafruit_led_animation.animation.volume`
================================================================================
Volume animation for CircuitPython helper library for LED animations.
* Author(s): Mark Komus
Implementation Notes
--------------------
**Hardware:**
* `Adafruit NeoPixels <https://www.adafruit.com/category/168>`_
* `Adafruit DotStars <https://www.adafruit.com/category/885>`_
**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

from adafruit_led_animation.animation import Animation
from adafruit_led_animation.color import colorwheel
from decoders import CustomDecoder


def reverse_colorwheel(value: int) -> tuple[int, int, int]:
    r = (value & 0xFF0000) >> 16
    g = (value & 0x00FF00) >> 8
    b = value & 0x0000FF
    return r, g, b


def map_range(x, in_min, in_max, out_min, out_max):
    """
    Maps a number from one range to another.
    :return: Returns value mapped to new range
    :rtype: float
    """
    mapped = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if out_min <= out_max:
        return max(min(mapped, out_max), out_min)

    return min(max(mapped, out_max), out_min)


class Volume(Animation):
    """
    Animate the brightness and number of pixels based on volume.
    :param pixel_object: The initialised LED object.
    :param float speed: Animation update speed in seconds, e.g. ``0.1``.
    :param brightest_color: Color at max volume ``(r, g, b)`` tuple, or ``0x000000`` hex format
    :param decoder: a CustomDecoder object that the volume will be taken from
    :param float max_volume: what volume is considered maximum where everything is lit up
    """

    on_cycle_complete_supported = True

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        pixel_object,
        speed,
        brightest_color,
        decoder: CustomDecoder,
        max_volume=50,
        notify_cycles=100,
        name=None,
        color_period=5,
        precompute_rainbow=True,
    ):
        self._decoder = decoder
        self._num_pixels = len(pixel_object)
        self._max_volume = max_volume
        self._brightest_color = brightest_color
        self.on_cycle_complete_supported = True
        super().__init__(
            pixel_object=pixel_object,
            speed=speed,
            color=brightest_color,
            name=name,
        )
        self.notify_cycles = notify_cycles
        self._period = color_period
        self.wheel_index = 0
        if precompute_rainbow:
            self.generate_rainbow()

    def generate_rainbow(self):
        """Generates the rainbow."""
        self.colors = []
        i = 0
        while i < 256:
            self.colors.append(reverse_colorwheel(colorwheel(int(i))))
            i += 1

    def set_brightest_color(self, brightest_color):
        """
        Animate the brightness and number of pixels based on volume.
        :param brightest_color: Color at max volume ``(r, g, b)`` tuple, or ``0x000000`` hex format
        """
        self._brightest_color = brightest_color

    @property
    def color(self):
        return self._brightest_color

    @color.setter
    def color(self, value):
        self._brightest_color = value

    def draw(self):
        red = int(
            map_range(
                self._decoder.rms_level,
                0,
                self._max_volume,
                0,
                self._brightest_color[0],
            )
        )
        green = int(
            map_range(
                self._decoder.rms_level,
                0,
                self._max_volume,
                0,
                self._brightest_color[1],
            )
        )
        blue = int(
            map_range(
                self._decoder.rms_level,
                0,
                self._max_volume,
                0,
                self._brightest_color[2],
            )
        )

        lit_pixels = int(
            map_range(self._decoder.rms_level, 0, self._max_volume, 0, self._num_pixels)
        )
        if lit_pixels > self._num_pixels:
            lit_pixels = self._num_pixels

        self.pixel_object[0:lit_pixels] = [(red, green, blue)] * lit_pixels
        self.pixel_object[lit_pixels : self._num_pixels] = [(0, 0, 0)] * (
            self._num_pixels - lit_pixels
        )
        self.cycle_complete = True

    def animate(self, show=True):
        super().animate(show)
        self._decoder.animate()

    def on_cycle_complete(self):
        self.cycle_count += 1
        if self.cycle_count % self.notify_cycles == 0:
            # for callback in self._also_notify:
            self.wheel_index += 1
            next_color = self.colors[self.wheel_index % len(self.colors)]
            #     callback(self)
            self.color = next_color
            # print(f"next color: {next_color}")
