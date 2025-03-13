from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.app import App
from kivy.core.window import Window
from datetime import datetime
import os
import theme

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView


class FileListScreen(Screen):
    """Screen for displaying and managing all audio recordings."""

    def __init__(self, **kwargs):
        super(FileListScreen, self).__init__(**kwargs)
        self.recordings_list = None
        self.search_input = None
        self.dialog = None

        # Bind to window resize to ensure proper layout
        Window.bind(on_resize=self.on_window_resize)

    def on_window_resize(self, instance, width, height):
        """Handle window resize to ensure layout adapts properly"""
        if hasattr(self, 'main_scroll'):
            # Ensure the scroll view adapts to the new size
            self.main_scroll.size = (width, height)

    def on_enter(self):
        """Build the UI when the screen is entered."""
        self.build_ui()

    def build_ui(self):
        """Build the UI for the file list screen."""
        self.clear_widgets()

        # Use scroll view for better handling of different screen sizes
        self.main_scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        main_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None  # Required for scrolling
        )

        # Set initial height, will be adjusted below
        main_layout.height = dp(800)

        # Header with title and back button
        header = MDBoxLayout(
            size_hint_y=None,
            height=dp(56),
            spacing=dp(8)
        )

        back_btn = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color=theme.TEXT_COLOR,
            icon_size=dp(24),  # Updated to use icon_size
            on_release=self.go_back
        )
        header.add_widget(back_btn)

        title = MDLabel(
            text="All Recordings",
            theme_text_color="Custom",
            text_color=theme.TEXT_COLOR,
            font_style="H5",
            halign="center"
        )
        header.add_widget(title)

        # Add a spacer to balance the header
        spacer = MDIconButton(
            icon="magnify",
            theme_text_color="Custom",
            text_color=theme.TEXT_COLOR,
            icon_size=dp(24),  # Updated to use icon_size
            on_release=self.focus_search
        )
        header.add_widget(spacer)

        main_layout.add_widget(header)

        # Search bar
        search_layout = MDBoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(8),
            padding=[0, dp(8)]
        )

        self.search_input = MDTextField(
            hint_text="Search recordings...",
            mode="rectangle",
            size_hint_x=1,
            on_text_validate=self.search_recordings
        )
        search_layout.add_widget(self.search_input)

        main_layout.add_widget(search_layout)

        # Recordings list in a card
        list_card = MDCard(
            orientation="vertical",
            padding=dp(12),
            elevation=2,
            radius=dp(10),
            size_hint_y=None,
            height=dp(500)  # Set initial height
        )
        list_card.md_bg_color = theme.SURFACE_COLOR

        # Create scrollable list for recordings
        recordings_scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        self.recordings_list = MDList(
            spacing=dp(8),
            padding=[dp(4), dp(4)],
            size_hint_y=None
        )
        self.recordings_list.bind(minimum_height=self.recordings_list.setter('height'))

        recordings_scroll.add_widget(self.recordings_list)
        list_card.add_widget(recordings_scroll)

        main_layout.add_widget(list_card)

        # Add button for importing audio at the bottom
        import_button = MDRaisedButton(
            text="IMPORT NEW AUDIO",
            font_style="Button",
            pos_hint={"center_x": 0.5},
            md_bg_color=theme.SUCCESS_COLOR,
            text_color=theme.TEXT_COLOR,
            on_release=self.go_to_import,
            size_hint_y=None,
            height=dp(48),
            padding=[dp(16), 0],
            elevation=4
        )
        button_container = MDBoxLayout(
            size_hint_y=None,
            height=dp(70),
            padding=[dp(16), dp(8)]
        )
        button_container.add_widget(import_button)
        main_layout.add_widget(button_container)

        # Calculate total height based on children
        total_height = 0
        for child in main_layout.children:
            if hasattr(child, 'height'):
                total_height += child.height

        # Add padding for spacing
        total_height += dp(100)

        # Set minimum height to ensure scrolling works properly
        main_layout.height = max(total_height, dp(800))

        # Add main layout to scroll view
        self.main_scroll.add_widget(main_layout)

        # Add scroll view to screen
        self.add_widget(self.main_scroll)

        # Load and display recordings
        self.load_recordings()

    def focus_search(self, instance):
        """Focus the search field."""
        if self.search_input:
            self.search_input.focus = True

    def load_recordings(self, search_term=None):
        """Load recordings from the database and display them."""
        app = App.get_running_app()

        # Clear existing recordings list
        self.recordings_list.clear_widgets()

        try:
            # Get recordings based on search term or get all
            if search_term:
                recordings = app.database.search_recordings(search_term)
            else:
                recordings = app.database.get_all_recordings()

            if not recordings:
                empty_card = MDCard(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(100),
                    radius=dp(10),
                    elevation=1,
                    padding=dp(16)
                )
                empty_card.md_bg_color = theme.CARD_COLOR

                empty_label = MDLabel(
                    text="No recordings found" if search_term else "No recordings yet. Import some!",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=theme.TEXT_COLOR
                )
                empty_card.add_widget(empty_label)

                self.recordings_list.add_widget(empty_card)
                return

            # Add each recording to the list
            for recording in recordings:
                recording_id, title, description, filepath, duration, date_created, cover_art = recording

                # Format duration as MM:SS
                duration_text = "??:??"
                if duration:
                    minutes = int(duration) // 60
                    seconds = int(duration) % 60
                    duration_text = f"{minutes:02d}:{seconds:02d}"

                # Create a custom list item for each recording
                recording_card = MDCard(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(130),  # Increased height
                    padding=dp(16),
                    spacing=dp(8),
                    radius=dp(10),
                    elevation=1,
                    ripple_behavior=True
                )
                recording_card.md_bg_color = theme.CARD_COLOR

                # Title and duration row
                header_row = MDBoxLayout(
                    size_hint_y=None,
                    height=dp(30)
                )

                title_label = MDLabel(
                    text=title if title else "Untitled",
                    font_style="H6",
                    theme_text_color="Custom",
                    text_color=theme.TEXT_COLOR,
                    size_hint_x=0.8
                )
                header_row.add_widget(title_label)

                duration_label = MDLabel(
                    text=duration_text,
                    theme_text_color="Custom",
                    text_color=theme.SECONDARY_TEXT_COLOR,
                    size_hint_x=0.2,
                    halign="right"
                )
                header_row.add_widget(duration_label)

                recording_card.add_widget(header_row)

                # Description if available
                if description:
                    desc_label = MDLabel(
                        text=description[:50] + ("..." if len(description) > 50 else ""),
                        theme_text_color="Custom",
                        text_color=theme.SECONDARY_TEXT_COLOR,
                        font_style="Caption",
                        size_hint_y=None,
                        height=dp(20)
                    )
                    recording_card.add_widget(desc_label)

                # Format date nicely
                date_text = "Unknown date"
                try:
                    if date_created:
                        dt = datetime.fromisoformat(date_created)
                        date_text = dt.strftime("%b %d, %Y %H:%M")
                except Exception as e:
                    print(f"Error formatting date: {e}")

                date_label = MDLabel(
                    text=date_text,
                    theme_text_color="Custom",
                    text_color=theme.SECONDARY_TEXT_COLOR,
                    font_style="Caption",
                    size_hint_y=None,
                    height=dp(20)
                )
                recording_card.add_widget(date_label)

                # Action buttons
                buttons_row = MDBoxLayout(
                    size_hint_y=None,
                    height=dp(40),
                    spacing=dp(12)  # Increased spacing
                )

                play_btn = MDIconButton(
                    icon="play",
                    theme_text_color="Custom",
                    text_color=theme.FLAX,  # Use gold color from theme
                    icon_size=dp(24),
                    on_release=lambda x, rec_id=recording_id: self.play_recording(rec_id)
                )
                buttons_row.add_widget(play_btn)

                add_to_playlist_btn = MDIconButton(
                    icon="playlist-plus",
                    theme_text_color="Custom",
                    text_color=theme.SUCCESS_COLOR,
                    icon_size=dp(24),
                    on_release=lambda x, rec_id=recording_id: self.show_playlist_options(rec_id)
                )
                buttons_row.add_widget(add_to_playlist_btn)

                delete_btn = MDIconButton(
                    icon="delete",
                    theme_text_color="Custom",
                    text_color=theme.ERROR_COLOR,
                    icon_size=dp(24),
                    on_release=lambda x, rec_id=recording_id: self.confirm_delete(rec_id)
                )
                buttons_row.add_widget(delete_btn)

                recording_card.add_widget(buttons_row)

                # Make the whole card clickable to play the recording
                recording_card.rec_id = recording_id
                recording_card.bind(on_release=lambda x: self.play_recording(x.rec_id))

                # Add the card to the list
                self.recordings_list.add_widget(recording_card)

        except Exception as e:
            error_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(100),
                radius=dp(10),
                elevation=1,
                padding=dp(16)
            )
            error_card.md_bg_color = theme.CARD_COLOR

            error_label = MDLabel(
                text=f"Error loading recordings: {str(e)}",
                theme_text_color="Custom",
                text_color=theme.ERROR_COLOR,
                halign="center"
            )
            error_card.add_widget(error_label)

            self.recordings_list.add_widget(error_card)
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
                app.root_layout.current = 'playback'
                # Access the playback screen and update it with current recording info
                playback_screen = app.root_layout.get_screen('playback')

                # Set the source screen to 'file_list' so back button works properly
                playback_screen.source_screen = 'file_list'

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
        """Show a dialog to select which playlist to add the recording to."""
        app = App.get_running_app()
        playlists = app.database.get_all_playlists()

        if not playlists:
            self.dialog = MDDialog(
                title="No Playlists Available",
                text="You don't have any playlists yet. Create one first.",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=theme.PRIMARY_COLOR,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="CREATE PLAYLIST",
                        theme_text_color="Custom",
                        text_color=theme.TEXT_COLOR,
                        md_bg_color=theme.SUCCESS_COLOR,
                        on_release=lambda x: self.create_playlist_prompt(recording_id)
                    ),
                ],
            )
        else:
            items = []
            for playlist in playlists:
                items.append(f"{playlist[1]}")  # playlist name at index 1

            # Simple dialog with text for now
            playlists_text = "\n".join([f"• {name}" for name in items])

            self.dialog = MDDialog(
                title="Add to Playlist",
                text=f"Select a playlist to add the recording to:\n\n{playlists_text}\n\nNote: Selection from list will be added in the next update.",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=theme.PRIMARY_COLOR,
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="CREATE NEW",
                        theme_text_color="Custom",
                        text_color=theme.TEXT_COLOR,
                        md_bg_color=theme.SUCCESS_COLOR,
                        on_release=lambda x: self.create_playlist_prompt(recording_id)
                    ),
                ],
            )

        self.dialog.open()

    def create_playlist_prompt(self, recording_id=None):
        """Show a dialog to create a new playlist."""
        if self.dialog:
            self.dialog.dismiss()

        content_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(200),
            padding=[dp(24), dp(8), dp(24), dp(16)]
        )

        title_input = MDTextField(
            hint_text="Playlist Name",
            required=True,
            helper_text="Enter a name for your playlist",
            helper_text_mode="on_focus"
        )
        content_box.add_widget(title_input)

        description_input = MDTextField(
            hint_text="Description (optional)",
            multiline=True,
            helper_text="Enter an optional description",
            helper_text_mode="on_focus"
        )
        content_box.add_widget(description_input)

        self.dialog = MDDialog(
            title="Create New Playlist",
            type="custom",
            content_cls=content_box,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=theme.PRIMARY_COLOR,
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="CREATE",
                    theme_text_color="Custom",
                    text_color=theme.TEXT_COLOR,
                    md_bg_color=theme.SUCCESS_COLOR,
                    on_release=lambda x: self.create_playlist(
                        title_input.text,
                        description_input.text,
                        recording_id
                    )
                ),
            ],
        )
        self.dialog.open()

    def create_playlist(self, name, description, recording_id):
        """Create a new playlist and optionally add a recording to it."""
        if not name.strip():
            return

        app = App.get_running_app()
        playlist_id = app.database.create_playlist(name, description)

        if playlist_id and recording_id is not None:
            app.database.add_recording_to_playlist(playlist_id, recording_id)

        if self.dialog:
            self.dialog.dismiss()

        # Show confirmation
        self.show_message(f"Playlist '{name}' created" +
                          (" and recording added!" if recording_id else "!"))

    def add_to_playlist(self, recording_id, playlist_id):
        """Add a recording to the selected playlist."""
        app = App.get_running_app()
        success = app.database.add_recording_to_playlist(playlist_id, recording_id)

        if self.dialog:
            self.dialog.dismiss()

        # Show confirmation
        if success:
            playlist = app.database.get_playlist(playlist_id)
            msg = f"Added to playlist '{playlist[1]}'"
        else:
            msg = "Failed to add to playlist"

        self.show_message(msg)

    def confirm_delete(self, recording_id):
        """Show confirmation dialog before deleting a recording."""
        app = App.get_running_app()
        recording = app.database.get_recording(recording_id)

        if not recording:
            return

        self.dialog = MDDialog(
            title="Confirm Delete",
            text=f"Are you sure you want to delete '{recording[1]}'?\n\nThis cannot be undone.",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=theme.PRIMARY_COLOR,
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="DELETE",
                    theme_text_color="Custom",
                    text_color=theme.TEXT_COLOR,
                    md_bg_color=theme.ERROR_COLOR,
                    on_release=lambda x: self.delete_recording(recording_id)
                ),
            ],
        )
        self.dialog.open()

    def delete_recording(self, recording_id):
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

        if self.dialog:
            self.dialog.dismiss()

        # Reload the recordings list
        self.load_recordings()

    def go_back(self, instance):
        """Navigate back to the home screen."""
        app = App.get_running_app()
        app.root_layout.current = 'home'

    def go_to_import(self, instance):
        """Navigate to the import screen."""
        app = App.get_running_app()
        app.root_layout.current = 'import'

    def show_message(self, message):
        """Show a simple message dialog."""
        self.dialog = MDDialog(
            title="Message",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=theme.PRIMARY_COLOR,
                    on_release=lambda x: self.dialog.dismiss()
                ),
            ],
        )
        self.dialog.open()

    def show_error(self, message):
        """Show an error dialog."""
        self.dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=theme.ERROR_COLOR,
                    on_release=lambda x: self.dialog.dismiss()
                ),
            ],
        )
        self.dialog.open()
