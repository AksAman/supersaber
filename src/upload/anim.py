from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation import Animation


def init_animations(
    pixels,
    fg_color,
    bg_color,
    callbacks,
) -> list[Animation]:
    print("init_animations")
    n_pixels = len(pixels)
    pulse = Pulse(pixels, speed=0.1, color=fg_color, period=4)
    comet = Comet(
        pixels,
        speed=0.02,
        color=fg_color,
        tail_length=12,
        bounce=True,
        background_color=bg_color,
    )

    sparkle = Sparkle(
        pixels,
        speed=0.1,
        color=bg_color,
        num_sparkles=n_pixels // 2,
    )
    animations: list[Animation] = [
        comet,
        sparkle,
        pulse,
    ]

    for animation in animations:
        if not animation.on_cycle_complete_supported:
            continue
        for callback in callbacks:
            animation.add_cycle_complete_receiver(callback)

    return animations
