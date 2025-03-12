from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime


class PlaylistScreen(Screen):
    """Screen for displaying and managing playlists."""

    def __init__(self, **kwargs):
        super(PlaylistScreen, self).__init__(**kwargs)
        self.playlists_layout = None
        self.current_playlist_id = None
        self.current_playlist_layout = None
        self.is_playlist_detail_view = False

    def on_enter(self):
        """Build the UI when the screen is entered."""
        self.build_ui()

    def build_ui(self):
        """Build the UI for the playlist screen."""
        self.clear_widgets()

        if self.is_playlist_detail_view and self.current_playlist_id is not None:
            self.build_playlist_detail_ui()
        else:
            self.build_playlists_list_ui()

    def build_playlists_list_ui(self):
        """Build the list of all playlists."""
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
            text="Playlists",
            font_size=dp(24)
        )
        header.add_widget(title)

        main_layout.add_widget(header)

        # Create new playlist button
        create_btn = Button(
            text="Create New Playlist",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.2, 0.7, 0.2, 1),
            on_release=self.show_create_playlist_dialog
        )
        main_layout.add_widget(create_btn)

        # Playlists list in a ScrollView
        scroll_view = ScrollView()

        # GridLayout for the list of playlists
        self.playlists_layout = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        # The height will be set dynamically based on children
        self.playlists_layout.bind(minimum_height=self.playlists_layout.setter('height'))

        scroll_view.add_widget(self.playlists_layout)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

        # Load and display playlists
        self.load_playlists()

    def build_playlist_detail_ui(self):
        """Build the detail view for a specific playlist."""
        app = App.get_running_app()
        playlist = app.database.get_playlist(self.current_playlist_id)

        if not playlist:
            # If playlist doesn't exist, go back to list view
            self.is_playlist_detail_view = False
            self.build_playlists_list_ui()
            return

        playlist_id, name, description, date_created = playlist

        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Header with back button and playlist name
        header = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        back_btn = Button(
            text="Back",
            size_hint_x=None,
            width=dp(80),
            on_release=self.back_to_playlists
        )
        header.add_widget(back_btn)

        title = Label(
            text=name,
            font_size=dp(20)
        )
        header.add_widget(title)

        main_layout.add_widget(header)

        # Description
        if description:
            desc_label = Label(
                text=description,
                size_hint_y=None,
                height=dp(40),
                text_size=(dp(400), dp(40)),
                halign='center'
            )
            main_layout.add_widget(desc_label)

        # Playlist control buttons
        controls = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        play_all_btn = Button(
            text="Play All",
            on_release=lambda x: self.play_playlist(playlist_id)
        )
        controls.add_widget(play_all_btn)

        edit_btn = Button(
            text="Edit",
            on_release=lambda x: self.show_edit_playlist_dialog(playlist_id)
        )
        controls.add_widget(edit_btn)

        delete_btn = Button(
            text="Delete",
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            on_release=lambda x: self.confirm_delete_playlist(playlist_id)
        )
        controls.add_widget(delete_btn)

        main_layout.add_widget(controls)

        # Recordings list label
        recordings_label = Label(
            text="Recordings",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40)
        )
        main_layout.add_widget(recordings_label)

        # Recordings list in a ScrollView
        scroll_view = ScrollView()

        # GridLayout for the list of recordings
        self.current_playlist_layout = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        # The height will be set dynamically based on children
        self.current_playlist_layout.bind(minimum_height=self.current_playlist_layout.setter('height'))

        scroll_view.add_widget(self.current_playlist_layout)
        main_layout.add_widget(scroll_view)

        # Add recording button
        add_btn = Button(
            text="Add Recording",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.2, 0.7, 0.2, 1),
            on_release=lambda x: self.show_add_recording_dialog(playlist_id)
        )
        main_layout.add_widget(add_btn)

        self.add_widget(main_layout)

        # Load and display recordings in this playlist
        self.load_playlist_recordings(playlist_id)

    def load_playlists(self):
        """Load playlists from the database and display them."""
        app = App.get_running_app()

        # Clear existing playlists list
        self.playlists_layout.clear_widgets()

        try:
            playlists = app.database.get_all_playlists()

            if not playlists:
                # Show message when no playlists found
                no_playlists = Label(
                    text="No playlists yet. Create one!",
                    size_hint_y=None,
                    height=dp(50)
                )
                self.playlists_layout.add_widget(no_playlists)
                return

            # Add each playlist to the list
            for playlist in playlists:
                playlist_id, name, description, date_created, recording_count = playlist

                # Create a layout for each playlist item
                item = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(100),
                    padding=dp(10),
                    spacing=dp(5)
                )

                # Header row with name and recording count
                header_row = BoxLayout(size_hint_y=None, height=dp(30))

                name_label = Label(
                    text=name,
                    font_size=dp(18),
                    size_hint_x=0.7,
                    halign='left',
                    text_size=(dp(200), dp(30))
                )
                header_row.add_widget(name_label)

                count_label = Label(
                    text=f"{recording_count} items",
                    font_size=dp(16),
                    size_hint_x=0.3,
                    halign='right'
                )
                header_row.add_widget(count_label)

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

                # Action buttons
                buttons_row = BoxLayout(
                    size_hint_y=None,
                    height=dp(40),
                    spacing=dp(10)
                )

                view_btn = Button(
                    text="View",
                    background_normal='',
                    background_color=(0.2, 0.7, 0.9, 1),
                    on_release=lambda x, p_id=playlist_id: self.view_playlist(p_id)
                )
                buttons_row.add_widget(view_btn)

                play_btn = Button(
                    text="Play All",
                    background_normal='',
                    background_color=(0.3, 0.6, 0.9, 1),
                    on_release=lambda x, p_id=playlist_id: self.play_playlist(p_id)
                )
                buttons_row.add_widget(play_btn)

                item.add_widget(buttons_row)

                # Add the complete playlist item to the layout
                self.playlists_layout.add_widget(item)

        except Exception as e:
            error_label = Label(
                text=f"Error loading playlists: {str(e)}",
                size_hint_y=None,
                height=dp(50)
            )
            self.playlists_layout.add_widget(error_label)

    def load_playlist_recordings(self, playlist_id):
        """Load and display recordings in a specific playlist."""
        app = App.get_running_app()

        # Clear existing recordings list
        self.current_playlist_layout.clear_widgets()

        try:
            recordings = app.database.get_playlist_recordings(playlist_id)

            if not recordings:
                # Show message when no recordings found
                no_recordings = Label(
                    text="No recordings in this playlist. Add some!",
                    size_hint_y=None,
                    height=dp(50)
                )
                self.current_playlist_layout.add_widget(no_recordings)
                return

            # Add each recording to the list
            for recording in recordings:
                recording_id, title, description, filepath, duration, date_created, cover_art, position = recording

                # Create a layout for each recording item
                item = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(100),
                    padding=dp(10),
                    spacing=dp(5)
                )

                # Header row with title and duration
                header_row = BoxLayout(size_hint_y=None, height=dp(30))

                pos_label = Label(
                    text=f"{position + 1}.",
                    font_size=dp(16),
                    size_hint_x=0.1
                )
                header_row.add_widget(pos_label)

                title_label = Label(
                    text=title,
                    font_size=dp(16),
                    size_hint_x=0.7,
                    halign='left',
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
                    size_hint_x=0.2,
                    halign='right'
                )
                header_row.add_widget(duration_label)

                item.add_widget(header_row)

                # Action buttons
                buttons_row = BoxLayout(
                    size_hint_y=None,
                    height=dp(40),
                    spacing=dp(10)
                )

                play_btn = Button(
                    text="Play",
                    background_normal='',
                    background_color=(0.2, 0.7, 0.9, 1),
                    on_release=lambda x, rec_id=recording_id: self.play_recording(rec_id)
                )
                buttons_row.add_widget(play_btn)

                remove_btn = Button(
                    text="Remove",
                    background_normal='',
                    background_color=(0.9, 0.3, 0.3, 1),
                    on_release=lambda x, p_id=playlist_id, r_id=recording_id: self.remove_from_playlist(p_id, r_id)
                )
                buttons_row.add_widget(remove_btn)

                item.add_widget(buttons_row)

                # Add the complete recording item to the layout
                self.current_playlist_layout.add_widget(item)

        except Exception as e:
            error_label = Label(
                text=f"Error loading recordings: {str(e)}",
                size_hint_y=None,
                height=dp(50)
            )
            self.current_playlist_layout.add_widget(error_label)

    def view_playlist(self, playlist_id):
        """Switch to the detail view for a specific playlist."""
        self.current_playlist_id = playlist_id
        self.is_playlist_detail_view = True
        self.build_ui()

    def play_playlist(self, playlist_id):
        """Play all recordings in the playlist."""
        app = App.get_running_app()
        recordings = app.database.get_playlist_recordings(playlist_id)

        if not recordings:
            self.show_message("Playlist is empty")
            return

        # Play the first recording
        first_recording = recordings[0]
        self.play_recording(first_recording[0])  # recording_id is at index 0

        # TODO: Queue up the rest of the playlist

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
                self.show_message(f"Failed to load recording: {recording[1]}")
        else:
            self.show_message(f"Recording not found: ID {recording_id}")

    def show_create_playlist_dialog(self, instance=None):
        """Show dialog to create a new playlist."""
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
            on_release=lambda x: self.create_playlist(name_input.text, desc_input.text, popup)
        )
        buttons.add_widget(create_btn)

        content.add_widget(buttons)

        popup.open()

    def create_playlist(self, name, description, popup):
        """Create a new playlist."""
        if not name.strip():
            return

        app = App.get_running_app()
        playlist_id = app.database.create_playlist(name, description)

        popup.dismiss()

        if playlist_id:
            # Refresh the playlists list
            self.load_playlists()

            # Show confirmation
            self.show_message(f"Playlist '{name}' created!")
        else:
            self.show_message("Failed to create playlist")

    def show_edit_playlist_dialog(self, playlist_id):
        """Show dialog to edit an existing playlist."""
        app = App.get_running_app()
        playlist = app.database.get_playlist(playlist_id)

        if not playlist:
            return

        playlist_id, name, description, date_created = playlist

        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        name_input = TextInput(
            text=name,
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(name_input)

        desc_input = TextInput(
            text=description if description else "",
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
            title="Edit Playlist",
            content=content,
            size_hint=(0.8, 0.6)
        )

        cancel_btn = Button(
            text="Cancel",
            on_release=lambda x: popup.dismiss()
        )
        buttons.add_widget(cancel_btn)

        save_btn = Button(
            text="Save",
            background_normal='',
            background_color=(0.2, 0.7, 0.2, 1),
            on_release=lambda x: self.update_playlist(playlist_id, name_input.text, desc_input.text, popup)
        )
        buttons.add_widget(save_btn)

        content.add_widget(buttons)

        popup.open()

    def update_playlist(self, playlist_id, name, description, popup):
        """Update an existing playlist."""
        if not name.strip():
            return

        app = App.get_running_app()
        success = app.database.update_playlist(playlist_id, name, description)

        popup.dismiss()

        if success:
            # Refresh the UI
            self.build_ui()

            # Show confirmation
            self.show_message(f"Playlist updated!")
        else:
            self.show_message("Failed to update playlist")

    def confirm_delete_playlist(self, playlist_id):
        """Show confirmation dialog before deleting a playlist."""
        app = App.get_running_app()
        playlist = app.database.get_playlist(playlist_id)

        if not playlist:
            return

        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        content.add_widget(Label(
            text=f"Are you sure you want to delete playlist '{playlist[1]}'?\n\nThis cannot be undone."
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
            on_release=lambda x: self.delete_playlist(playlist_id, popup)
        )
        buttons.add_widget(delete_btn)

        content.add_widget(buttons)

        popup.open()

    def delete_playlist(self, playlist_id, popup):
        """Delete a playlist."""
        app = App.get_running_app()
        success = app.database.delete_playlist(playlist_id)

        popup.dismiss()

        if success:
            # Go back to playlist list view
            self.is_playlist_detail_view = False
            self.current_playlist_id = None
            self.build_ui()

            # Show confirmation
            self.show_message("Playlist deleted")
        else:
            self.show_message("Failed to delete playlist")

    def show_add_recording_dialog(self, playlist_id):
        """Show dialog to add a recording to the playlist."""
        app = App.get_running_app()
        all_recordings = app.database.get_all_recordings()

        if not all_recordings:
            self.show_message("No recordings available. Import some first!")
            return

        # Get recordings already in the playlist
        playlist_recordings = app.database.get_playlist_recordings(playlist_id)
        existing_ids = [rec[0] for rec in playlist_recordings]  # recording_id is at index 0

        # Filter out recordings already in the playlist
        available_recordings = [rec for rec in all_recordings if rec[0] not in existing_ids]

        if not available_recordings:
            self.show_message("All recordings are already in this playlist!")
            return

        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        content.add_widget(Label(
            text="Select recordings to add:",
            size_hint_y=None,
            height=dp(30)
        ))

        # Scrollable list of recordings
        scroll_view = ScrollView(size_hint_y=None, height=dp(300))
        recordings_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            padding=dp(5),
            size_hint_y=None
        )
        recordings_layout.bind(minimum_height=recordings_layout.setter('height'))

        # Add each recording with a checkbox
        from kivy.uix.checkbox import CheckBox

        selected_recordings = []

        for recording in available_recordings:
            recording_id, title, description, filepath, duration, date_created, cover_art = recording

            # Format duration
            duration_text = "??:??"
            if duration:
                minutes = int(duration) // 60
                seconds = int(duration) % 60
                duration_text = f"{minutes:02d}:{seconds:02d}"

            # Create a row for each recording
            row = BoxLayout(
                size_hint_y=None,
                height=dp(50)
            )

            checkbox = CheckBox(size_hint_x=0.1)
            checkbox.bind(active=lambda cb, value, rec_id=recording_id:
            selected_recordings.append(rec_id) if value else selected_recordings.remove(rec_id))
            row.add_widget(checkbox)

            title_label = Label(
                text=title,
                size_hint_x=0.7,
                halign='left',
                text_size=(dp(200), dp(50))
            )
            row.add_widget(title_label)

            duration_label = Label(
                text=duration_text,
                size_hint_x=0.2
            )
            row.add_widget(duration_label)

            recordings_layout.add_widget(row)

        scroll_view.add_widget(recordings_layout)
        content.add_widget(scroll_view)

        # Buttons
        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        popup = Popup(
            title="Add Recordings to Playlist",
            content=content,
            size_hint=(0.9, 0.8)
        )

        cancel_btn = Button(
            text="Cancel",
            on_release=lambda x: popup.dismiss()
        )
        buttons.add_widget(cancel_btn)

        add_btn = Button(
            text="Add Selected",
            background_normal='',
            background_color=(0.2, 0.7, 0.2, 1),
            on_release=lambda x: self.add_recordings_to_playlist(playlist_id, selected_recordings, popup)
        )
        buttons.add_widget(add_btn)

        content.add_widget(buttons)

        popup.open()

    def add_recordings_to_playlist(self, playlist_id, recording_ids, popup):
        """Add selected recordings to the playlist."""
        if not recording_ids:
            self.show_message("No recordings selected")
            popup.dismiss()
            return

        app = App.get_running_app()
        success_count = 0

        for recording_id in recording_ids:
            if app.database.add_recording_to_playlist(playlist_id, recording_id):
                success_count += 1

        popup.dismiss()

        # Refresh the recordings list
        self.load_playlist_recordings(playlist_id)

        # Show confirmation
        if success_count > 0:
            self.show_message(f"Added {success_count} recording(s) to playlist")
        else:
            self.show_message("Failed to add recordings to playlist")

    def remove_from_playlist(self, playlist_id, recording_id):
        """Remove a recording from the playlist."""
        app = App.get_running_app()
        success = app.database.remove_recording_from_playlist(playlist_id, recording_id)

        if success:
            # Refresh the recordings list
            self.load_playlist_recordings(playlist_id)
            self.show_message("Recording removed from playlist")
        else:
            self.show_message("Failed to remove recording")

    def back_to_playlists(self, instance):
        """Go back to the playlists list view."""
        self.is_playlist_detail_view = False
        self.current_playlist_id = None
        self.build_ui()

    def go_back(self, instance):
        """Navigate back to the home screen."""
        app = App.get_running_app()
        app.root.current = 'home'

    def show_message(self, message):
        """Show a simple message popup."""
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