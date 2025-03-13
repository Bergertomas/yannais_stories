from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
import os
import shutil
import theme

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.toast import toast


class ImportScreen(Screen):
    """Screen for importing audio files into the app."""

    def __init__(self, **kwargs):
        super(ImportScreen, self).__init__(**kwargs)
        self.selected_file = None
        self.file_manager = None
        self.dialog = None
        self.title_input = None
        self.desc_input = None

        # Build UI during initialization
        self.build_ui()

    def build_ui(self):
        """Build the UI for the import screen using KivyMD components."""
        main_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(16),
            md_bg_color=theme.BACKGROUND_COLOR
        )

        # Header with back button and title
        header = MDBoxLayout(
            size_hint_y=None,
            height=dp(56),
            spacing=dp(8),
            padding=[0, dp(8)]
        )

        # Back button
        back_btn = MDRaisedButton(
            text="Back",
            on_release=self.go_back,
            md_bg_color=theme.PRIMARY_COLOR,
            text_color=theme.TEXT_COLOR
        )
        header.add_widget(back_btn)

        # Title
        title = MDLabel(
            text="Import Audio",
            font_style="H5",
            halign="center",
            theme_text_color="Custom",
            text_color=theme.TEXT_COLOR
        )
        header.add_widget(title)

        # Add a spacer widget for balance
        spacer = MDBoxLayout(size_hint_x=None, width=back_btn.width)
        header.add_widget(spacer)

        main_layout.add_widget(header)

        # Card for import instructions
        instruction_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(100),
            padding=dp(16),
            radius=dp(10),
            elevation=2
        )
        instruction_card.md_bg_color = theme.SURFACE_COLOR

        instructions = MDLabel(
            text="Select an audio file to import.\nSupported formats: MP3, WAV, OGG",
            theme_text_color="Custom",
            text_color=theme.TEXT_COLOR,
            halign="center"
        )
        instruction_card.add_widget(instructions)

        main_layout.add_widget(instruction_card)

        # Card for selected file info
        file_info_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            padding=dp(16),
            radius=dp(10),
            elevation=2
        )
        file_info_card.md_bg_color = theme.SURFACE_COLOR

        self.selected_file_label = MDLabel(
            text="No file selected",
            theme_text_color="Custom",
            text_color=theme.TEXT_COLOR,
            halign="center"
        )
        file_info_card.add_widget(self.selected_file_label)

        main_layout.add_widget(file_info_card)

        # Card for metadata input
        metadata_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),
            padding=dp(16),
            spacing=dp(16),
            radius=dp(10),
            elevation=2
        )
        metadata_card.md_bg_color = theme.SURFACE_COLOR

        # Title input
        self.title_input = MDTextField(
            hint_text="Enter a title for this recording",
            mode="rectangle",
            helper_text="Required",
            helper_text_mode="on_error"
        )
        metadata_card.add_widget(self.title_input)

        # Description input
        self.desc_input = MDTextField(
            hint_text="Enter an optional description",
            mode="rectangle",
            multiline=True
        )
        metadata_card.add_widget(self.desc_input)

        main_layout.add_widget(metadata_card)

        # Browse button
        browse_btn = MDRaisedButton(
            text="Browse for Audio File",
            on_release=self.show_file_manager,
            md_bg_color=theme.PRIMARY_COLOR,
            text_color=theme.TEXT_COLOR,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8
        )
        main_layout.add_widget(browse_btn)

        # Import button
        import_btn = MDRaisedButton(
            text="Import File",
            on_release=self.import_file,
            md_bg_color=theme.SUCCESS_COLOR,
            text_color=theme.TEXT_COLOR,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8
        )
        main_layout.add_widget(import_btn)

        # Add a spacer at the bottom
        main_layout.add_widget(MDBoxLayout(size_hint_y=0.1))

        self.add_widget(main_layout)

        # Initialize the file manager
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_path,
            preview=True,
            ext=['.mp3', '.wav', '.ogg', '.m4a']
        )

    def show_file_manager(self, instance):
        """Show the file manager to select an audio file."""
        try:
            # Set the starting path
            start_path = self.get_default_path()
            self.file_manager.show(start_path)
        except Exception as e:
            print(f"Error showing file manager: {e}")
            self.show_error(f"Error opening file browser: {str(e)}")

    def exit_file_manager(self, *args):
        """Close the file manager."""
        self.file_manager.close()

    def select_path(self, path):
        """Handle file selection from the file manager."""
        self.exit_file_manager()

        if os.path.isfile(path):
            self.selected_file = path
            filename = os.path.basename(self.selected_file)
            self.selected_file_label.text = f"Selected: {filename}"

            # Auto-fill title field with filename (without extension)
            name_without_ext = os.path.splitext(filename)[0]
            self.title_input.text = name_without_ext
        else:
            self.show_error("Please select a valid audio file.")

    def get_default_path(self):
        """Get a sensible default path for the file chooser."""
        # Try to use the external storage on Android
        if os.path.exists('/storage/emulated/0'):
            return '/storage/emulated/0'

        # On Android 11+, try to use Music directory
        if os.path.exists('/storage/emulated/0/Music'):
            return '/storage/emulated/0/Music'

        # Try to use the Downloads directory
        if os.path.exists('/storage/emulated/0/Download'):
            return '/storage/emulated/0/Download'

        # Fall back to the app's directory
        return os.path.dirname(os.path.abspath(__file__))

    def import_file(self, instance):
        """Import the selected file into the app."""
        if not self.selected_file:
            self.show_error("Please select a file first.")
            return

        title = self.title_input.text.strip()
        if not title:
            self.show_error("Please enter a title for the recording.")
            return

        description = self.desc_input.text.strip()

        # Get file info
        try:
            # Try to get duration from a sound
            from kivy.core.audio import SoundLoader
            sound = SoundLoader.load(self.selected_file)
            duration = sound.length if sound else 0
            if sound:
                sound.unload()

            # If we couldn't get duration, use a placeholder
            if not duration or duration <= 0:
                print("Could not detect audio duration, using placeholder")
                duration = 0  # Database will handle this

            # Copy the file to the app's data directory
            app = App.get_running_app()

            # Make sure the destination directory exists
            dest_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'recordings')
            try:
                os.makedirs(dest_dir, exist_ok=True)
            except Exception as e:
                print(f"Error creating recordings directory: {e}")
                # Try an alternative path
                dest_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'recordings')
                os.makedirs(dest_dir, exist_ok=True)

            filename = os.path.basename(self.selected_file)
            dest_path = os.path.join(dest_dir, filename)

            # If file with same name exists, append a number
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(dest_dir, f"{base}_{counter}{ext}")
                counter += 1

            # Copy the file
            print(f"Copying file from {self.selected_file} to {dest_path}")
            with open(self.selected_file, 'rb') as src_file:
                with open(dest_path, 'wb') as dest_file:
                    dest_file.write(src_file.read())

            # Add to database
            app.database.add_recording(
                title=title,
                description=description,
                filepath=dest_path,
                duration=duration
            )

            # Show success message
            self.show_success(f"Successfully imported '{title}'")

            # Clear inputs for next import
            self.title_input.text = ""
            self.desc_input.text = ""
            self.selected_file = None
            self.selected_file_label.text = "No file selected"

        except Exception as e:
            self.show_error(f"Error importing file: {str(e)}")
            print(f"Error importing file: {e}")

    def show_error(self, message):
        """Show an error dialog."""
        if self.dialog:
            self.dialog.dismiss()

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

    def show_success(self, message):
        """Show a success dialog with options."""
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Success",
            text=message,
            buttons=[
                MDFlatButton(
                    text="IMPORT ANOTHER",
                    theme_text_color="Custom",
                    text_color=theme.PRIMARY_COLOR,
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="GO TO RECORDINGS",
                    theme_text_color="Custom",
                    text_color=theme.TEXT_COLOR,
                    md_bg_color=theme.SUCCESS_COLOR,
                    on_release=lambda x: self.go_to_files(self.dialog)
                ),
            ],
        )
        self.dialog.open()

    def go_to_files(self, dialog):
        """Close the dialog and go to the file list screen."""
        dialog.dismiss()
        app = App.get_running_app()
        app.root_layout.current = 'file_list'

    def go_back(self, instance):
        """Navigate back to the home screen."""
        app = App.get_running_app()
        app.root_layout.current = 'home'
