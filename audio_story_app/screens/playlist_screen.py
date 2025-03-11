from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from miscel.audio_story_app.database import (get_playlist_recordings, update_playlist, delete_playlist,
                                             reorder_playlist_recordings, create_playlist, get_all_playlists,
                                             update_playlist, delete_playlist, reorder_playlist_recordings,
                                             get_all_recordings)


class PlaylistScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        self.display_playlists()
    def on_enter(self):
        self.ids.playlists_list.clear_widgets()
        playlists = get_all_playlists()
        # Remove the temporary override unless it's intentional for testing
        # playlists = ['Playlist 1', 'Playlist 2', 'Playlist 3']
        for playlist in playlists:
            btn = Button(text=playlist[1], size_hint_y=None, height=40)
            btn.bind(on_press=lambda x, p=playlist: self.view_playlist(p))
            self.ids.playlists_list.add_widget(btn)

    def add_recordings_to_playlist(self, playlist_id):
        recordings = get_all_recordings()  # From your database module
        content = BoxLayout(orientation='vertical')
        selected_recordings = []
        for rec in recordings:
            row = BoxLayout(orientation='horizontal')
            checkbox = CheckBox()
            checkbox.bind(active=lambda cb, value, r=rec: selected_recordings.append(
                r[0]) if value else selected_recordings.remove(r[0]) if r[0] in selected_recordings else None)
            row.add_widget(checkbox)
            row.add_widget(Label(text=rec[1]))  # Assuming title is at index 1
            content.add_widget(row)
        add_btn = Button(text='Add Selected')
        add_btn.bind(on_press=lambda x: self._add_to_playlist(playlist_id, selected_recordings))
        content.add_widget(add_btn)
        self.popup = Popup(title='Add Recordings', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def create_new_playlist(self):
        content = BoxLayout(orientation='vertical')
        name_input = TextInput(hint_text='Playlist Name')
        desc_input = TextInput(hint_text='Description')
        create_btn = Button(text='Create')
        create_btn.bind(on_press=lambda x: self._create_playlist(name_input.text, desc_input.text))
        content.add_widget(name_input)
        content.add_widget(desc_input)
        content.add_widget(create_btn)
        self.popup = Popup(title='Create New Playlist', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def _create_playlist(self, name, description):
        create_playlist(name, description)
        self.popup.dismiss()
        self.on_enter()
        Popup(title='Success', content=Label(text='Playlist created!'), size_hint=(0.6, 0.4)).open()

    def view_playlist(self, playlist):
        recordings = get_playlist_recordings(playlist[0])
        content = BoxLayout(orientation='vertical')
        for idx, rec in enumerate(recordings):
            row = BoxLayout(orientation='horizontal')
            label = Label(text=rec[1])
            up_btn = Button(text='↑', size_hint_x=0.2)
            up_btn.bind(on_press=lambda x, i=idx: self.move_recording_up(playlist[0], i))
            down_btn = Button(text='↓', size_hint_x=0.2)
            down_btn.bind(on_press=lambda x, i=idx: self.move_recording_down(playlist[0], i))
            row.add_widget(label)
            row.add_widget(up_btn)
            row.add_widget(down_btn)
            content.add_widget(row)
        Popup(title=f'Playlist: {playlist[1]}', content=content, size_hint=(0.8, 0.8)).open()

    def move_recording_up(self, playlist_id, index):
        recordings = get_playlist_recordings(playlist_id)
        if index > 0:
            recordings[index], recordings[index - 1] = recordings[index - 1], recordings[index]
            reorder_playlist_recordings(playlist_id, recordings)
            self.view_playlist((playlist_id,))

    def move_recording_down(self, playlist_id, index):
        recordings = get_playlist_recordings(playlist_id)
        if index < len(recordings) - 1:
            recordings[index], recordings[index + 1] = recordings[index + 1], recordings[index]
            reorder_playlist_recordings(playlist_id, recordings)
            self.view_playlist((playlist_id,))

    def _add_to_playlist(self, playlist_id, recording_ids):
        for order_num, rec_id in enumerate(recording_ids):
            self.add_recording_to_playlist(playlist_id, rec_id, order_num)
        self.popup.dismiss()

    def edit_playlist(self, playlist):
        content = BoxLayout(orientation='vertical')
        name_input = TextInput(text=playlist[1], hint_text='Playlist Name')
        desc_input = TextInput(text=playlist[2], hint_text='Description')
        save_btn = Button(text='Save Changes')
        save_btn.bind(on_press=lambda x: self._update_playlist(playlist[0], name_input.text, desc_input.text))
        content.add_widget(name_input)
        content.add_widget(desc_input)
        content.add_widget(save_btn)
        self.popup = Popup(title='Edit Playlist', content=content, size_hint=(0.8, 0.8))
        self.popup.open()

    def _update_playlist(self, playlist_id, name, description):
        update_playlist(playlist_id, name, description)
        self.popup.dismiss()
        self.on_enter()  # Refresh playlist list

    def delete_playlist(self, playlist):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Are you sure?'))
        confirm_btn = Button(text='Delete')
        confirm_btn.bind(on_press=lambda x: self._delete_playlist(playlist[0]))
        content.add_widget(confirm_btn)
        content.add_widget(Button(text='Cancel', on_press=lambda x: self.popup.dismiss()))
        self.popup = Popup(title='Confirm Delete', content=content, size_hint=(0.6, 0.4))
        self.popup.open()

    def _delete_playlist(self, playlist_id):
        delete_playlist(playlist_id)
        self.popup.dismiss()
        self.on_enter()

    def play_recording(self, audio_path):
        from kivy.app import App
        app = App.get_running_app()
        app.player.play(audio_path)

    def display_playlists(self):
        self.layout.clear_widgets()
        # For now, hardcode a playlist (replace with actual playlist fetching)
        playlists = ["Favorites"]
        for playlist in playlists:
            btn = Button(text=playlist)
            btn.bind(on_press=lambda x, p=playlist: self.view_playlist(p))
            self.layout.add_widget(btn)

    def view_playlist(self, playlist_name):
        recordings = get_playlist_recordings(playlist_name)
        content = BoxLayout(orientation='vertical')
        for rec_id, title, audio_path in recordings:
            row = BoxLayout(orientation='horizontal')
            row.add_widget(Label(text=title))
            play_btn = Button(text='Play')
            play_btn.bind(on_press=lambda x, path=audio_path: self.navigate_to_playback(path))
            row.add_widget(play_btn)
            content.add_widget(row)
        Popup(title=f'Playlist: {playlist_name}', content=content, size_hint=(0.8, 0.8)).open()

    def navigate_to_playback(self, audio_path):
        from kivy.app import App
        app = App.get_running_app()
        playback_screen = app.root.get_screen('playback')
        playback_screen.audio_path = audio_path
        app.root.current = 'playback'


