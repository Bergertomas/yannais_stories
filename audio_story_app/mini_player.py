from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
import theme


class MiniPlayer(BoxLayout):
    """Floating playback controls that appear when audio is playing."""

    title = StringProperty("Not Playing")
    is_playing = BooleanProperty(False)
    progress = NumericProperty(0)
    max_progress = NumericProperty(100)

    def __init__(self, **kwargs):
        super(MiniPlayer, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)
        self.opacity = 1  # Start visible for testing

        # Add background
        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*theme.SURFACE_COLOR)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(0.2, 0.2, 0.2, 1)
            self.border = Rectangle(pos=self.pos, size=(self.width, dp(1)))

        # Bind size/pos changes to update rectangles
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Title label
        self.title_label = Label(
            text=self.title,
            size_hint_x=0.5,
            halign='left',
            shorten=True,
            shorten_from='right'
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        self.add_widget(self.title_label)

        # Progress bar
        self.progress_bar = ProgressBar(
            max=self.max_progress,
            value=self.progress,
            size_hint_x=0.2
        )
        self.add_widget(self.progress_bar)

        # Play/pause button
        self.play_pause_btn = Button(
            text="▶️" if not self.is_playing else "⏸",
            size_hint_x=0.15,
            font_size=dp(20),
            background_color=theme.ACCENT_COLOR,
            on_release=self.toggle_play_pause
        )
        self.add_widget(self.play_pause_btn)

        # Go to playback screen button
        self.goto_btn = Button(
            text="Open",
            size_hint_x=0.15,
            background_color=theme.PRIMARY_COLOR,
            on_release=self.goto_playback
        )
        self.add_widget(self.goto_btn)

        # Schedule updates
        self.update_event = Clock.schedule_interval(self.update_state, 0.5)

    def update_rect(self, *args):
        """Update background rectangle on size/pos changes."""
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size
        if hasattr(self, 'border'):
            self.border.pos = self.pos
            self.border.size = (self.width, dp(1))

    def update_state(self, dt):
        """Update player state based on app's audio player."""
        app = App.get_running_app()
        if not hasattr(app, 'player') or not app.player:
            return

        try:
            # Update visibility based on whether anything is loaded
            if app.player.sound:
                self.opacity = 1
            else:
                self.opacity = 0
                return

            # Update title
            if app.player.current_file:
                filename = os.path.basename(app.player.current_file)
                self.title = filename

            # Update is_playing state
            self.is_playing = app.player.is_playing

            # Update play/pause button
            self.play_pause_btn.text = "⏸" if self.is_playing else "▶️"

            # Update progress
            if app.player.duration > 0:
                self.max_progress = app.player.duration
                self.progress = app.player.current_pos
                self.progress_bar.max = app.player.duration
                self.progress_bar.value = app.player.current_pos
        except Exception as e:
            print(f"Error updating mini player: {e}")

    def toggle_play_pause(self, instance):
        """Toggle playback state."""
        app = App.get_running_app()
        if not app.player:
            return

        try:
            if app.player.is_playing:
                app.player.pause()
            else:
                app.player.play()
        except Exception as e:
            print(f"Error toggling play/pause: {e}")

    def goto_playback(self, instance):
        """Navigate to the full playback screen."""
        app = App.get_running_app()
        if app.root:
            app.root.current = 'playback'

    def on_touch_down(self, touch):
        """Handle touch events."""
        # Only process if visible
        if self.opacity < 0.5:
            return False

        if self.collide_point(*touch.pos):
            return super(MiniPlayer, self).on_touch_down(touch)
        return False


import os
