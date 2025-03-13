from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.app import App
import random
import math

# Keep all existing color names that might be used in KV files
# Original colors (from your existing theme)
PRIMARY_COLOR = get_color_from_hex('#5B6EAD')  # Keep original
ACCENT_COLOR = get_color_from_hex('#E6C27A')  # Keep original
BACKGROUND_COLOR = get_color_from_hex('#1A1F35')  # Keep original
SURFACE_COLOR = get_color_from_hex('#2D345A')  # Keep original
TEXT_COLOR = get_color_from_hex('#FFFFFF')  # Keep original
SECONDARY_TEXT_COLOR = get_color_from_hex('#E1E1E1')  # Keep original
SUCCESS_COLOR = get_color_from_hex('#6BAF92')  # Keep original
WARNING_COLOR = get_color_from_hex('#D4B86A')  # Keep original
ERROR_COLOR = get_color_from_hex('#C98B8B')  # Keep original
DIVIDER_COLOR = get_color_from_hex('#22315A')  # Keep original

# Star colors (from existing theme)
STAR_WHITE = (1, 1, 1, 1)  # Keep original
STAR_GOLD = get_color_from_hex('#E6C27A')  # Keep original
STAR_BLUE = get_color_from_hex('#7AB8FF')  # Keep original

# Navigation colors (from existing theme)
NAV_BLUE = get_color_from_hex('#5B6EAD')  # Keep original
NAV_GREEN = get_color_from_hex('#6BAF92')  # Keep original
NAV_GOLD = get_color_from_hex('#D4B86A')  # Keep original
NAV_PURPLE = get_color_from_hex('#9B8EC3')  # Keep original

# Font sizes (used in KV files)
FONT_SIZE_SMALL = '14sp'  # Keep original
FONT_SIZE_REGULAR = '16sp'  # Keep original
FONT_SIZE_LARGE = '20sp'  # Keep original
FONT_SIZE_XLARGE = '24sp'  # Keep original
FONT_SIZE_XXLARGE = '30sp'  # Keep original

# Button heights (used in KV files)
BUTTON_HEIGHT_SMALL = dp(40)  # Keep original
BUTTON_HEIGHT_REGULAR = dp(48)  # Keep original
BUTTON_HEIGHT_LARGE = dp(56)  # Keep original

# Add the reference to GOLD_LIGHT that's used in KV files
GOLD_LIGHT = ACCENT_COLOR  # Add this for KV compatibility

# Add your new custom color scheme
PRUSSIAN_BLUE = get_color_from_hex('#002D4E')
PRUSSIAN_BLUE_2 = get_color_from_hex('#003156')
PRUSSIAN_BLUE_3 = get_color_from_hex('#00365F')
CHARCOAL = get_color_from_hex('#234C5E')
FLAX = get_color_from_hex('#E0C87A')
DUTCH_WHITE = get_color_from_hex('#ECE0BA')
EGGSHELL = get_color_from_hex('#F2ECDA')
ALABASTER = get_color_from_hex('#F5F2EA')
PERIWINKLE = get_color_from_hex('#CBC9E7')
ULTRA_VIOLET = get_color_from_hex('#4C428F')

# Add card color for new theme elements
CARD_COLOR = PRUSSIAN_BLUE_3


class StarField(Widget):
    """Widget that displays animated stars in the background"""

    def __init__(self, **kwargs):
        super(StarField, self).__init__(**kwargs)
        self.stars = []
        self.size_hint = (1, 1)  # Take full screen size
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Generate stars
        self.generate_stars(80)

        # Update at a gentle pace for calming effect
        Clock.schedule_interval(self.update_stars, 1 / 15)

    def generate_stars(self, count):
        """Generate random stars"""
        self.stars = []

        # Get actual widget size or use window size as fallback
        width = self.width if self.width > 0 else Window.width
        height = self.height if self.height > 0 else Window.height

        for _ in range(count):
            # Random position
            x = random.random() * width
            y = random.random() * height

            # Random size (varied sizes for depth effect)
            size = random.random() * 2 + 1  # Slightly larger stars

            # Random brightness
            alpha = random.random() * 0.6 + 0.4

            # Random twinkle speed
            twinkle_speed = random.random() * 0.02 + 0.005

            # Random twinkle offset
            twinkle_offset = random.random() * 6.28  # 0 to 2π

            # Randomly choose between white and gold stars
            color = STAR_GOLD if random.random() > 0.7 else STAR_WHITE

            self.stars.append({
                'x': x,
                'y': y,
                'size': size,
                'color': color,
                'alpha': alpha,
                'base_alpha': alpha,
                'twinkle_speed': twinkle_speed,
                'twinkle_offset': twinkle_offset
            })

    def update_stars(self, dt):
        """Update star animation with gentle twinkling"""
        self.canvas.clear()
        with self.canvas:
            # First draw a full-screen background rectangle
            Color(*BACKGROUND_COLOR)
            Rectangle(pos=(0, 0), size=(Window.width, Window.height))

            # Then draw each star
            for star in self.stars:
                # Calculate gentle twinkle effect
                time_factor = Clock.get_boottime() * star['twinkle_speed']
                # Use simple sin function if math is not imported
                twinkle = 0.5 * (1 + math.sin(time_factor + star['twinkle_offset']))
                alpha = star['base_alpha'] * (0.7 + 0.3 * twinkle)

                # Unpack color - handle both tuples and lists
                if isinstance(star['color'], (list, tuple)):
                    if len(star['color']) == 4:
                        r, g, b, _ = star['color']
                    else:
                        r, g, b = star['color']

                    Color(r, g, b, alpha)
                else:
                    # Fallback to white if color is not properly formatted
                    Color(1, 1, 1, alpha)

                Ellipse(
                    pos=(star['x'] - star['size'] / 2, star['y'] - star['size'] / 2),
                    size=(star['size'], star['size'])
                )

    def on_size(self, *args):
        """Handle resize - redistribute stars when window size changes"""
        if self.width > 0 and self.height > 0:
            self.generate_stars(80)


def apply_theme(app):
    """Apply theme to the app."""
    # Set window background color
    Window.clearcolor = BACKGROUND_COLOR

    # Configure KivyMD theme if available
    if hasattr(app, 'theme_cls'):
        # Apply the custom color scheme to KivyMD
        app.theme_cls.primary_palette = "BlueGray"  # Closest to PRUSSIAN_BLUE
        app.theme_cls.accent_palette = "Amber"  # Closest to FLAX
        app.theme_cls.primary_hue = "700"  # Dark shade
        app.theme_cls.accent_hue = "500"  # Medium shade
        app.theme_cls.theme_style = "Dark"  # Dark theme

        print(f"Applied KivyMD theme with custom color scheme")

    # Add starfield to the root layout if it exists
    if hasattr(app, 'root_layout'):
        try:
            # Remove any existing starfields to prevent duplication
            for child in list(app.root_layout.children):
                if isinstance(child, StarField):
                    app.root_layout.remove_widget(child)

            # Create and add a new starfield at the bottom layer
            starfield = StarField()
            app.root_layout.add_widget(starfield, index=len(app.root_layout.children))
            print("Added starfield to root layout")
        except Exception as e:
            print(f"Error adding starfield: {e}")


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
