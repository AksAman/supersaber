from adafruit_led_animation.color import (
    AMBER,
    AQUA,
    BLACK,
    BLUE,
    CYAN,
    GOLD,
    GREEN,
    JADE,
    PINK,
    PURPLE,
    RED,
    YELLOW,
    calculate_intensity,
)

BLACK = BLACK
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


MUTED_COLORS = [calculate_intensity(color, 0.2) for color in _COLORS]
fac = 0.2
MUTED_COLORS = [(r * fac, g * fac, b * fac) for r, g, b in _COLORS]
