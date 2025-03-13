from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
import os
import theme

from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.card import MDCard


class MiniPlayer(MDCard):
    """Floating playback controls that appear when audio is playing."""

    title = StringProperty("Not Playing")
    is_playing = BooleanProperty(False)
    progress = NumericProperty(0)
    max_progress = NumericProperty(100)

    def __init__(self, **kwargs):
        super(MiniPlayer, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = [dp(8), dp(8)]
        self.spacing = dp(8)
        self.radius = [dp(12), dp(12), 0, 0]  # Rounded corners on the top only
        self.elevation = 6  # Add shadow for depth

        # Use theme colors (safe fallback to RGB tuple if md_bg_color causes issues)
        self.md_bg_color = theme.SURFACE_COLOR

        # Title label
        self.title_label = MDLabel(
            text=self.title,
            size_hint_x=0.5,
            halign='left',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            shorten=True,
            shorten_from='right'
        )
        self.add_widget(self.title_label)

        # Progress bar
        self.progress_bar = MDProgressBar(
            max=self.max_progress,
            value=self.progress,
            size_hint_x=0.2,
            color=theme.ACCENT_COLOR
        )
        self.add_widget(self.progress_bar)

        # Play/pause button
        self.play_pause_btn = MDIconButton(
            icon="play",
            size_hint_x=None,
            width=dp(48),
            icon_size=dp(24),  # Use icon_size instead of user_font_size
            theme_text_color="Custom",
            text_color=theme.ACCENT_COLOR,
            on_release=self.toggle_play_pause
        )
        self.add_widget(self.play_pause_btn)

        # Go to playback screen button
        self.goto_btn = MDIconButton(
            icon="arrow-expand-up",
            size_hint_x=None,
            width=dp(48),
            icon_size=dp(24),  # Use icon_size instead of user_font_size
            theme_text_color="Custom",
            text_color=theme.PRIMARY_COLOR,
            on_release=self.goto_playback
        )
        self.add_widget(self.goto_btn)

        # Schedule updates
        self.update_event = Clock.schedule_interval(self.update_state, 0.5)

    def update_state(self, dt):
        """Update player state based on app's audio player."""
        app = App.get_running_app()
        if not hasattr(app, 'player') or not app.player:
            return

        try:
            # Update visibility based on whether anything is loaded
            if app.player.sound:
                if self.opacity < 1:
                    print("Mini player: Sound is loaded, showing mini player")
                self.opacity = 1

                # Update title from file path
                if app.player.current_file:
                    filename = os.path.basename(app.player.current_file)
                    self.title = filename
                    # Set title_label text directly in case binding isn't working
                    self.title_label.text = filename

                # Update is_playing state
                self.is_playing = app.player.is_playing

                # Update play/pause button icon
                self.play_pause_btn.icon = "pause" if self.is_playing else "play"

                # Update progress
                if app.player.duration > 0:
                    self.max_progress = app.player.duration
                    self.progress = app.player.current_pos
                    self.progress_bar.max = app.player.duration
                    self.progress_bar.value = app.player.current_pos
            else:
                # Keep visible but show "Not Playing"
                self.title = "Not Playing"
                self.title_label.text = "Not Playing"
        except Exception as e:
            print(f"Error updating mini player: {e}")

    def toggle_play_pause(self, instance):
        """Toggle playback state."""
        app = App.get_running_app()
        if not app.player or not app.player.sound:
            return

        try:
            print(f"Mini player: Toggle play/pause, current state: {app.player.is_playing}")
            if app.player.is_playing:
                app.player.pause()
                self.play_pause_btn.icon = "play"
            else:
                app.player.play()
                self.play_pause_btn.icon = "pause"
        except Exception as e:
            print(f"Error toggling play/pause in mini player: {e}")

    def goto_playback(self, instance):
        """Navigate to the full playback screen."""
        app = App.get_running_app()
        if hasattr(app, 'root_layout'):
            print("Mini player: Navigating to playback screen")
            app.root_layout.current = 'playback'

    def on_touch_down(self, touch):
        """Handle touch events."""
        # Only process if visible
        if self.opacity < 0.5:
            return False

        if self.collide_point(*touch.pos):
            return super(MiniPlayer, self).on_touch_down(touch)
        return False
