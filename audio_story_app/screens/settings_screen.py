from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.properties import NumericProperty
from kivy.config import Config


class SettingsScreen(Screen):
    volume = NumericProperty(1.0)

    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        layout = BoxLayout(orientation='vertical')
        volume_slider = Slider(min=0, max=1, value=self.volume)
        volume_slider.bind(value=self.set_volume)
        layout.add_widget(Label(text='Volume'))
        layout.add_widget(volume_slider)
        theme_btn = Button(text='Switch Theme (Light/Dark)')
        theme_btn.bind(on_press=self.switch_theme)
        layout.add_widget(theme_btn)
        self.add_widget(layout)

    def set_volume(self, instance, value):
        self.volume = value
        self.player.set_volume(value)
        Config.set('audio', 'volume', value)
        Config.write()

    def switch_theme(self, *args):
        # Toggle between light and dark themes
        current_theme = Config.get('ui', 'theme', fallback='light')
        new_theme = 'dark' if current_theme == 'light' else 'light'
        Config.set('ui', 'theme', new_theme)
        Config.write()
        # Apply theme (update colors in app)