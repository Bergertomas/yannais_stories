from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from datetime import datetime
import os
import theme


class PlaybackScreen(Screen):
    """Screen for audio playback with controls."""

    def __init__(self, **kwargs):
        super(PlaybackScreen, self).__init__(**kwargs)
        self.current_recording = None
        self.position_slider = None
        self.time_label = None
        self.title_label = None
        self.play_pause_btn = None
        self.update_event = None
        self.is_slider_being_dragged = False
        self.description_label = None
        self.date_label = None
        # Build UI during initialization
        self.build_ui()

    def on_enter(self):
        """Called when the screen is entered."""
        # Start the UI update timer
        if not self.update_event:
            self.update_event = Clock.schedule_interval(self.update_ui, 0.1)

        # Update the UI based on current playback state
        self.update_play_pause_button()

    def build_ui(self):
        """Build the UI for the playback screen."""
        self.clear_widgets()

        # Use a fixed layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint=(1, 1)
        )

        # Header with back button and title
        header = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        back_btn = Button(
            text="Back",
            size_hint_x=None,
            width=dp(80),
            background_color=theme.PRIMARY_COLOR,
            on_release=self.go_back
        )
        header.add_widget(back_btn)

        self.title_label = Label(
            text="Now Playing",
            font_size=dp(20),
            halign='center'
        )
        header.add_widget(self.title_label)

        main_layout.add_widget(header)

        # Recording info section
        info_layout = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            size_hint_y=None,
            height=dp(120)
        )

        # Description label
        self.description_label = Label(
            text="",
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle'
        )
        info_layout.add_widget(self.description_label)

        # Date created
        self.date_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14)
        )
        info_layout.add_widget(self.date_label)

        main_layout.add_widget(info_layout)

        # Spacer
        main_layout.add_widget(BoxLayout(size_hint_y=0.2))

        # Playback controls section
        controls_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
            height=dp(200)
        )

        # Time and position slider
        time_layout = BoxLayout(
            size_hint_y=None,
            height=dp(30)
        )

        self.time_label = Label(
            text="00:00 / 00:00",
            size_hint_x=1.0
        )
        time_layout.add_widget(self.time_label)

        controls_layout.add_widget(time_layout)

        # Position slider
        self.position_slider = Slider(
            min=0,
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(30),
            cursor_size=(dp(20), dp(20))
        )
        self.position_slider.bind(on_touch_down=self.on_slider_touch_down)
        self.position_slider.bind(on_touch_up=self.on_slider_touch_up)
        controls_layout.add_widget(self.position_slider)

        # Playback buttons
        buttons_layout = BoxLayout(
            size_hint_y=None,
            height=dp(70),
            spacing=dp(20),
            padding=[dp(20), 0]
        )

        # Rewind button - use simple text instead of unicode
        rewind_btn = Button(
            text="<<",  # Simple text rewind symbol
            font_size=dp(24),
            background_color=theme.PRIMARY_COLOR,
            on_release=self.rewind
        )
        buttons_layout.add_widget(rewind_btn)

        # Play/Pause button - use simple text instead of unicode
        self.play_pause_btn = Button(
            text="Play",  # Simple text
            font_size=dp(24),
            background_color=theme.ACCENT_COLOR,
            on_release=self.toggle_play_pause
        )
        buttons_layout.add_widget(self.play_pause_btn)

        # Forward button - use simple text instead of unicode
        forward_btn = Button(
            text=">>",  # Simple text forward symbol
            font_size=dp(24),
            background_color=theme.PRIMARY_COLOR,
            on_release=self.forward
        )
        buttons_layout.add_widget(forward_btn)

        controls_layout.add_widget(buttons_layout)

        # Volume slider
        volume_layout = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        volume_label = Label(
            text="Volume",  # Simple text instead of unicode
            size_hint_x=0.2
        )
        volume_layout.add_widget(volume_label)

        volume_slider = Slider(
            min=0,
            max=1,
            value=1,
            size_hint_x=0.8
        )
        volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(volume_slider)

        controls_layout.add_widget(volume_layout)

        main_layout.add_widget(controls_layout)

        # Add a spacer at the bottom to push content up
        main_layout.add_widget(BoxLayout(size_hint_y=0.1))

        self.add_widget(main_layout)

    def update_playback_info(self, recording):
        """Update the UI with recording information."""
        if not recording:
            print("No recording provided")
            return

        print(f"Updating playback info with recording: {recording}")
        self.current_recording = recording

        try:
            recording_id, title, description, filepath, duration, date_created, cover_art = recording

            # Update title
            if title and isinstance(title, str):
                self.title_label.text = title
            else:
                self.title_label.text = "Untitled Recording"

            # Update description
            if description and isinstance(description, str):
                self.description_label.text = description
            else:
                self.description_label.text = "No description"

            # Update date
            try:
                if date_created and isinstance(date_created, str):
                    dt = datetime.fromisoformat(date_created)
                    formatted_date = dt.strftime("%b %d, %Y %H:%M")
                else:
                    formatted_date = "Unknown date"
            except Exception as e:
                print(f"Error formatting date: {e}")
                formatted_date = "Invalid date"

            self.date_label.text = formatted_date

            # Update slider max value
            app = App.get_running_app()
            if app.player and app.player.duration > 0:
                self.position_slider.max = app.player.duration
                print(f"Setting slider max to {app.player.duration}")
            elif duration and duration > 0:
                self.position_slider.max = duration
                print(f"Setting slider max to {duration}")
            else:
                self.position_slider.max = 100  # Default
                print("Using default slider max of 100")

            # Update play/pause button
            self.update_play_pause_button()

        except Exception as e:
            print(f"Error updating playback info: {e}")

    def update_ui(self, dt):
        """Update the UI based on playback state."""
        app = App.get_running_app()

        if not app.player or not app.player.sound:
            return

        # Update the position slider if not being dragged
        try:
            if not self.is_slider_being_dragged:
                # Unbind temporarily to avoid recursive updates
                self.position_slider.value = app.player.current_pos

            # Update the time label
            current_pos = app.player.current_pos
            duration = app.player.duration

            # Format as MM:SS / MM:SS
            current_min = int(current_pos) // 60
            current_sec = int(current_pos) % 60
            total_min = int(duration) // 60
            total_sec = int(duration) % 60

            time_text = f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}"
            self.time_label.text = time_text

            # Update play/pause button
            self.update_play_pause_button()

        except Exception as e:
            print(f"Error updating UI: {e}")

    def update_play_pause_button(self):
        """Update the play/pause button text based on playback state."""
        app = App.get_running_app()
        try:
            if app.player and app.player.is_playing:
                self.play_pause_btn.text = "Pause"  # Simple text
            else:
                self.play_pause_btn.text = "Play"  # Simple text
        except Exception as e:
            print(f"Error updating play/pause button: {e}")

    def toggle_play_pause(self, instance):
        """Toggle between play and pause states."""
        app = App.get_running_app()

        if not app.player or not app.player.sound:
            print("No sound loaded to toggle playback")
            return

        try:
            if app.player.is_playing:
                print("Pausing playback via button press")
                app.player.pause()
            else:
                print("Starting/resuming playback via button press")
                app.player.play()

            # Update button immediately
            self.update_play_pause_button()

        except Exception as e:
            print(f"Error toggling play/pause: {e}")

    def rewind(self, instance):
        """Rewind the playback by 10 seconds."""
        app = App.get_running_app()

        if not app.player or not app.player.sound:
            return

        try:
            new_pos = max(0, app.player.current_pos - 10)
            print(f"Rewinding to position: {new_pos}")
            app.player.seek(new_pos)
        except Exception as e:
            print(f"Error rewinding: {e}")

    def forward(self, instance):
        """Forward the playback by 10 seconds."""
        app = App.get_running_app()

        if not app.player or not app.player.sound:
            return

        try:
            new_pos = min(app.player.duration, app.player.current_pos + 10)
            print(f"Fast forwarding to position: {new_pos}")
            app.player.seek(new_pos)
        except Exception as e:
            print(f"Error fast forwarding: {e}")

    def on_slider_touch_down(self, instance, touch):
        """Handle slider touch down event."""
        if instance.collide_point(*touch.pos):
            print("Slider touch down - starting drag")
            self.is_slider_being_dragged = True
            return True
        return False

    def on_slider_touch_up(self, instance, touch):
        """Handle slider touch up event - seek to the new position."""
        if instance.collide_point(*touch.pos) and self.is_slider_being_dragged:
            app = App.get_running_app()

            position = instance.value
            print(f"Seek to position: {position}")
            app.player.seek(position)

            self.is_slider_being_dragged = False
            return True
        return False

    def on_volume_change(self, instance, value):
        """Change the playback volume."""
        app = App.get_running_app()

        if not app.player:
            return

        try:
            app.player.set_volume(value)
        except Exception as e:
            print(f"Error changing volume: {e}")

    def go_back(self, instance):
        """Navigate back and optionally stop playback."""
        app = App.get_running_app()
        app.root_layout.current = 'file_list'

    def on_leave(self):
        """Called when the screen is exited."""
        # Stop the UI update timer
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None
