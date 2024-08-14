from adafruit_led_animation.animation import Animation
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.sparkle import Sparkle
from decoders import CustomDecoder
from volume2 import Volume


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
        speed=0.001,
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
    setattr(sparkle, "has_muted_colors", True)  # type: ignore

    pulse = Pulse(pixels, speed=0.02, color=fg_color_muted, period=3)
    setattr(pulse, "has_muted_colors", True)  # type: ignore

    rainbow = Rainbow(pixels, speed=0.01, period=5)

    volume = Volume(
        pixel_object=pixels,
        speed=0.002,
        brightest_color=fg_color,
        decoder=decoder,
        max_volume=190,
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
