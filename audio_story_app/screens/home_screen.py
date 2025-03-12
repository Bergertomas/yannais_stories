from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.app import App
import os
import theme


class HomeScreen(Screen):
    """Main home screen for the app."""

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.build_ui()

    def on_enter(self):
        """Called when the screen is entered - refresh content."""
        # Clear existing content and rebuild
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        """Build the UI for the home screen."""
        # Use a layout with fixed width
        layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20),
            size_hint=(1, 1)
        )

        # Title
        title = Label(
            text="Audio Story App",
            font_size=dp(30),
            size_hint_y=None,
            height=dp(50),
            bold=True
        )
        layout.add_widget(title)

        # Recently added section
        recent_section = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(170)  # Fixed height
        )

        recent_label = Label(
            text="Recently Added",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        recent_label.bind(size=recent_label.setter('text_size'))
        recent_section.add_widget(recent_label)

        # Get recent recordings
        app = App.get_running_app()
        recent_recordings = self.get_recent_recordings(app.database, limit=3)

        # Add recordings or placeholder
        if recent_recordings:
            for recording in recent_recordings:
                # Make sure we're getting the actual data, not the object's attributes
                recording_id, title, description, filepath, duration, date_created, cover_art = recording

                recording_btn = Button(
                    text=title if title and isinstance(title, str) else "Untitled Recording",
                    size_hint_y=None,
                    height=dp(40),
                    background_normal='',
                    background_color=theme.PRIMARY_COLOR,
                    on_release=lambda x, rec_id=recording_id: self.play_recording(rec_id)
                )
                recent_section.add_widget(recording_btn)
        else:
            placeholder = Label(
                text="No recordings yet. Go to Import to add some!",
                size_hint_y=None,
                height=dp(50)
            )
            recent_section.add_widget(placeholder)

        layout.add_widget(recent_section)

        # Navigation section
        nav_section = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(300)  # Fixed height
        )

        nav_label = Label(
            text="Navigate To",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        nav_label.bind(size=nav_label.setter('text_size'))
        nav_section.add_widget(nav_label)

        # Navigation buttons
        file_list_btn = Button(
            text="All Recordings",
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=theme.PRIMARY_COLOR,
            on_release=lambda x: self.navigate_to('file_list')
        )
        nav_section.add_widget(file_list_btn)

        playlist_btn = Button(
            text="Playlists",
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=theme.PRIMARY_COLOR,
            on_release=lambda x: self.navigate_to('playlist')
        )
        nav_section.add_widget(playlist_btn)

        import_btn = Button(
            text="Import Audio",
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=theme.SUCCESS_COLOR,
            on_release=lambda x: self.navigate_to('import')
        )
        nav_section.add_widget(import_btn)

        settings_btn = Button(
            text="Settings",
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=theme.PRIMARY_COLOR,
            on_release=lambda x: self.navigate_to('settings')
        )
        nav_section.add_widget(settings_btn)

        layout.add_widget(nav_section)

        # Add spacer to prevent content from being too tight
        spacer = BoxLayout(size_hint_y=0.1)
        layout.add_widget(spacer)

        # Add the entire layout to the screen
        self.add_widget(layout)

    def get_recent_recordings(self, database, limit=3):
        """Get the most recently added recordings."""
        if database:
            try:
                all_recordings = database.get_all_recordings()
                return all_recordings[:limit] if all_recordings else []
            except Exception as e:
                print(f"Error fetching recent recordings: {e}")
                return []
        return []

    def navigate_to(self, screen_name):
        """Navigate to another screen."""
        app = App.get_running_app()
        app.root_layout.current = screen_name

    def play_recording(self, recording_id):
        """Play a specific recording."""
        app = App.get_running_app()
        try:
            recording = app.database.get_recording(recording_id)

            if recording:
                # Navigate to the playback screen first
                app.root_layout.current = 'playback'

                # Access the playback screen and update it with current recording info
                playback_screen = app.root_layout.get_screen('playback')

                # Load the recording into the player
                if app.player.load(recording[3]):  # filepath is at index 3
                    # Wait a moment for UI to update
                    from kivy.clock import Clock
                    def start_playback(dt):
                        playback_screen.update_playback_info(recording)
                        app.player.play()

                    Clock.schedule_once(start_playback, 0.1)
                else:
                    print(f"Failed to load recording: {recording[1]}")
            else:
                print(f"Recording not found: ID {recording_id}")
        except Exception as e:
            print(f"Error playing recording: {e}")
