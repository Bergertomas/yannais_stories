from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.metrics import dp
from kivy.app import App
import os
from kivy.core.audio import SoundLoader


class ImportScreen(Screen):
    """Screen for importing audio files into the app."""

    def __init__(self, **kwargs):
        super(ImportScreen, self).__init__(**kwargs)
        self.selected_file = None
        self.file_chooser = None
        self.build_ui()

    def build_ui(self):
        """Build the UI for the import screen."""
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Header with back button and title
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
            text="Import Audio",
            font_size=dp(24)
        )
        header.add_widget(title)

        main_layout.add_widget(header)

        # Instructions
        instructions = Label(
            text="Select an audio file to import:",
            size_hint_y=None,
            height=dp(40),
            halign='left'
        )
        instructions.bind(size=instructions.setter('text_size'))
        main_layout.add_widget(instructions)

        # File chooser
        self.file_chooser = FileChooserListView(
            path=self.get_default_path(),
            filters=['*.mp3', '*.wav', '*.ogg', '*.m4a']
        )
        self.file_chooser.bind(selection=self.on_file_selected)
        main_layout.add_widget(self.file_chooser)

        # Selected file info
        self.selected_file_label = Label(
            text="No file selected",
            size_hint_y=None,
            height=dp(40)
        )
        main_layout.add_widget(self.selected_file_label)

        # Metadata input section
        metadata_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(180),
            spacing=dp(10),
            padding=[0, dp(10)]
        )

        # Title input
        title_layout = BoxLayout(
            size_hint_y=None,
            height=dp(50)
        )
        title_layout.add_widget(Label(
            text="Title:",
            size_hint_x=0.3
        ))
        self.title_input = TextInput(
            hint_text="Enter a title for this recording",
            multiline=False
        )
        title_layout.add_widget(self.title_input)
        metadata_layout.add_widget(title_layout)

        # Description input
        desc_layout = BoxLayout(
            size_hint_y=None,
            height=dp(100)
        )
        desc_layout.add_widget(Label(
            text="Description:",
            size_hint_x=0.3,
            valign='top'
        ))
        self.desc_input = TextInput(
            hint_text="Enter an optional description",
            multiline=True
        )
        desc_layout.add_widget(self.desc_input)
        metadata_layout.add_widget(desc_layout)

        main_layout.add_widget(metadata_layout)

        # Import button
        import_btn = Button(
            text="Import File",
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.2, 0.7, 0.2, 1),
            on_release=self.import_file
        )
        main_layout.add_widget(import_btn)

        self.add_widget(main_layout)

    def get_default_path(self):
        """Get a sensible default path for the file chooser."""
        # Try to use the external storage on Android
        if os.path.exists('/storage/emulated/0'):
            return '/storage/emulated/0'

        # Fall back to the app's directory
        return os.path.dirname(os.path.abspath(__file__))

    def on_file_selected(self, instance, selection):
        """Handle file selection."""
        if selection:
            self.selected_file = selection[0]
            filename = os.path.basename(self.selected_file)
            self.selected_file_label.text = f"Selected: {filename}"

            # Auto-fill title field with filename (without extension)
            name_without_ext = os.path.splitext(filename)[0]
            self.title_input.text = name_without_ext
        else:
            self.selected_file = None
            self.selected_file_label.text = "No file selected"

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
            # Load the sound to get its duration
            sound = SoundLoader.load(self.selected_file)
            duration = sound.length if sound else 0
            if sound:
                sound.unload()

            # Copy the file to the app's data directory
            app = App.get_running_app()
            dest_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'recordings')
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
            self.file_chooser.selection = []

        except Exception as e:
            self.show_error(f"Error importing file: {str(e)}")

    def show_error(self, message):
        """Show an error popup."""
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
            title="Error",
            content=content,
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def show_success(self, message):
        """Show a success popup."""
        from kivy.uix.popup import Popup

        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message))

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        popup = Popup(
            title="Success",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )

        import_another_btn = Button(
            text="Import Another",
            on_release=lambda x: popup.dismiss()
        )
        buttons.add_widget(import_another_btn)

        go_to_files_btn = Button(
            text="Go to Recordings",
            on_release=lambda x: self.go_to_files(popup)
        )
        buttons.add_widget(go_to_files_btn)

        content.add_widget(buttons)

        popup.open()

    def go_to_files(self, popup):
        """Close the popup and go to the file list screen."""
        popup.dismiss()
        app = App.get_running_app()
        app.root.current = 'file_list'

    def go_back(self, instance):
        """Navigate back to the previous screen."""
        app = App.get_running_app()
        app.root.current = 'home'
