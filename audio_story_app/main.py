from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
import os
import theme
import time
from datetime import datetime


# Set minimum window size for desktop
Config.set('graphics', 'minimum_width', '400')
Config.set('graphics', 'minimum_height', '600')

# Load KV file
try:
    # Try to load the enhanced KV file
    Builder.load_file('kv_files/audio_story.kv')
except Exception as e:
    print(f"Error loading enhanced KV file: {e}")
    try:
        # Fall back to original KV file
        Builder.load_file('kv_files/audio_story.kv')
    except Exception as e:
        print(f"Error loading KV file: {e}")

# Import database and player
from database import Database
from player import player as global_player
from mini_player import MiniPlayer

# Import screens
from screens.home_screen import DreamTalesHomeScreen
from screens.file_list_screen import FileListScreen
from screens.import_screen import ImportScreen
from screens.playlist_screen import PlaylistScreen
from screens.settings_screen import SettingsScreen



class RootLayout(FloatLayout):
    """Root layout that contains both the screen manager and mini player."""

    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs)

        # Create screen manager
        self.sm = ScreenManager(transition=SlideTransition())

        # Add screens
        self.sm.add_widget(DreamTalesHomeScreen(name='home'))
        self.sm.add_widget(FileListScreen(name='file_list'))
        self.sm.add_widget(ImportScreen(name='import'))
        self.sm.add_widget(PlaylistScreen(name='playlist'))
        self.sm.add_widget(SettingsScreen(name='settings'))

        # Use our updated playback screen
        from screens.playback_screen import PlaybackScreen
        self.sm.add_widget(PlaybackScreen(name='playback'))

        # Add screen manager to the layout (takes full size)
        self.sm.size_hint = (1, 1)
        self.add_widget(self.sm)

        # Create mini player (will be at the bottom of screen)
        self.mini_player = MiniPlayer()
        self.mini_player.pos_hint = {'x': 0, 'bottom': 0}
        self.mini_player.size_hint_x = 1
        self.add_widget(self.mini_player)

    @property
    def current(self):
        """Provide access to the current screen name."""
        return self.sm.current

    @current.setter
    def current(self, value):
        """Allow setting the current screen."""
        if self.sm.has_screen(value):
            self.sm.current = value
        else:
            print(f"Screen {value} does not exist")

    def get_screen(self, name):
        """Get a screen by name."""
        if self.sm.has_screen(name):
            return self.sm.get_screen(name)
        return None


