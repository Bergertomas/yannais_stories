from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.app import App
import random


class BackgroundScreen(FloatLayout):
    """A fullscreen background with stars and gradient."""

    def __init__(self, **kwargs):
        super(BackgroundScreen, self).__init__(**kwargs)

        # Set up the gradient background
        with self.canvas.before:
            # Dark blue background - deep night sky
            Color(0.08, 0.1, 0.2, 1)  # Very dark blue
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

        # Bind to size/pos changes
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Create and add static stars
        self._add_stars()

        # Schedule twinkling effect
        Clock.schedule_interval(self._twinkle_stars, 1 / 3)  # Update 3 times per second for gentle twinkling

    def _update_rect(self, *args):
        """Update the background rectangle."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _add_stars(self):
        """Add static star images to the background."""
        # Clear existing canvas instructions
        self.canvas.clear()

        # Create 3 layers of stars with different sizes and opacities
        # for a parallax-like depth effect

        # Background tiny stars (many, dim)
        for _ in range(100):
            x = random.random() * self.width
            y = random.random() * self.height
            size = random.uniform(1, 2)  # Tiny stars
            opacity = random.uniform(0.1, 0.4)  # Dim

            with self.canvas:
                Color(1, 1, 1, opacity)
                Ellipse(pos=(x, y), size=(size, size))

        # Mid-layer stars (medium number, medium brightness)
        for _ in range(50):
            x = random.random() * self.width
            y = random.random() * self.height
            size = random.uniform(1.5, 3)  # Medium stars
            opacity = random.uniform(0.3, 0.6)  # Medium brightness

            with self.canvas:
                Color(1, 1, 1, opacity)
                Ellipse(pos=(x, y), size=(size, size))

        # Foreground stars (few, bright)
        for _ in range(20):
            x = random.random() * self.width
            y = random.random() * self.height
            size = random.uniform(2, 4)  # Larger stars
            opacity = random.uniform(0.5, 0.9)  # Brighter

            with self.canvas:
                Color(1, 1, 1, opacity)
                Ellipse(pos=(x, y), size=(size, size))

        # Add a few special brighter stars that will twinkle
        self.twinkling_stars = []
        for _ in range(15):
            x = random.random() * self.width
            y = random.random() * self.height
            size = random.uniform(2.5, 4.5)
            base_opacity = random.uniform(0.6, 0.9)
            twinkle_speed = random.uniform(0.3, 1.0)  # Different speeds

            self.twinkling_stars.append({
                'x': x,
                'y': y,
                'size': size,
                'base_opacity': base_opacity,
                'opacity': base_opacity,
                'speed': twinkle_speed,
                'phase': random.random() * 6.28  # Random starting phase
            })

            with self.canvas:
                Color(1, 1, 1, base_opacity)
                Ellipse(pos=(x, y), size=(size, size))

    def _twinkle_stars(self, dt):
        """Animate only the twinkling stars."""
        # Only redraw the twinkling stars, not all stars
        for i, star in enumerate(self.twinkling_stars):
            # Calculate new opacity based on gentle sine wave
            time = Clock.get_boottime() * star['speed'] + star['phase']
            new_opacity = star['base_opacity'] * (0.7 + 0.3 * (
                        0.5 + 0.5 * (0.5 + 0.5 * (0.5 + 0.5 * (0.5 + 0.5 * (0.5 + 0.5 * (0.5 + 0.5 * (0.5 + 0.5))))))))

            # Update the star's properties
            star['opacity'] = new_opacity
            self.twinkling_stars[i] = star

        # Now redraw just the twinkling stars
        # First get their canvas indices to avoid redrawing everything
        with self.canvas:
            # Clear previous twinkling stars
            # This is inefficient but works for our purpose
            for star in self.twinkling_stars:
                Color(1, 1, 1, star['opacity'])
                Ellipse(pos=(star['x'], star['y']), size=(star['size'], star['size']))

    def on_size(self, *args):
        """Regenerate stars when window is resized."""
        # Only regenerate if we have a valid size
        if self.width > 0 and self.height > 0:
            self._add_stars()
