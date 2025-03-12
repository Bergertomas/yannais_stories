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
        self.build_ui()  # Build UI during initialization

    def on_enter(self):
        """Called when the screen is entered."""
        # Only start the UI update timer, don't rebuild UI
        if not self.update_event:
            self.update_event = Clock.schedule_interval(self.update_ui, 0.1)

    def build_ui(self):
        """Build the UI for the playback screen."""
        self.clear_widgets()

        # Use a responsive view as the root layout
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
            size_hint_y=0.25
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
        main_layout.add_widget(BoxLayout(size_hint_y=0.15))

        # Playback controls section
        controls_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=0.6
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
        # Bind to value instead of touch events for more reliable behavior
        self.position_slider.bind(value=self.on_slider_value)
        controls_layout.add_widget(self.position_slider)

        # Playback buttons
        buttons_layout = BoxLayout(
            size_hint_y=None,
            height=dp(70),
            spacing=dp(20),
            padding=[dp(20), 0]
        )

        # Rewind button
        rewind_btn = Button(
            text="⏮",  # Unicode rewind symbol
            font_size=dp(24),
            background_color=theme.PRIMARY_COLOR,
            on_release=self.rewind
        )
        buttons_layout.add_widget(rewind_btn)

        # Play/Pause button
        self.play_pause_btn = Button(
            text="⏸",  # Unicode pause symbol
            font_size=dp(30),
            background_color=theme.ACCENT_COLOR,
            on_release=self.toggle_play_pause
        )
        buttons_layout.add_widget(self.play_pause_btn)

        # Forward button
        forward_btn = Button(
            text="⏭",  # Unicode fast forward symbol
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
            text="🔊",  # Unicode volume symbol
            size_hint_x=0.3
        )
        volume_layout.add_widget(volume_label)

        volume_slider = Slider(
            min=0,
            max=1,
            value=1,
            size_hint_x=0.7
        )
        volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(volume_slider)

        controls_layout.add_widget(volume_layout)

        main_layout.add_widget(controls_layout)

        self.add_widget(main_layout)

        # If we have a current recording, update display with it
        if self.current_recording:
            self.update_playback_info(self.current_recording)

    def update_playback_info(self, recording):
        """Update the UI with recording information."""
        if not recording:
            return

        self.current_recording = recording
        recording_id, title, description, filepath, duration, date_created, cover_art = recording

        # Update title
        self.title_label.text = title if title else "Untitled Recording"

        # Update description
        self.description_label.text = description if description else "No description"

        # Update date
        try:
            if date_created:
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
        if app.player and app.player.duration:
            self.position_slider.max = app.player.duration
        elif duration:
            self.position_slider.max = duration
        else:
            self.position_slider.max = 100  # Default

        # Update play/pause button
        self.update_play_pause_button()

    def update_ui(self, dt):
        """Update the UI based on playback state (called by Clock)."""
        app = App.get_running_app()

        # Update the position slider if not being dragged
        if not self.is_slider_being_dragged and app.player and app.player.sound:
            try:
                # Block the event temporarily to avoid recursion
                self.position_slider.unbind(value=self.on_slider_value)
                self.position_slider.value = app.player.current_pos
                self.position_slider.bind(value=self.on_slider_value)
            except Exception as e:
                print(f"Error updating slider position: {e}")

        # Update the time label
        if app.player and app.player.sound:
            try:
                current_pos = app.player.current_pos
                duration = app.player.duration

                # Format as MM:SS / MM:SS
                current_min = int(current_pos) // 60
                current_sec = int(current_pos) % 60
                total_min = int(duration) // 60
                total_sec = int(duration) % 60

                time_text = f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}"
                self.time_label.text = time_text
            except Exception as e:
                print(f"Error updating time label: {e}")
                self.time_label.text = "00:00 / 00:00"

        # Update play/pause button
        self.update_play_pause_button()

    def update_play_pause_button(self):
        """Update the play/pause button text based on playback state."""
        app = App.get_running_app()
        try:
            if app.player and app.player.is_playing:
                self.play_pause_btn.text = "⏸"  # Unicode pause symbol
            else:
                self.play_pause_btn.text = "▶️"  # Unicode play symbol
        except Exception as e:
            print(f"Error updating play/pause button: {e}")

    def toggle_play_pause(self, instance):
        """Toggle between play and pause states."""
        app = App.get_running_app()
        try:
            if app.player.is_playing:
                print("Pausing playback")
                app.player.pause()
            else:
                print("Starting playback")
                app.player.play()
            self.update_play_pause_button()
        except Exception as e:
            print(f"Error toggling play/pause: {e}")

    def rewind(self, instance):
        """Rewind the playback by 10 seconds."""
        app = App.get_running_app()
        try:
            if app.player and app.player.sound:
                new_pos = max(0, app.player.current_pos - 10)
                print(f"Rewinding to: {new_pos}")
                app.player.seek(new_pos)
        except Exception as e:
            print(f"Error rewinding: {e}")

    def forward(self, instance):
        """Forward the playback by 10 seconds."""
        app = App.get_running_app()
        try:
            if app.player and app.player.sound:
                new_pos = min(app.player.duration, app.player.current_pos + 10)
                print(f"Forwarding to: {new_pos}")
                app.player.seek(new_pos)
        except Exception as e:
            print(f"Error forwarding: {e}")

    def on_slider_value(self, instance, value):
        """Handle slider value change - seek to the new position."""
        if self.is_slider_being_dragged:
            app = App.get_running_app()
            try:
                if app.player and app.player.sound:
                    print(f"Seeking to position: {value}")
                    app.player.seek(value)
            except Exception as e:
                print(f"Error seeking to position: {e}")

    def on_slider_touch_down(self, instance, touch):
        """Handle slider touch down event."""
        if instance.collide_point(*touch.pos):
            self.is_slider_being_dragged = True
            return True
        return False

    def on_slider_touch_up(self, instance, touch):
        """Handle slider touch up event."""
        if instance.collide_point(*touch.pos) and self.is_slider_being_dragged:
            app = App.get_running_app()
            try:
                if app.player and app.player.sound:
                    print(f"Seeking to position after drag: {instance.value}")
                    app.player.seek(instance.value)
            except Exception as e:
                print(f"Error seeking to position: {e}")
            self.is_slider_being_dragged = False
            return True
        return False

    def on_volume_change(self, instance, value):
        """Change the playback volume."""
        app = App.get_running_app()
        try:
            if app.player:
                app.player.set_volume(value)
        except Exception as e:
            print(f"Error changing volume: {e}")

    def go_back(self, instance):
        """Navigate back and optionally stop playback."""
        app = App.get_running_app()
        # Don't stop playback, just navigate back
        app.root.current = 'file_list'

    def on_leave(self):
        """Called when the screen is exited."""
        # Stop the UI update timer
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None
