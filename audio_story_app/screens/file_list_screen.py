from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime
import os

import theme


class FileListScreen(Screen):
    """Screen for displaying and managing all audio recordings."""

    def __init__(self, **kwargs):
        super(FileListScreen, self).__init__(**kwargs)
        self.recordings_layout = None
        self.search_input = None

    def on_enter(self):
        """Build the UI when the screen is entered."""
        self.build_ui()

    def build_ui(self):
        """Build the UI for the file list screen."""
        self.clear_widgets()

        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

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
            text="All Recordings",
            font_size=dp(24)
        )
        header.add_widget(title)

        main_layout.add_widget(header)

        # Search bar
        search_layout = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=[0, dp(5)]
        )

        self.search_input = TextInput(
            hint_text="Search recordings...",
            multiline=False,
            size_hint_x=0.8,
            height=dp(40),
            on_text_validate=self.search_recordings
        )
        search_layout.add_widget(self.search_input)

        search_btn = Button(
            text="Search",
            size_hint_x=0.2,
            on_release=self.search_recordings
        )
        search_layout.add_widget(search_btn)

        main_layout.add_widget(search_layout)

        # Recordings list in a ScrollView
        scroll_view = ScrollView()

        # GridLayout for the list of recordings
        self.recordings_layout = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        # The height will be set dynamically based on children
        self.recordings_layout.bind(minimum_height=self.recordings_layout.setter('height'))

        scroll_view.add_widget(self.recordings_layout)
        main_layout.add_widget(scroll_view)

        # Add button for importing audio
        import_layout = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=[dp(10), dp(10)]
        )

        import_btn = Button(
            text="Import New Audio",
            background_normal='',
            background_color=theme.SUCCESS_COLOR,
            on_release=self.go_to_import
        )
        import_layout.add_widget(import_btn)

        main_layout.add_widget(import_layout)

        self.add_widget(main_layout)

        # Load and display recordings
        self.load_recordings()

    def load_recordings(self, search_term=None):
        """Load recordings from the database and display them."""
        app = App.get_running_app()

        # Clear existing recordings list
        self.recordings_layout.clear_widgets()

        try:
            # Get recordings based on search term or get all
            if search_term:
                recordings = app.database.search_recordings(search_term)
            else:
                recordings = app.database.get_all_recordings()

            if not recordings:
                # Show message when no recordings found
                no_recordings = Label(
                    text="No recordings found" if search_term else "No recordings yet. Import some!",
                    size_hint_y=None,
                    height=dp(50)
                )
                self.recordings_layout.add_widget(no_recordings)
                return

            # Add each recording to the list
            for recording in recordings:
                recording_id, title, description, filepath, duration, date_created, cover_art = recording

                # Create a layout for each recording item
                item = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(120),
                    padding=dp(10),
                    spacing=dp(5)
                )

                # Title and duration row
                header_row = BoxLayout(size_hint_y=None, height=dp(30))

                title_label = Label(
                    text=title if title else "Untitled",
                    font_size=dp(18),
                    size_hint_x=0.7,
                    halign='left',
                    valign='middle',
                    text_size=(dp(200), dp(30))
                )
                header_row.add_widget(title_label)

                # Format duration as MM:SS
                duration_text = "??:??"
                if duration:
                    minutes = int(duration) // 60
                    seconds = int(duration) % 60
                    duration_text = f"{minutes:02d}:{seconds:02d}"

                duration_label = Label(
                    text=duration_text,
                    font_size=dp(16),
                    size_hint_x=0.3,
                    halign='right'
                )
                header_row.add_widget(duration_label)

                item.add_widget(header_row)

                # Description (if any)
                if description:
                    desc_label = Label(
                        text=description[:50] + ("..." if len(description) > 50 else ""),
                        font_size=dp(14),
                        size_hint_y=None,
                        height=dp(20),
                        halign='left',
                        text_size=(dp(300), dp(20))
                    )
                    item.add_widget(desc_label)
                else:
                    # Add placeholder for proper spacing
                    desc_label = Label(
                        text="",
                        font_size=dp(14),
                        size_hint_y=None,
                        height=dp(20)
                    )
                    item.add_widget(desc_label)

                # Date created (format nicely)
                try:
                    if date_created:
                        dt = datetime.fromisoformat(date_created)
                        formatted_date = dt.strftime("%b %d, %Y %H:%M")
                    else:
                        formatted_date = "Unknown date"
                except:
                    formatted_date = "Invalid date"

                date_label = Label(
                    text=formatted_date,
                    font_size=dp(12),
                    size_hint_y=None,
                    height=dp(20),
                    halign='left',
                    text_size=(dp(300), dp(20))
                )
                item.add_widget(date_label)

                # Action buttons
                buttons_row = BoxLayout(
                    size_hint_y=None,
                    height=dp(40),
                    spacing=dp(10)
                )

                play_btn = Button(
                    text="Play",
                    background_normal='',
                    background_color=theme.PRIMARY_COLOR,
                    on_release=lambda x, rec_id=recording_id: self.play_recording(rec_id)
                )
                buttons_row.add_widget(play_btn)

                add_to_playlist_btn = Button(
                    text="Add to Playlist",
                    background_normal='',
                    background_color=theme.SUCCESS_COLOR,
                    on_release=lambda x, rec_id=recording_id: self.show_playlist_options(rec_id)
                )
                buttons_row.add_widget(add_to_playlist_btn)

                delete_btn = Button(
                    text="Delete",
                    background_normal='',
                    background_color=theme.ERROR_COLOR,
                    on_release=lambda x, rec_id=recording_id: self.confirm_delete(rec_id)
                )
                buttons_row.add_widget(delete_btn)

                item.add_widget(buttons_row)

                # Add the complete recording item to the layout
                self.recordings_layout.add_widget(item)

        except Exception as e:
            error_label = Label(
                text=f"Error loading recordings: {str(e)}",
                size_hint_y=None,
                height=dp(50)
            )
            self.recordings_layout.add_widget(error_label)
            print(f"Exception in load_recordings: {e}")

    def search_recordings(self, instance=None):
        """Search recordings based on text input."""
        search_term = self.search_input.text.strip()
        self.load_recordings(search_term if search_term else None)

    def play_recording(self, recording_id):
        """Play a specific recording."""
        app = App.get_running_app()
        recording = app.database.get_recording(recording_id)

        if recording:
            # Load the recording into the player
            if app.player.load(recording[3]):  # filepath is at index 3
                # Switch to the playback screen
                app.root.current = 'playback'
                # Access the playback screen and update it with current recording info
                playback_screen = app.root.get_screen('playback')
                playback_screen.update_playback_info(recording)
                # Start playback
                app.player.play()
            else:
                print(f"Failed to load recording: {recording[1]}")
                self.show_error(f"Failed to load audio file: {os.path.basename(recording[3])}")
        else:
            print(f"Recording not found: ID {recording_id}")
            self.show_error("Recording not found")

    def show_playlist_options(self, recording_id):
        """Show a popup to select which playlist to add the recording to."""
        from kivy.uix.popup import Popup
        from kivy.uix.button import Button

        app = App.get_running_app()
        playlists = app.database.get_all_playlists()

        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        popup = Popup(
            title="Add to Playlist",
            content=content,
            size_hint=(0.8, 0.8)
        )

        if not playlists:
            content.add_widget(Label(text="No playlists found. Create one first."))

            create_btn = Button(
                text="Create New Playlist",
                size_hint_y=None,
                height=dp(50),
                on_release=lambda x: self.create_playlist_prompt(popup, recording_id)
            )
            content.add_widget(create_btn)
        else:
            content.add_widget(Label(text="Select a playlist:"))

            # Create a scrollable list for playlists
            scroll = ScrollView(size_hint=(1, None), height=dp(300))
            playlist_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
            playlist_layout.bind(minimum_height=playlist_layout.setter('height'))

            for playlist in playlists:
                btn = Button(
                    text=playlist[1],  # playlist name
                    size_hint_y=None,
                    height=dp(50),
                    on_release=lambda x, p_id=playlist[0]: self.add_to_playlist(recording_id, p_id, popup)
                )
                playlist_layout.add_widget(btn)

            scroll.add_widget(playlist_layout)
            content.add_widget(scroll)

            # Also provide option to create a new playlist
            create_btn = Button(
                text="Create New Playlist",
                size_hint_y=None,
                height=dp(50),
                background_normal='',
                background_color=(0.4, 0.8, 0.4, 1),
                on_release=lambda x: self.create_playlist_prompt(popup, recording_id)
            )
            content.add_widget(create_btn)

        # Add a cancel button
        cancel_btn = Button(
            text="Cancel",
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.8, 0.8, 0.8, 1),
            on_release=lambda x: popup.dismiss()
        )
        content.add_widget(cancel_btn)

        popup.open()

    def create_playlist_prompt(self, previous_popup, recording_id=None):
        """Show a popup to create a new playlist."""
        previous_popup.dismiss()

        from kivy.uix.popup import Popup
        from kivy.uix.textinput import TextInput

        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        name_input = TextInput(
            hint_text="Playlist Name",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(name_input)

        desc_input = TextInput(
            hint_text="Description (optional)",
            multiline=True,
            size_hint_y=None,
            height=dp(100)
        )
        content.add_widget(desc_input)

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        popup = Popup(
            title="Create New Playlist",
            content=content,
            size_hint=(0.8, 0.6)
        )

        cancel_btn = Button(
            text="Cancel",
            on_release=lambda x: popup.dismiss()
        )
        buttons.add_widget(cancel_btn)

        create_btn = Button(
            text="Create",
            background_normal='',
            background_color=(0.2, 0.7, 0.2, 1),
            on_release=lambda x: self.create_playlist(name_input.text, desc_input.text, recording_id, popup)
        )
        buttons.add_widget(create_btn)

        content.add_widget(buttons)

        popup.open()

    def create_playlist(self, name, description, recording_id, popup):
        """Create a new playlist and optionally add a recording to it."""
        if not name.strip():
            return

        app = App.get_running_app()
        playlist_id = app.database.create_playlist(name, description)

        if playlist_id and recording_id is not None:
            app.database.add_recording_to_playlist(playlist_id, recording_id)

        popup.dismiss()

        # Show confirmation
        self.show_message(f"Playlist '{name}' created" +
                          (" and recording added!" if recording_id else "!"))

    def add_to_playlist(self, recording_id, playlist_id, popup):
        """Add a recording to the selected playlist."""
        app = App.get_running_app()
        success = app.database.add_recording_to_playlist(playlist_id, recording_id)

        popup.dismiss()

        # Show confirmation
        if success:
            playlist = app.database.get_playlist(playlist_id)
            msg = f"Added to playlist '{playlist[1]}'"
        else:
            msg = "Failed to add to playlist"

        self.show_message(msg)

    def confirm_delete(self, recording_id):
        """Show confirmation dialog before deleting a recording."""
        from kivy.uix.popup import Popup

        app = App.get_running_app()
        recording = app.database.get_recording(recording_id)

        if not recording:
            return

        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        content.add_widget(Label(
            text=f"Are you sure you want to delete '{recording[1]}'?\n\nThis cannot be undone."
        ))

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(20)
        )

        popup = Popup(
            title="Confirm Delete",
            content=content,
            size_hint=(0.8, 0.4)
        )

        cancel_btn = Button(
            text="Cancel",
            on_release=lambda x: popup.dismiss()
        )
        buttons.add_widget(cancel_btn)

        delete_btn = Button(
            text="Delete",
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            on_release=lambda x: self.delete_recording(recording_id, popup)
        )
        buttons.add_widget(delete_btn)

        content.add_widget(buttons)

        popup.open()

    def delete_recording(self, recording_id, popup):
        """Delete a recording and its file."""
        app = App.get_running_app()
        recording = app.database.get_recording(recording_id)

        if recording:
            # Get filepath before deleting from database
            filepath = recording[3]

            # Delete from database
            app.database.delete_recording(recording_id)

            # Delete physical file if it exists
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print(f"Error deleting file: {e}")

        popup.dismiss()

        # Reload the recordings list
        self.load_recordings()

    def go_back(self, instance):
        """Navigate back to the home screen."""
        app = App.get_running_app()
        app.root.current = 'home'

    def go_to_import(self, instance):
        """Navigate to the import screen."""
        app = App.get_running_app()
        app.root.current = 'import'

    def show_message(self, message):
        """Show a simple message popup."""
        from kivy.uix.popup import Popup

        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message))

        popup = Popup(
            title="Message",
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=True
        )

        btn = Button(
            text="OK",
            size_hint_y=None,
            height=dp(50),
            on_release=lambda x: popup.dismiss()
        )
        content.add_widget(btn)

        popup.open()

    def show_error(self, message):
        """Show an error popup."""
        from kivy.uix.popup import Popup

        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message))

        popup = Popup(
            title="Error",
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=True
        )

        btn = Button(
            text="OK",
            size_hint_y=None,
            height=dp(50),
            on_release=lambda x: popup.dismiss()
        )
        content.add_widget(btn)

        popup.open()