class AudioStoryApp(App):
    """Main application class for the Audio Story App."""

    def build(self):
        """Build and return the app's UI."""
        # Set app title
        self.title = "Audio Story App"

        # Apply theme
        theme.apply_theme(self)

        # Create necessary directories
        self.ensure_directories()

        # Initialize database
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'audio_story.db')
        self.database = Database(db_path)

        # Set up audio player
        self.player = global_player

        # Set default volume from settings
        try:
            default_volume = float(self.database.get_setting('default_volume', '0.8'))
            self.player.set_volume(default_volume)
        except Exception as e:
            print(f"Error setting default volume: {e}")

        # Automatically scan and import recordings from the recordings directory
        self.auto_import_recordings()

        # Create root layout
        self.root_layout = RootLayout()

        # Set up keyboard/back button handling
        self.bind_keys()

        return self.root_layout

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        app_dir = os.path.dirname(os.path.abspath(__file__))

        # Data directory
        data_dir = os.path.join(app_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)

        # Recordings directory
        self.recordings_dir = os.path.join(data_dir, 'recordings')
        os.makedirs(self.recordings_dir, exist_ok=True)

    def auto_import_recordings(self):
        """Automatically scan the recordings directory and import any new files with proper duration detection."""
        print("Scanning recordings directory for new files...")

        if not hasattr(self, 'recordings_dir') or not os.path.exists(self.recordings_dir):
            print("Recordings directory not found")
            return

        # Get all existing recordings in the database
        existing_recordings = self.database.get_all_recordings()
        existing_filepaths = [rec[3] for rec in existing_recordings]  # filepath is at index 3

        # Count for imported files
        imported_count = 0
        updated_count = 0

        # Define supported audio extensions
        supported_extensions = ['.mp3', '.wav', '.ogg', '.m4a']

        # First, check for recordings with missing duration
        for recording in existing_recordings:
            recording_id, title, description, filepath, duration, date_created, cover_art = recording

            # If duration is missing or zero, try to detect it
            if duration is None or duration <= 0:
                if os.path.exists(filepath):
                    try:
                        from kivy.core.audio import SoundLoader
                        sound = SoundLoader.load(filepath)

                        if sound:
                            # Get and update duration
                            new_duration = sound.length
                            sound.unload()  # Free resources

                            if new_duration > 0:
                                # Update the database with the correct duration
                                self.database.update_recording(
                                    recording_id=recording_id,
                                    duration=new_duration
                                )
                                updated_count += 1
                                print(f"Updated duration for '{title}': {new_duration} seconds")
                    except Exception as e:
                        print(f"Error updating duration for {filepath}: {e}")

        # Now check for any new files to import
        for filename in os.listdir(self.recordings_dir):
            filepath = os.path.join(self.recordings_dir, filename)

            # Skip directories and non-audio files
            if os.path.isdir(filepath):
                continue

            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in supported_extensions:
                continue

            # Skip files already in the database
            if filepath in existing_filepaths:
                continue

            try:
                # Use filename as title (without extension)
                title = os.path.splitext(filename)[0]

                # Try to get duration using SoundLoader
                from kivy.core.audio import SoundLoader
                sound = SoundLoader.load(filepath)

                duration = 0
                if sound:
                    # Get duration
                    duration = sound.length
                    # Unload the sound to free resources
                    sound.unload()
                    print(f"Detected duration for {filename}: {duration} seconds")
                else:
                    print(f"Could not detect duration for {filename}, using 0")

                # Create a file modified date
                file_stats = os.stat(filepath)
                last_modified = datetime.fromtimestamp(file_stats.st_mtime).isoformat()

                # Add to database with detected duration
                self.database.add_recording(
                    title=title,
                    description="Auto-imported recording",
                    filepath=filepath,
                    duration=duration,  # Now we have the actual duration
                    cover_art=None
                )

                imported_count += 1
                print(f"Auto-imported: {filename}")

            except Exception as e:
                print(f"Error auto-importing {filename}: {e}")

        if imported_count > 0 or updated_count > 0:
            message = []
            if imported_count > 0:
                message.append(f"Auto-imported {imported_count} new recording(s)")
            if updated_count > 0:
                message.append(f"Updated duration for {updated_count} recording(s)")
            print(", ".join(message))
        else:
            print("No new recordings found to import")

    def bind_keys(self):
        """Set up keyboard and back button handling."""
        # Handle keyboard events
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self.root_layout)
        if self._keyboard:
            self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Handle Android back button
        if platform == 'android':
            try:
                from android.hardware import keyboard
                keyboard.hook_keyboard([27], self.handle_back_button)
            except ImportError:
                pass

    def _keyboard_closed(self):
        """Handle keyboard being closed."""
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Handle keyboard button presses."""
        if keycode[1] == 'escape':
            return self.handle_back_button()
        return False

    def handle_back_button(self, *args):
        """Handle back button press based on current screen."""
        if not hasattr(self, 'root_layout') or not self.root_layout:
            return False

        current = self.root_layout.current

        if current == 'home':
            # Confirm exit
            self.confirm_exit()
            return True
        elif current == 'playback':
            # Go back but don't stop playback
            self.root_layout.current = 'file_list'
            return True
        else:
            # Navigate back to home
            self.root_layout.current = 'home'
            return True

    def confirm_exit(self):
        """Show exit confirmation dialog."""
        from kivy.uix.popup import Popup
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.metrics import dp

        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        content.add_widget(Label(text="Are you sure you want to exit?"))

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        popup = Popup(
            title="Exit App",
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=True
        )

        cancel_btn = Button(
            text="Cancel",
            on_release=lambda x: popup.dismiss()
        )
        buttons.add_widget(cancel_btn)

        exit_btn = Button(
            text="Exit",
            on_release=lambda x: self.stop()
        )
        buttons.add_widget(exit_btn)

        content.add_widget(buttons)

        popup.open()

    def on_pause(self):
        """Handle app pause (for Android)."""
        # Allow the app to continue in the background
        background_playback = self.database.get_setting('background_playback', 'True') == 'True'

        if not background_playback and self.player and self.player.is_playing:
            self.player.pause()

        return True

    def on_resume(self):
        """Handle app resume (for Android)."""
        # Scan for new recordings when app is resumed
        self.auto_import_recordings()

    def on_stop(self):
        """Clean up resources when the app stops."""
        # Stop any playback
        if hasattr(self, 'player') and self.player and self.player.is_playing:
            self.player.stop()

        # Close database connection
        if hasattr(self, 'database') and self.database:
            self.database.close()


if __name__ == '__main__':
    AudioStoryApp().run()
