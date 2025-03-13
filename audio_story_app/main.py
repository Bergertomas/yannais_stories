from kivy.app import App
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
import os
import theme

# Set minimum window size for desktop
Config.set('graphics', 'minimum_width', '400')
Config.set('graphics', 'minimum_height', '600')

# Try to directly load the KV files we know should exist
try:
    Builder.load_file('kv_files/audio_story.kv')
    print("Loaded audio_story.kv")
except Exception as e:
    print(f"Error loading audio_story.kv: {e}")

try:
    Builder.load_file('kv_files/home_screen.kv')
    print("Loaded home_screen.kv")
except Exception as e:
    print(f"Error loading home_screen.kv: {e}")

try:
    Builder.load_file('kv_files/file_list_screen.kv')
    print("Loaded file_list_screen.kv")
except Exception as e:
    print(f"Error loading file_list_screen.kv: {e}")

try:
    Builder.load_file('kv_files/playlist_screen.kv')
    print("Loaded playlist_screen.kv")
except Exception as e:
    print(f"Error loading playlist_screen.kv: {e}")

try:
    Builder.load_file('kv_files/settings_screen.kv')
    print("Loaded settings_screen.kv")
except Exception as e:
    print(f"Error loading settings_screen.kv: {e}")

# Import database and player
from database import Database
from player import player as global_player
from mini_player import MiniPlayer

# Import screens
from screens.home_screen import HomeScreen
from screens.file_list_screen import FileListScreen
from screens.import_screen import ImportScreen
from screens.playlist_screen import PlaylistScreen
from screens.settings_screen import SettingsScreen
from screens.playback_screen import PlaybackScreen


class RootLayout(FloatLayout):
    """Root layout that contains both the screen manager and mini player."""

    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs)
        print("Initializing RootLayout")

        # Create a transparent background for the entire layout
        with self.canvas.before:
            Color(0, 0, 0, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        # Import and add StarField
        try:
            from starfield import StarField
            self.starfield = StarField()
            self.add_widget(self.starfield)
            print("Added StarField as background")
        except Exception as e:
            print(f"Error adding StarField: {e}")

        # Create screen manager
        self.sm = ScreenManager(transition=SlideTransition())
        print("Created ScreenManager")

        # Add screens
        try:
            self.sm.add_widget(HomeScreen(name='home'))
            print("Added HomeScreen")
            self.sm.add_widget(FileListScreen(name='file_list'))
            print("Added FileListScreen")
            self.sm.add_widget(ImportScreen(name='import'))
            print("Added ImportScreen")
            self.sm.add_widget(PlaylistScreen(name='playlist'))
            print("Added PlaylistScreen")
            self.sm.add_widget(SettingsScreen(name='settings'))
            print("Added SettingsScreen")
            self.sm.add_widget(PlaybackScreen(name='playback'))
            print("Added PlaybackScreen")
        except Exception as e:
            print(f"Error adding screens: {e}")

        # Set default screen
        self.sm.current = 'home'
        print(f"Set current screen to: {self.sm.current}")

        # Add screen manager to the layout (takes full size)
        self.sm.size_hint = (1, 1)
        self.add_widget(self.sm)
        print("Added ScreenManager to RootLayout")

        # Create mini player (will be at the bottom of screen)
        try:
            self.mini_player = MiniPlayer()
            self.mini_player.pos_hint = {'x': 0, 'bottom': 0}
            self.mini_player.size_hint_x = 1
            self.add_widget(self.mini_player)
            print("Added MiniPlayer to RootLayout")
        except Exception as e:
            print(f"Error adding mini player: {e}")

    def _update_rect(self, instance, value):
        """Update the background rectangle when size changes"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    @property
    def current(self):
        """Provide access to the current screen name."""
        return self.sm.current

    @current.setter
    def current(self, value):
        """Allow setting the current screen."""
        if self.sm.has_screen(value):
            self.sm.current = value
            print(f"Changed screen to: {value}")
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
        print("Building AudioStoryApp")

        # Set app title
        self.title = "Audio Story App"

        # Apply theme
        theme.apply_theme(self)
        print("Applied theme")

        # Create necessary directories
        self.ensure_directories()
        print("Ensured directories")

        # Initialize database
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'audio_story.db')
        self.database = Database(db_path)
        print("Initialized database")

        # Set up audio player
        self.player = global_player
        print("Set up audio player")

        # Set default volume from settings
        try:
            default_volume = float(self.database.get_setting('default_volume', '0.8'))
            self.player.set_volume(default_volume)
            print(f"Set default volume: {default_volume}")
        except Exception as e:
            print(f"Error setting default volume: {e}")

        # Create root layout
        try:
            self.root_layout = RootLayout()
            from theme import StarField
            # Create starfield and add it as the bottom-most widget
            starfield = StarField()
            self.root_layout.add_widget(starfield, index=len(self.root_layout.children))
            print("Added starfield directly to root_layout")
            print("Created RootLayout")
        except Exception as e:
            print(f"Error creating RootLayout: {e}")

        # Set up keyboard/back button handling
        self.bind_keys()
        print("Bound keys")

        return self.root_layout

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        app_dir = os.path.dirname(os.path.abspath(__file__))

        # Data directory
        data_dir = os.path.join(app_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)

        # Recordings directory
        recordings_dir = os.path.join(data_dir, 'recordings')
        os.makedirs(recordings_dir, exist_ok=True)

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
        pass

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
