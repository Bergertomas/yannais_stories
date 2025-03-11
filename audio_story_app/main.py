from kivy.app import App
from screens.home_screen import HomeScreen
from screens.file_list_screen import FileListScreen
from screens.playlist_screen import PlaylistScreen
from screens.settings_screen import SettingsScreen
from screens.import_screen import ImportScreen
from database import init_db
from player import Player
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.lang import Builder

Builder.load_file('kv_files/playlist_screen.kv')  # Adjust path to match your structure


class AudioStoryApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(HomeScreen(name='home'))
        Config.setdefaults('audio', {'volume': 1.0})
        Config.setdefaults('ui', {'theme': 'light'})
        # Initialize the audio player as an app attribute
        self.player = Player()
        # Set up the database
        init_db()
        # Create the ScreenManager to handle navigation
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(FileListScreen(name='file_list'))
        sm.add_widget(PlaylistScreen(name='playlist_management'))
        sm.add_widget(SettingsScreen(self.player, name='settings'))
        sm.add_widget(ImportScreen(name='import'))
        return sm


if __name__ == '__main__':
    AudioStoryApp().run()
