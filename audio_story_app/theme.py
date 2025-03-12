from kivy.utils import get_color_from_hex

# Theme colors
PRIMARY_COLOR = get_color_from_hex('#2196F3')  # Blue
ACCENT_COLOR = get_color_from_hex('#FF4081')  # Pink
BACKGROUND_COLOR = get_color_from_hex('#121212')  # Dark
SURFACE_COLOR = get_color_from_hex('#1E1E1E')  # Slightly lighter dark
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

def apply_theme(app):
    """Apply theme to various widgets programmatically if needed."""
    pass