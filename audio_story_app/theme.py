from kivy.utils import get_color_from_hex

# Main colors
PRIMARY_COLOR = get_color_from_hex('#344DB4')  # Royal blue for headers and primary UI
SECONDARY_COLOR = get_color_from_hex('#1A2E51')  # Deep navy for main content area
ACCENT_COLOR = get_color_from_hex('#FFD073')  # Golden yellow like stars
BACKGROUND_COLOR = get_color_from_hex('#1A2E51')  # Deep navy - night sky background
BACKGROUND_DARKER = get_color_from_hex('#162440')  # Slightly darker for certain elements
SURFACE_COLOR = get_color_from_hex('#263C66')  # Slightly lighter navy for cards
CARD_COLOR = get_color_from_hex('#263C66')  # Card background

# Text colors
TEXT_COLOR = get_color_from_hex('#FFFFFF')  # White text
SECONDARY_TEXT_COLOR = get_color_from_hex('#CCD7FF')  # Light blue-white text
LIGHT_TEXT_COLOR = get_color_from_hex('#F0F8FF')  # Very light blue for emphasis

# UI element colors
BUTTON_COLOR = get_color_from_hex('#4169E1')  # Royal blue for buttons
NAV_BAR_COLOR = get_color_from_hex('#344DB4')  # Bottom navigation bar color
DIVIDER_COLOR = get_color_from_hex('#394E80')  # Light divider

# Star colors
STAR_GOLD = get_color_from_hex('#FFD073')  # Golden yellow - main star color
STAR_WHITE = get_color_from_hex('#FFFFFF')  # White - bright stars
STAR_BLUE = get_color_from_hex('#B3E0FF')  # Light blue - distant stars

# Additional color palette for variety
COLOR_PURPLE = get_color_from_hex('#B89AFF')  # Soft purple for variety
COLOR_GOLD = get_color_from_hex('#FFC247')  # Star gold
COLOR_MOON = get_color_from_hex('#F0F1B3')  # Moon yellow/white


# Additional colors for story cards
CARD_BLUE = get_color_from_hex('#4681C0')  # Blue for some story cards
CARD_PURPLE = get_color_from_hex('#7A4BC0')  # Purple for some story cards
CARD_GREEN = get_color_from_hex('#41A074')  # Green for some story cards
CARD_ORANGE = get_color_from_hex('#EE7B51')  # Orange for some story cards

# Font sizes
FONT_SIZE_TINY = '12sp'
FONT_SIZE_SMALL = '14sp'
FONT_SIZE_REGULAR = '16sp'
FONT_SIZE_LARGE = '20sp'
FONT_SIZE_XLARGE = '24sp'
FONT_SIZE_XXLARGE = '28sp'
FONT_SIZE_HEADER = '36sp'

# Radius and padding values
CORNER_RADIUS_SMALL = '8dp'
CORNER_RADIUS_MEDIUM = '15dp'
CORNER_RADIUS_LARGE = '20dp'
CORNER_RADIUS_XLARGE = '25dp'
CORNER_RADIUS_FULL = '50dp'  # For circular elements

PADDING_SMALL = '5dp'
PADDING_MEDIUM = '10dp'
PADDING_LARGE = '15dp'
PADDING_XLARGE = '20dp'


# Nav bar dimension
NAV_BAR_HEIGHT = '60dp'
HEADER_HEIGHT = '60dp'

# Button height
BUTTON_HEIGHT_SMALL = '40dp'
BUTTON_HEIGHT_REGULAR = '48dp'
BUTTON_HEIGHT_LARGE = '56dp'

# Rounded corners - more pronounced for kid-friendly appearance
CORNER_RADIUS_REGULAR = '15dp'

# Nav bar dimension
NAV_BAR_HEIGHT = '60dp'
HEADER_HEIGHT = '60dp'


def apply_theme(app):
    """Apply DreamTales theme to app window."""
    from kivy.core.window import Window

    # Set window background color
    Window.clearcolor = BACKGROUND_COLOR


# Helper functions for styling
def card_style():
    """Return style properties for a card container."""
    return {
        'background_color': CARD_COLOR,
        'border_radius': [CORNER_RADIUS_REGULAR, CORNER_RADIUS_REGULAR,
                          CORNER_RADIUS_REGULAR, CORNER_RADIUS_REGULAR]
    }


# def button_style(button_type='primary'):
#     """Return style properties for different button types."""
#     if button_type == 'primary':
#         return {
#             'background_color': PRIMARY_COLOR,
#             'color': TEXT_COLOR,
#             'border_radius': [CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL,
#                               CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL]
#         }
#     elif button_type == 'accent':
#         return {
#             'background_color': ACCENT_COLOR,
#             'color': BACKGROUND_COLOR,  # Dark text on light background
#             'border_radius': [CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL,
#                               CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL]
#         }
#     elif button_type == 'success':
#         return {
#             'background_color': SUCCESS_COLOR,
#             'color': BACKGROUND_COLOR,
#             'border_radius': [CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL,
#                               CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL]
#         }
#     elif button_type == 'warning':
#         return {
#             'background_color': WARNING_COLOR,
#             'color': BACKGROUND_COLOR,  # Dark text on light background
#             'border_radius': [CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL,
#                               CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL]
#         }
#     elif button_type == 'error':
#         return {
#             'background_color': ERROR_COLOR,
#             'color': BACKGROUND_COLOR,
#             'border_radius': [CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL,
#                               CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL]
#         }
#     elif button_type == 'outline':
#         return {
#             'background_color': (0, 0, 0, 0),  # Transparent
#             'color': COLOR_GOLD,
#             'border_color': COLOR_GOLD,
#             'border_width': '1dp',
#             'border_radius': [CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL,
#                               CORNER_RADIUS_SMALL, CORNER_RADIUS_SMALL]
#         }
