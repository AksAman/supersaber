from adafruit_led_animation.color import (
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


COLORS = [
    JADE,
    RED,
    YELLOW,
    GREEN,
    CYAN,
    BLUE,
    PURPLE,
    BLACK,
    AQUA,
    GOLD,
    PINK,
    AMBER,
]
COLORS = [calculate_intensity(color, 0.1) for color in COLORS]
