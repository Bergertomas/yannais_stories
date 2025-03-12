from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

# Theme colors
PRIMARY_COLOR = get_color_from_hex('#4051B5')  # Indigo
ACCENT_COLOR = get_color_from_hex('#7289DA')  # Discord-like blue
BACKGROUND_COLOR = get_color_from_hex('#1E1F36')  # Dark blue-gray
SURFACE_COLOR = get_color_from_hex('#282A48')  # Slightly lighter dark blue
TEXT_COLOR = get_color_from_hex('#FFFFFF')  # White
SECONDARY_TEXT_COLOR = get_color_from_hex('#B3FFFFFF')  # White with 70% opacity

# Button colors
SUCCESS_COLOR = get_color_from_hex('#4CAF50')  # Green
WARNING_COLOR = get_color_from_hex('#FFC107')  # Amber
ERROR_COLOR = get_color_from_hex('#F44336')  # Red

# Font sizes
FONT_SIZE_SMALL = '14sp'
FONT_SIZE_REGULAR = '16sp'
FONT_SIZE_LARGE = '20sp'
FONT_SIZE_XLARGE = '24sp'
FONT_SIZE_XXLARGE = '30sp'

# Layout metrics
PADDING_SMALL = '5dp'
PADDING_REGULAR = '10dp'
PADDING_LARGE = '20dp'
SPACING_SMALL = '5dp'
SPACING_REGULAR = '10dp'
SPACING_LARGE = '20dp'

# Button height
BUTTON_HEIGHT_SMALL = '40dp'
BUTTON_HEIGHT_REGULAR = '48dp'
BUTTON_HEIGHT_LARGE = '56dp'


def apply_rounded_button_style(button, color=None):
    """Apply a rounded style to a button."""
    if color is None:
        color = PRIMARY_COLOR

    # Clear any existing canvas instructions
    button.canvas.before.clear()

    with button.canvas.before:
        Color(color[0], color[1], color[2], color[3] if len(color) > 3 else 1)
        button._rect = RoundedRectangle(pos=button.pos, size=button.size, radius=[dp(10)])

    # Bind updates to ensure the rectangle gets updated when the button size/pos changes
    button.bind(pos=update_rect, size=update_rect)


def update_rect(instance, value):
    """Update the rectangle's position and size when the button changes."""
    if hasattr(instance, '_rect'):
        instance._rect.pos = instance.pos
        instance._rect.size = instance.size


def apply_theme(app):
    """Apply theme to the app."""
    # Set window background color
    Window.clearcolor = BACKGROUND_COLOR

    # We'll let individual screens handle their button styling
    # by importing this module and using apply_rounded_button_style
    pass
