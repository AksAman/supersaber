from adafruit_led_animation.color import (  # noqa: F401
    RED,
    YELLOW,
    GREEN,
    CYAN,
    BLUE,
    PURPLE,
    BLACK,
    JADE,
    AQUA,
    GOLD,
    PINK,
    AMBER,
    calculate_intensity,
)


_COLORS = [
    JADE,
    RED,
    YELLOW,
    GREEN,
    CYAN,
    BLUE,
    PURPLE,
    AQUA,
    GOLD,
    PINK,
    AMBER,
]
COLORS = _COLORS


# MUTED_COLORS = [calculate_intensity(color, 0.2) for color in _COLORS]
fac = 0.1
MUTED_COLORS = [(r * fac, g * fac, b * fac) for r, g, b in _COLORS]
