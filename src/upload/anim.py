from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation import Animation
from adafruit_led_animation.animation.rainbow import Rainbow
from volume2 import Volume
from decoders import CustomDecoder


def init_animations(
    pixels,
    fg_color,
    bg_color,
    fg_color_muted,
    bg_color_muted,
    callbacks,
    decoder: CustomDecoder,
) -> list[Animation]:
    print("init_animations")
    n_pixels = len(pixels)
    comet = Comet(
        pixels,
        speed=0.018,
        color=fg_color,
        tail_length=12,
        bounce=True,
        background_color=bg_color,
    )
    comet2 = Comet(
        pixels,
        speed=0.005,
        color=fg_color,
        tail_length=12,
        bounce=False,
        background_color=bg_color,
    )

    sparkle = Sparkle(
        pixels,
        speed=0.05,
        color=fg_color_muted,
        num_sparkles=n_pixels // 2,
    )

    sparkle.has_muted_colors = True

    pulse = Pulse(pixels, speed=0.02, color=fg_color_muted, period=3)
    pulse.has_muted_colors = True

    rainbow = Rainbow(pixels, speed=0.01, period=5)

    volume = Volume(
        pixel_object=pixels,
        speed=0.01,
        brightest_color=fg_color,
        decoder=decoder,
        max_volume=100,
        notify_cycles=2,
    )

    animations: list[Animation] = [
        volume,
        comet,
        comet2,
        sparkle,
        pulse,
        rainbow,
    ]

    for animation in animations:
        if not animation.on_cycle_complete_supported:
            continue
        for callback in callbacks:
            animation.add_cycle_complete_receiver(callback)

    return animations
