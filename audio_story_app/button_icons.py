from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Triangle, Ellipse, Rectangle, Line
from kivy.metrics import dp


class IconButton(Button):
    """Button with custom drawn icon instead of text."""

    def __init__(self, icon_type='play', **kwargs):
        # Set empty text - we'll draw the icon instead
        kwargs['text'] = ''
        super(IconButton, self).__init__(**kwargs)
        self.icon_type = icon_type
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        """Update the button's icon based on its type."""
        # Clear the canvas instructions
        self.canvas.after.clear()

        # Get centered position within button
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2

        # Get dimensions based on button size (75% of the smallest dimension)
        size = min(self.width, self.height) * 0.5

        # Draw the appropriate icon based on type
        with self.canvas.after:
            Color(1, 1, 1, 1)  # White icons for visibility

            if self.icon_type == 'play':
                # Draw play triangle
                Triangle(
                    points=[
                        cx - size / 2, cy - size / 2,  # Left bottom
                        cx - size / 2, cy + size / 2,  # Left top
                        cx + size / 2, cy  # Right middle
                    ]
                )

            elif self.icon_type == 'pause':
                # Draw two pause bars
                bar_width = size / 3
                bar_spacing = size / 4

                # Left bar
                Rectangle(
                    pos=(cx - bar_spacing - bar_width, cy - size / 2),
                    size=(bar_width, size)
                )

                # Right bar
                Rectangle(
                    pos=(cx + bar_spacing, cy - size / 2),
                    size=(bar_width, size)
                )

            elif self.icon_type == 'rewind':
                # Draw rewind triangles
                tri_size = size * 0.4
                spacing = tri_size / 4

                # Left triangle
                Triangle(
                    points=[
                        cx - spacing - tri_size, cy,  # Left middle
                        cx - spacing, cy + tri_size / 2,  # Right top
                        cx - spacing, cy - tri_size / 2  # Right bottom
                    ]
                )

                # Right triangle
                Triangle(
                    points=[
                        cx + spacing, cy,  # Right middle
                        cx + spacing + tri_size, cy + tri_size / 2,  # Left top
                        cx + spacing + tri_size, cy - tri_size / 2  # Left bottom
                    ]
                )

            elif self.icon_type == 'forward':
                # Draw forward triangles
                tri_size = size * 0.4
                spacing = tri_size / 4

                # Left triangle
                Triangle(
                    points=[
                        cx - spacing - tri_size, cy + tri_size / 2,  # Left top
                        cx - spacing - tri_size, cy - tri_size / 2,  # Left bottom
                        cx - spacing, cy  # Right middle
                    ]
                )

                # Right triangle
                Triangle(
                    points=[
                        cx + spacing, cy + tri_size / 2,  # Right top
                        cx + spacing, cy - tri_size / 2,  # Right bottom
                        cx + spacing + tri_size, cy  # Right middle
                    ]
                )

            elif self.icon_type == 'repeat':
                # Draw repeat circle with arrow
                # Circle outline
                Line(
                    circle=(cx, cy, size / 2),
                    width=dp(2)
                )

                # Arrow head at bottom
                arrow_size = size / 4
                Triangle(
                    points=[
                        cx, cy - size / 2 - arrow_size / 2,  # Bottom point
                            cx - arrow_size / 2, cy - size / 2 + arrow_size / 2,  # Left point
                            cx + arrow_size / 2, cy - size / 2 + arrow_size / 2  # Right point
                    ]
                )

            elif self.icon_type == 'continue':
                # Draw next track icon (triangle with bar)
                tri_size = size * 0.6
                bar_width = size / 5

                # Triangle
                Triangle(
                    points=[
                        cx - tri_size / 2, cy - tri_size / 2,  # Left bottom
                        cx - tri_size / 2, cy + tri_size / 2,  # Left top
                        cx + tri_size / 2 - bar_width, cy  # Right middle
                    ]
                )

                # Bar
                Rectangle(
                    pos=(cx + tri_size / 2 - bar_width, cy - tri_size / 2),
                    size=(bar_width, tri_size)
                )

            elif self.icon_type == 'home':
                # Draw home icon
                roof_size = size * 0.7
                house_size = size * 0.5

                # Roof (triangle)
                Triangle(
                    points=[
                        cx - roof_size / 2, cy - size * 0.1,  # Left
                        cx + roof_size / 2, cy - size * 0.1,  # Right
                        cx, cy + size / 2  # Top
                    ]
                )

                # House (rectangle)
                Rectangle(
                    pos=(cx - house_size / 2, cy - size / 2),
                    size=(house_size, house_size * 0.8)
                )

            elif self.icon_type == 'list':
                # Draw list icon (three horizontal lines)
                line_width = size * 0.7
                line_height = size * 0.1
                line_spacing = size * 0.2

                # Top line
                Rectangle(
                    pos=(cx - line_width / 2, cy + line_spacing),
                    size=(line_width, line_height)
                )

                # Middle line
                Rectangle(
                    pos=(cx - line_width / 2, cy - line_height / 2),
                    size=(line_width, line_height)
                )

                # Bottom line
                Rectangle(
                    pos=(cx - line_width / 2, cy - line_spacing - line_height),
                    size=(line_width, line_height)
                )

            elif self.icon_type == 'star':
                # Draw a simple star
                # For simplicity, draw a filled circle with points
                Ellipse(
                    pos=(cx - size / 6, cy - size / 6),
                    size=(size / 3, size / 3)
                )

                # Draw points coming out from the circle
                for i in range(8):
                    angle = i * 3.14159 / 4  # 45 degrees between points
                    x1 = cx + (size / 6) * 0.8 * 2 * dp(1) * dp(1)
                    y1 = cy + (size / 6) * 0.8 * 2 * dp(1) * dp(1)
                    x2 = cx + (size / 2) * dp(1) * dp(1)
                    y2 = cy + (size / 2) * dp(1) * dp(1)

                    # Draw a simple line
                    Line(
                        points=[x1, y1, x2, y2],
                        width=dp(1.5)
                    )

            # Add more icon types as needed

    def set_icon(self, icon_type):
        """Change the button's icon type."""
        self.icon_type = icon_type
        self.update_canvas()


class RoundedButton(Button):
    """Button with rounded corners and proper touch area."""

    def __init__(self, text='', background_color=None, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.text = text
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Transparent background
        self._bg_color = background_color or PRIMARY_COLOR

        # Draw the rounded background
        with self.canvas.before:
            Color(rgba=self._bg_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)] * 4
            )

        # Bind to update the rectangle when the button size/pos changes
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, instance, value):
        """Update background rectangle when button changes."""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

    def set_background_color(self, color):
        """Change the background color."""
        self._bg_color = color
        with self.canvas.before:
            Color(rgba=color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)] * 4
            )
