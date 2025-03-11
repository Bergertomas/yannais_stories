from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
import sqlite3
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from miscel.audio_story_app.database import get_all_recordings


class IconButton(ButtonBehavior, Image):
    pass


class PlaybackScreen(Screen):
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.sound = None
        layout = BoxLayout(orientation='vertical')
        self.progress_slider = Slider(min=0, max=1, value=0)
        self.progress_slider.bind(on_touch_move=self.seek)
        # controls.add_widget(IconButton(source='play.png', on_press=self.play))
        # controls.add_widget(IconButton(source='pause.png', on_press=self.pause))
        # controls.add_widget(IconButton(source='stop.png', on_press=self.stop))
        layout.add_widget(self.progress_slider)
        self.time_label = Label(text='0:00 / 0:00')
        layout.add_widget(self.time_label)
        controls = BoxLayout(orientation='horizontal')
        controls.add_widget(Button(text='Play', on_press=self.play))
        controls.add_widget(Button(text='Pause', on_press=self.pause))
        controls.add_widget(Button(text='Stop', on_press=self.stop))
        layout.add_widget(controls)
        self.add_widget(layout)
        Clock.schedule_interval(self.update_progress, 1)
        options = BoxLayout(orientation='horizontal')
        shuffle_btn = ToggleButton(text='Shuffle')
        shuffle_btn.bind(on_press=lambda x: self.set_shuffle(shuffle_btn.state))
        repeat_btn = ToggleButton(text='Repeat')
        repeat_btn.bind(on_press=lambda x: self.set_repeat(repeat_btn.state))
        options.add_widget(shuffle_btn)
        options.add_widget(repeat_btn)
        layout.add_widget(options)

    def play(self, *args):
        if self.audio_path:
            if not self.sound:
                self.sound = SoundLoader.load(self.audio_path)
            if self.sound:
                self.sound.play()
                self.status_label.text = f'Playing: {self.audio_path}'
            else:
                self.status_label.text = 'Error: Could not load the audio file'
        else:
            self.status_label.text = 'No audio file selected'

    def pause(self, *args):
        if self.sound:
            self.sound.stop()

    def stop(self, *args):
        if self.sound:
            self.sound.stop()
            self.progress_slider.value = 0

    def seek(self, instance, touch):
        if self.sound and self.progress_slider.collide_point(*touch.pos):
            self.sound.seek(self.progress_slider.value)

    def update_progress(self, dt):
        if self.sound and self.sound.state == 'play':
            self.progress_slider.max = self.player.current_sound.length
            self.progress_slider.value = self.player.current_sound.get_pos()
            self.time_label.text = f'{self.format_time(self.player.current_sound.get_pos())} / {self.format_time(self.player.current_sound.length)}'

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f'{minutes}:{seconds:02d}'

    def set_shuffle(self, state):
        self.player.shuffle = state == 'down'

    def set_repeat(self, state):
        self.player.repeat = state == 'down'