import sqlite3

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from miscel.audio_story_app.database import get_all_recordings
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

Builder.load_file('kv_files/file_list_screen.kv')

class RecordingItem(BoxLayout):
    title = StringProperty('')
    description = StringProperty('')
    audio_path = StringProperty('')


def fetch_recordings():
    conn = sqlite3.connect('your_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, audio_path FROM recordings")
    recordings = cursor.fetchall()
    conn.close()
    return recordings

class FileListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        self.display_recordings()

    def display_recordings(self):
        self.layout.clear_widgets()
        recordings = get_all_recordings()
        for rec_id, title, audio_path in recordings:
            row = BoxLayout(orientation='horizontal')
            row.add_widget(Label(text=title))
            play_btn = Button(text='Play')
            play_btn.bind(on_press=lambda x, path=audio_path: self.navigate_to_playback(path))
            row.add_widget(play_btn)
            self.layout.add_widget(row)

    def navigate_to_playback(self, audio_path):
        from kivy.app import App
        app = App.get_running_app()
        playback_screen = app.root.get_screen('playback')
        playback_screen.audio_path = audio_path
        app.root.current = 'playback'

