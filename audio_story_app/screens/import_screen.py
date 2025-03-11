from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import os
from miscel.audio_story_app.database import add_recording
from datetime import date
from kivy.app import App


class ImportScreen(Screen):
    def __init__(self, **kwargs):
        super(ImportScreen, self).__init__(**kwargs)
        # Create a layout for the screen
        layout = BoxLayout(orientation='vertical')

        # Add the "Back to Home" button
        back_button = Button(
            text='Back to Home',
            size_hint_y=None,
            height=50,
            background_color=(0.8, 0.2, 0.2, 1)  # Reddish color
        )
        back_button.bind(on_press=self.go_home)  # Bind to the go_home method
        layout.add_widget(back_button)

        # Add the file chooser
        self.file_chooser = FileChooserIconView(filters=['*.mp3', '*.wav'])
        layout.add_widget(self.file_chooser)
        self.file_chooser.bind(on_submit=self.on_file_selected)

        self.add_widget(layout)

    def go_home(self, *args):
        """Navigate back to the Home screen."""
        self.manager.current = 'home'

    def on_file_selected(self, file_chooser, selected_path, *args):
        # Handle file selection by copying to app directory and adding to database
        app_dir = os.path.join(App.get_running_app().user_data_dir, 'audio_files')
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)
        file_name = os.path.basename(selected_path[0])
        new_path = os.path.join(app_dir, file_name)
        with open(selected_path[0], 'rb') as src, open(new_path, 'wb') as dst:
            dst.write(src.read())
        title = file_name
        description = ''
        date_str = str(date.today())
        try:
            add_recording(title, description, date_str, '', selected_path)
            self.manager.current = 'file_list'
        except Exception as e:
            Popup(title='Error', content=Label(text=f'Import failed: {str(e)}'), size_hint=(0.6, 0.4)).open()
