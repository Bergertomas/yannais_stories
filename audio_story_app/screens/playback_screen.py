from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.core.window import Window
from datetime import datetime
import math
import theme

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView


class PlaybackScreen(Screen):
    """Playback screen with modernized KivyMD UI."""

    position = NumericProperty(0)
    duration = NumericProperty(100)
    time_display = StringProperty("00:00 / 00:00")

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
        self.repeat_enabled = False
        self.repeat_btn = None
        self._handling_track_finish = False
        self.current_playlist_id = None
        self.source_screen = None  # Track which screen we came from

        # Bind to window resize to ensure proper layout
        Window.bind(on_resize=self.on_window_resize)

        # Build UI during initialization
        self.build_ui()

    def on_window_resize(self, instance, width, height):
        """Handle window resize to ensure layout adapts properly"""
        # Rebuild UI on significant size changes
        if hasattr(self, 'main_scroll'):
            # Ensure the scroll view adapts to the new size
            self.main_scroll.size = (width, height)

    def on_enter(self):
        """Called when the screen is entered."""
        # Start the UI update timer
        if not self.update_event:
            self.update_event = Clock.schedule_interval(self.update_ui, 0.1)

        # Update the UI based on current playback state
        self.update_play_pause_button()

        # Register for track finished event
        app = App.get_running_app()
        if app.player:
            app.player.bind(on_track_finished=self.on_track_finished)

    def build_ui(self):
        """Build the UI for the playback screen."""
        self.clear_widgets()

        # Use scrollview for better handling of different screen sizes
        self.main_scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        # Main layout
        main_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(18),  # Increased spacing between elements
            size_hint_y=None  # Needed for scroll to work
        )

        # Set initial height, will be adjusted below
        main_layout.height = dp(700)

        # Header with back button and title
        header = MDBoxLayout(
            size_hint_y=None,
            height=dp(56),
            spacing=dp(8),
            padding=[0, dp(8)]
        )

        back_btn = MDIconButton(
            icon="arrow-left",
            on_release=self.go_back,
            theme_text_color="Custom",
            text_color=theme.TEXT_COLOR,
            icon_size=dp(24)  # Use icon_size instead of user_font_size
        )
        header.add_widget(back_btn)

        self.title_label = MDLabel(
            text="Now Playing",
            font_style="H5",
            theme_text_color="Custom",
            text_color=theme.TEXT_COLOR,
            halign="center"
        )
        header.add_widget(self.title_label)

        # Add a spacer to balance the header
        spacer = Widget(size_hint_x=None, width=dp(48))
        header.add_widget(spacer)

        main_layout.add_widget(header)

        # Album art card (placeholder with visual elements)
        album_card = MDCard(
            size_hint=(1, None),
            height=dp(240),  # Increased height
            radius=dp(20),
            elevation=4,
            padding=dp(12)  # Increased padding
        )
        # Set background color safely
        album_card.md_bg_color = theme.CARD_COLOR

        # Add a visual icon for the album art
        album_layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12)  # Added spacing between elements
        )

        album_icon = MDIconButton(
            icon="music-note",
            icon_size=dp(96),  # Use icon_size instead of user_font_size
            theme_text_color="Custom",
            text_color=theme.FLAX,  # Use gold color for icon
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        album_layout.add_widget(album_icon)

        # Description label inside the card
        self.description_label = MDLabel(
            text="",
            theme_text_color="Custom",
            text_color=theme.TEXT_COLOR,
            halign="center",
            font_style="Body1",
            size_hint_y=None,
            height=dp(60)  # Fixed height to prevent overlap
        )
        album_layout.add_widget(self.description_label)

        # Date label inside the card
        self.date_label = MDLabel(
            text="",
            theme_text_color="Custom",
            text_color=theme.SECONDARY_TEXT_COLOR,
            halign="center",
            font_style="Caption",
            size_hint_y=None,
            height=dp(30)  # Fixed height to prevent overlap
        )
        album_layout.add_widget(self.date_label)

        album_card.add_widget(album_layout)
        main_layout.add_widget(album_card)

        # Playback controls card
        controls_card = MDCard(
            size_hint=(1, None),
            height=dp(280),  # Increased height
            radius=dp(20),
            elevation=4,
            padding=dp(20)  # Increased padding
        )
        # Set background color safely
        controls_card.md_bg_color = theme.SURFACE_COLOR

        controls_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20)  # Increased spacing
        )

        # Time and position slider
        time_layout = MDBoxLayout(
            size_hint_y=None,
            height=dp(30)
        )

        self.time_label = MDLabel(
            text="00:00 / 00:00",
            theme_text_color="Custom",
            text_color=theme.TEXT_COLOR,
            halign="center"
        )
        time_layout.add_widget(self.time_label)

        controls_layout.add_widget(time_layout)

        # Position slider
        self.position_slider = MDSlider(
            min=0,
            max=100,
            value=0,
            color=theme.FLAX,  # Use gold color from our theme
            hint=False,  # Don't show the popup hint
            size_hint_y=None,
            height=dp(40)  # Increased height for better touch
        )
        self.position_slider.bind(on_touch_down=self.on_slider_touch_down)
        self.position_slider.bind(on_touch_up=self.on_slider_touch_up)
        controls_layout.add_widget(self.position_slider)

        # Main playback buttons
        buttons_layout = MDBoxLayout(
            size_hint_y=None,
            height=dp(80),  # Increased height
            spacing=dp(20),
            padding=[dp(20), dp(10)]  # Added padding at top and bottom
        )

        # Add a spacer to center the buttons
        buttons_layout.add_widget(Widget(size_hint_x=0.1))

        # Rewind button
        rewind_btn = MDIconButton(
            icon="rewind-10",
            theme_text_color="Custom",
            text_color=theme.FLAX,
            icon_size=dp(36),  # Use icon_size instead of user_font_size
            on_release=self.rewind
        )
        buttons_layout.add_widget(rewind_btn)

        # Play/Pause button (larger)
        self.play_pause_btn = MDIconButton(
            icon="play",
            theme_text_color="Custom",
            text_color=theme.FLAX,
            icon_size=dp(48),  # Use icon_size instead of user_font_size
            on_release=self.toggle_play_pause
        )
        buttons_layout.add_widget(self.play_pause_btn)

        # Forward button
        forward_btn = MDIconButton(
            icon="fast-forward-10",
            theme_text_color="Custom",
            text_color=theme.FLAX,
            icon_size=dp(36),  # Use icon_size instead of user_font_size
            on_release=self.forward
        )
        buttons_layout.add_widget(forward_btn)

        # Add another spacer to center the buttons
        buttons_layout.add_widget(Widget(size_hint_x=0.1))

        controls_layout.add_widget(buttons_layout)

        # Additional control buttons (repeat and playlist)
        extra_buttons = MDBoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(16),
            padding=[dp(16), 0]
        )

        # Repeat button
        self.repeat_btn = MDIconButton(
            icon="repeat",
            theme_text_color="Custom",
            text_color=theme.DUTCH_WHITE,
            icon_size=dp(24),  # Use icon_size instead of user_font_size
            on_release=self.toggle_repeat
        )
        extra_buttons.add_widget(self.repeat_btn)

        # Add to playlist button
        playlist_btn = MDIconButton(
            icon="playlist-plus",
            theme_text_color="Custom",
            text_color=theme.DUTCH_WHITE,
            icon_size=dp(24),  # Use icon_size instead of user_font_size
            on_release=self.add_to_playlist
        )
        extra_buttons.add_widget(playlist_btn)

        controls_layout.add_widget(extra_buttons)

        # Volume slider
        volume_layout = MDBoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(8)
        )

        volume_icon = MDIconButton(
            icon="volume-medium",
            theme_text_color="Custom",
            text_color=theme.TEXT_COLOR,
            icon_size=dp(24),  # Use icon_size instead of user_font_size
            size_hint_x=None,
            width=dp(40)
        )
        volume_layout.add_widget(volume_icon)

        volume_slider = MDSlider(
            min=0,
            max=1,
            value=1,
            color=theme.FLAX,
            hint=False
        )
        volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(volume_slider)

        controls_layout.add_widget(volume_layout)
        controls_card.add_widget(controls_layout)
        main_layout.add_widget(controls_card)

        # Add a spacer at the bottom to push content up
        main_layout.add_widget(Widget(size_hint_y=None, height=dp(30)))

        # Calculate total height based on children
        total_height = 0
        for child in main_layout.children:
            if hasattr(child, 'height'):
                total_height += child.height

        # Add padding for spacing
        total_height += dp(100)

        # Set minimum height to ensure scrolling works properly
        main_layout.height = max(total_height, dp(700))

        # Add main layout to scroll view
        self.main_scroll.add_widget(main_layout)

        # Add scroll view to screen
        self.add_widget(self.main_scroll)

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
        """Update UI based on playback state."""
        app = App.get_running_app()

        if not app.player or not app.player.sound:
            return

        try:
            # Update position slider if not being dragged
            if not self.is_slider_being_dragged:
                self.position_slider.value = app.player.current_pos

            # Update time label
            current_pos = app.player.current_pos
            duration = app.player.duration

            # Format time as MM:SS / MM:SS
            current_min = int(current_pos) // 60
            current_sec = int(current_pos) % 60
            total_min = int(duration) // 60
            total_sec = int(duration) % 60

            self.time_label.text = f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}"

            # Update play/pause button
            self.update_play_pause_button()

        except Exception as e:
            print(f"Error updating UI: {e}")

    def update_play_pause_button(self):
        """Update the play/pause button icon based on playback state."""
        app = App.get_running_app()
        try:
            if app.player and app.player.is_playing:
                self.play_pause_btn.icon = "pause"
            else:
                self.play_pause_btn.icon = "play"
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

    def toggle_repeat(self, instance):
        """Toggle repeat mode."""
        # Ensure the attribute exists
        if not hasattr(self, 'repeat_enabled'):
            self.repeat_enabled = False

        # Toggle the repeat mode
        self.repeat_enabled = not self.repeat_enabled

        # Update button appearance
        if self.repeat_enabled:
            self.repeat_btn.text_color = theme.FLAX  # Gold when active
            print("Repeat mode enabled")
        else:
            self.repeat_btn.text_color = theme.DUTCH_WHITE  # Normal when inactive
            print("Repeat mode disabled")

    def rewind(self, instance):
        """Rewind by 10 seconds."""
        app = App.get_running_app()

        if not app.player or not app.player.sound:
            return

        try:
            # Seek backward 10 seconds
            new_pos = max(0, app.player.current_pos - 10)
            print(f"Rewinding to position: {new_pos}")
            app.player.seek(new_pos)

        except Exception as e:
            print(f"Error rewinding: {e}")

    def forward(self, instance):
        """Forward by 10 seconds."""
        app = App.get_running_app()

        if not app.player or not app.player.sound:
            return

        try:
            # Seek forward 10 seconds
            new_pos = min(app.player.duration, app.player.current_pos + 10)
            print(f"Fast forwarding to position: {new_pos}")
            app.player.seek(new_pos)

        except Exception as e:
            print(f"Error fast forwarding: {e}")

    def on_slider_touch_down(self, instance, touch):
        """Handle slider touch down with proper seeking."""
        if instance.collide_point(*touch.pos):
            print("Slider touch down - starting drag")
            self.is_slider_being_dragged = True
            return True
        return False

    def on_slider_touch_up(self, instance, touch):
        """Handle slider touch up with final seek."""
        if self.is_slider_being_dragged and instance.collide_point(*touch.pos):
            # Final seek on release
            app = App.get_running_app()
            if app.player and app.player.sound:
                app.player.seek(instance.value)

            # Reset dragging state
            self.is_slider_being_dragged = False

            # Ensure UI updates
            self.update_play_pause_button()

            return True

        self.is_slider_being_dragged = False
        return False

    def on_volume_change(self, instance, value):
        """Change playback volume."""
        app = App.get_running_app()

        if not app.player:
            return

        try:
            app.player.set_volume(value)
        except Exception as e:
            print(f"Error changing volume: {e}")

    def add_to_playlist(self, instance):
        """Show dialog to add current recording to a playlist."""
        app = App.get_running_app()
        if not self.current_recording:
            return

        # Get the recording ID
        recording_id = self.current_recording[0]

        # Show the playlist selection dialog
        file_list_screen = app.root_layout.get_screen('file_list')
        if hasattr(file_list_screen, 'show_playlist_options'):
            file_list_screen.show_playlist_options(recording_id)

    def on_track_finished(self, *args):
        """Handle track completion event."""
        try:
            print("Track finished event received in playback screen")

            # First check if repeat mode is enabled
            if hasattr(self, 'repeat_enabled') and self.repeat_enabled:
                print("Repeat enabled, restarting track")
                app = App.get_running_app()
                if app.player and app.player.sound:
                    # Schedule the restart for the next frame to avoid VLC issues
                    Clock.schedule_once(lambda dt: app.player.play(), 0.1)

            # If not repeating, try to play next track in playlist
            elif hasattr(self, 'current_playlist_id') and self.current_playlist_id:
                success = self.play_next_in_playlist()
                if not success:
                    print("No next track available or error playing next track")
            else:
                print("Repeat not enabled and not in playlist, track will remain stopped")

        except Exception as e:
            print(f"Error handling track finished: {e}")

    def play_next_in_playlist(self):
        """Play the next track in the current playlist if available."""
        app = App.get_running_app()

        # Check if we're in a playlist
        if not hasattr(self, 'current_playlist_id') or not self.current_playlist_id:
            print("Not in a playlist - can't play next track")
            return False

        try:
            # Get all recordings in the current playlist
            playlist_recordings = app.database.get_playlist_recordings(self.current_playlist_id)

            if not playlist_recordings or len(playlist_recordings) <= 1:
                print("Playlist empty or has only one item")
                return False

            # Find current recording's position in playlist
            current_position = None
            for i, rec in enumerate(playlist_recordings):
                if rec[0] == self.current_recording[0]:  # Compare recording IDs
                    current_position = i
                    break

            if current_position is None:
                print("Current recording not found in playlist")
                return False

            # Check if there's a next track
            if current_position < len(playlist_recordings) - 1:
                next_recording = playlist_recordings[current_position + 1]
                print(f"Playing next track: {next_recording[1]}")  # Title is at index 1

                # Get playback screen
                playback_screen = app.root_layout.get_screen('playback')
                if playback_screen:
                    # Play the next recording
                    filepath = next_recording[3]  # filepath is at index 3

                    if app.player.load(filepath):
                        # Update playback info
                        self.current_recording = next_recording
                        self.update_playback_info(next_recording)

                        # Start playback
                        app.player.play()
                        return True

            print("End of playlist reached")
            return False

        except Exception as e:
            print(f"Error playing next track: {e}")
            return False

    def go_back(self, instance):
        """Navigate back to previous screen."""
        app = App.get_running_app()

        # Check where we came from
        if hasattr(self, 'source_screen') and self.source_screen == 'home':
            app.root_layout.current = 'home'
        else:
            # Default to file_list if no specific source
            app.root_layout.current = 'file_list'

    def on_leave(self):
        """Called when the screen is exited."""
        # Stop the UI update timer
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None

        # Unbind from track finished event
        app = App.get_running_app()
        if app.player:
            app.player.unbind(on_track_finished=self.on_track_finished)
