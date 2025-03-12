from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.metrics import dp
from kivy.app import App
import os
import shutil


class SettingsScreen(Screen):
    """Screen for app settings and preferences."""

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.background_switch = None
        self.default_volume_slider = None

    def on_enter(self):
        """Build the UI when the screen is entered."""
        self.build_ui()

    def build_ui(self):
        """Build the UI for the settings screen."""
        self.clear_widgets()

        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))

        # Header with title and back button
        header = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        back_btn = Button(
            text="Back",
            size_hint_x=None,
            width=dp(80),
            on_release=self.go_back
        )
        header.add_widget(back_btn)

        title = Label(
            text="Settings",
            font_size=dp(24)
        )
        header.add_widget(title)

        main_layout.add_widget(header)

        # Background playback setting
        bg_layout = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        bg_label = Label(
            text="Allow background playback",
            halign='left',
            size_hint_x=0.7,
            text_size=(dp(300), dp(50))
        )
        bg_layout.add_widget(bg_label)

        app = App.get_running_app()
        bg_value = app.database.get_setting('background_playback', 'True') == 'True'

        self.background_switch = Switch(
            active=bg_value,
            size_hint_x=0.3
        )
        self.background_switch.bind(active=self.on_background_switch)
        bg_layout.add_widget(self.background_switch)

        main_layout.add_widget(bg_layout)

        # Default volume setting
        volume_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(5)
        )

        volume_label = Label(
            text="Default Volume",
            halign='left',
            size_hint_y=None,
            height=dp(30),
            text_size=(dp(300), dp(30))
        )
        volume_layout.add_widget(volume_label)

        vol_slider_layout = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        vol_min_label = Label(
            text="0%",
            size_hint_x=0.1
        )
        vol_slider_layout.add_widget(vol_min_label)

        vol_value = float(app.database.get_setting('default_volume', '0.8'))

        self.default_volume_slider = Slider(
            min=0,
            max=1,
            value=vol_value,
            size_hint_x=0.7
        )
        self.default_volume_slider.bind(value=self.on_volume_slider)
        vol_slider_layout.add_widget(self.default_volume_slider)

        self.vol_value_label = Label(
            text=f"{int(vol_value * 100)}%",
            size_hint_x=0.2
        )
        vol_slider_layout.add_widget(self.vol_value_label)

        volume_layout.add_widget(vol_slider_layout)

        main_layout.add_widget(volume_layout)

        # Storage management section
        storage_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150),
            spacing=dp(10)
        )

        storage_title = Label(
            text="Storage Management",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            text_size=(dp(300), dp(30))
        )
        storage_layout.add_widget(storage_title)

        # Calculate storage usage
        storage_info = self.get_storage_info()

        storage_label = Label(
            text=f"Used space: {storage_info['used']}\nFiles: {storage_info['files']}",
            size_hint_y=None,
            height=dp(50),
            halign='left',
            text_size=(dp(300), dp(50))
        )
        storage_layout.add_widget(storage_label)

        clear_btn = Button(
            text="Clear All Recordings",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            on_release=self.confirm_clear_data
        )
        storage_layout.add_widget(clear_btn)

        main_layout.add_widget(storage_layout)

        # App info section
        info_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(5)
        )

        info_title = Label(
            text="App Information",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            text_size=(dp(300), dp(30))
        )
        info_layout.add_widget(info_title)

        version_label = Label(
            text="Audio Story App v1.0\nDeveloped with Kivy",
            size_hint_y=None,
            height=dp(50),
            halign='left',
            text_size=(dp(300), dp(50))
        )
        info_layout.add_widget(version_label)

        main_layout.add_widget(info_layout)

        self.add_widget(main_layout)

    def on_background_switch(self, instance, value):
        """Save the background playback setting."""
        app = App.get_running_app()
        app.database.set_setting('background_playback', str(value))

    def on_volume_slider(self, instance, value):
        """Save the default volume setting."""
        app = App.get_running_app()
        app.database.set_setting('default_volume', str(value))

        # Update the label
        self.vol_value_label.text = f"{int(value * 100)}%"

        # Also update the current volume if player exists
        if app.player:
            app.player.set_volume(value)

    def get_storage_info(self):
        """Calculate storage usage."""
        app = App.get_running_app()
        recordings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'recordings')

        total_size = 0
        file_count = 0

        try:
            if os.path.exists(recordings_dir):
                for file in os.listdir(recordings_dir):
                    file_path = os.path.join(recordings_dir, file)
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)
                        file_count += 1
        except Exception as e:
            print(f"Error calculating storage: {e}")

        # Convert bytes to human-readable format
        if total_size < 1024:
            size_str = f"{total_size} bytes"
        elif total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        else:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"

        return {
            'used': size_str,
            'files': file_count
        }

    def confirm_clear_data(self, instance):
        """Show confirmation dialog before clearing all data."""
        from kivy.uix.popup import Popup

        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        content.add_widget(Label(
            text="Are you sure you want to delete ALL recordings?\n\nThis cannot be undone!"
        ))

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(20)
        )

        cancel_btn = Button(
            text="Cancel",
            on_release=lambda x: popup.dismiss()
        )
        buttons.add_widget(cancel_btn)

        clear_btn = Button(
            text="Delete All",
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            on_release=lambda x: self.clear_all_data(popup)
        )
        buttons.add_widget(clear_btn)

        content.add_widget(buttons)

        popup = Popup(
            title="Confirm Delete All",
            content=content,
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def clear_all_data(self, popup):
        """Clear all recordings and reset the database."""
        app = App.get_running_app()

        try:
            # Stop any playback
            if app.player:
                app.player.stop()

            # Clear the database (by recreating tables)
            app.database.cursor.execute("DROP TABLE IF EXISTS recordings")
            app.database.cursor.execute("DROP TABLE IF EXISTS playlists")
            app.database.cursor.execute("DROP TABLE IF EXISTS playlist_items")
            app.database.conn.commit()
            app.database.create_tables()

            # Delete all recording files
            recordings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'recordings')
            if os.path.exists(recordings_dir):
                for file in os.listdir(recordings_dir):
                    file_path = os.path.join(recordings_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

            popup.dismiss()

            # Show success message
            self.show_message("All recordings and playlists have been deleted")

            # Refresh UI
            self.build_ui()

        except Exception as e:
            popup.dismiss()
            self.show_message(f"Error clearing data: {str(e)}")

    def go_back(self, instance):
        """Navigate back to the home screen."""
        app = App.get_running_app()
        app.root.current = 'home'

    def show_message(self, message):
        """Show a simple message popup."""
        from kivy.uix.popup import Popup

        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message))
        btn = Button(
            text="OK",
            size_hint_y=None,
            height=dp(50),
            on_release=lambda x: popup.dismiss()
        )
        content.add_widget(btn)

        popup = Popup(
            title="Message",
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=True
        )
        popup.open()
