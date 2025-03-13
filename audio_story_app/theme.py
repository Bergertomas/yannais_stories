from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.app import App
import random

# Theme colors - calming nighttime colors for toddlers
PRIMARY_COLOR = get_color_from_hex('#5B6EAD')  # Soft blue-purple
ACCENT_COLOR = get_color_from_hex('#E6C27A')  # Soft gold/amber
BACKGROUND_COLOR = get_color_from_hex('#1A1F35')  # Deep blue night sky
SURFACE_COLOR = get_color_from_hex('#2D345A')  # Slightly lighter blue-purple
TEXT_COLOR = get_color_from_hex('#FFFFFF')  # White
SECONDARY_TEXT_COLOR = get_color_from_hex('#E1E1E1')  # Light gray

# Calming accent colors
GOLD_LIGHT = get_color_from_hex('#E6C27A')  # Soft gold
GOLD_DARK = get_color_from_hex('#C4A76A')  # Muted gold

# Button colors - soft and calming
SUCCESS_COLOR = get_color_from_hex('#6BAF92')  # Soft green
WARNING_COLOR = get_color_from_hex('#D4B86A')  # Soft amber
ERROR_COLOR = get_color_from_hex('#C98B8B')  # Soft red

# Navigation button colors
NAV_BLUE = get_color_from_hex('#5B6EAD')  # Soft blue
NAV_GREEN = get_color_from_hex('#6BAF92')  # Soft green
NAV_GOLD = get_color_from_hex('#D4B86A')  # Soft gold/amber
NAV_PURPLE = get_color_from_hex('#9B8EC3')  # Soft purple

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


class StarField(Widget):
    """Widget that displays animated stars in the background"""

    def __init__(self, **kwargs):
        super(StarField, self).__init__(**kwargs)
        self.stars = []
        self.generate_stars(50)  # Generate 50 stars (less intense for toddlers)
        Clock.schedule_interval(self.update_stars, 1 / 20)  # Update at 20 FPS (gentler)

    def generate_stars(self, count):
        """Generate random stars"""
        self.stars = []
        for _ in range(count):
            # Random position
            x = random.random() * Window.width
            y = random.random() * Window.height

            # Random size (1-2 pixels - smaller for gentler effect)
            size = random.random() * 1.5 + 0.5

            # Random brightness (0.2-0.7 - softer for toddlers)
            alpha = random.random() * 0.5 + 0.2

            # Random twinkle speed (0.005-0.03 - slower for calming effect)
            twinkle_speed = random.random() * 0.025 + 0.005

            # Random twinkle offset
            twinkle_offset = random.random() * 6.28  # 0 to 2π

            self.stars.append({
                'x': x,
                'y': y,
                'size': size,
                'alpha': alpha,
                'base_alpha': alpha,
                'twinkle_speed': twinkle_speed,
                'twinkle_offset': twinkle_offset
            })

    def update_stars(self, dt):
        """Update star animation with gentle twinkling"""
        self.canvas.clear()
        with self.canvas:
            for star in self.stars:
                # Calculate gentle twinkle effect
                time_factor = Clock.get_boottime() * star['twinkle_speed']
                alpha_mod = 0.5 * (1 + (0.5 * (1 + (0.5 * (1 +
                                                           (0.5 *
                                                            (1 + (0.5))))))))
                alpha = star['base_alpha'] * alpha_mod

                # Draw star
                Color(1, 1, 1, alpha)  # White with calculated alpha
                Ellipse(pos=(star['x'] - star['size'] / 2, star['y'] - star['size'] / 2),
                        size=(star['size'], star['size']))

    def on_size(self, *args):
        """Handle resize - redistribute stars when window size changes"""
        for star in self.stars:
            star['x'] = random.random() * self.width
            star['y'] = random.random() * self.height


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

    # Add starfield to the root layout
    if hasattr(app, 'root_layout'):
        try:
            # First remove any existing starfield
            for child in list(app.root_layout.children):
                if isinstance(child, StarField):
                    app.root_layout.remove_widget(child)

            # Create and add a new starfield as the bottom-most widget
            starfield = StarField()
            app.root_layout.add_widget(starfield, index=len(app.root_layout.children))
            print("Added starfield to root layout")
        except Exception as e:
            print(f"Error adding starfield: {e}")
