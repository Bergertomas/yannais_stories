from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
import os
import random
import theme

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView


class StoryCard(MDCard):
    """A card widget for displaying a story item"""

    def __init__(self, title, recording_id=None, color=None, **kwargs):
        super(StoryCard, self).__init__(**kwargs)
        self.recording_id = recording_id
        self.md_bg_color = color or theme.NAV_BLUE
        self.radius = dp(15)
        self.elevation = 4  # Add shadow
        self.padding = dp(12)  # Increased padding
        self.orientation = "vertical"
        self.size_hint = (1, None)
        self.height = dp(120)

        # Title label
        self.title_label = MDLabel(
            text=title if title else "Untitled",
            font_style="H6",
            halign="center",
            valign="center",
            size_hint_y=0.6,  # Slightly reduced to make room
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        self.add_widget(self.title_label)

        # Play button
        self.play_btn = MDIconButton(
            icon="play-circle-outline",
            pos_hint={"center_x": 0.5},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            icon_size=dp(36)  # Use icon_size instead of user_font_size
        )
        self.add_widget(self.play_btn)

        self.bind(on_release=self.on_card_press)

    def on_card_press(self, *args):
        app = App.get_running_app()
        if hasattr(app, 'root_layout') and self.recording_id:
            # Get the home screen
            home_screen = app.root_layout.get_screen('home')
            if home_screen:
                # Call the play_recording method
                home_screen.play_recording(self.recording_id)


class HomeScreen(Screen):
    """Main home screen for the app."""

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.story_grid = None
        self.nav_grid = None
        print("HomeScreen initialized")

        # Bind to window resize to ensure proper layout
        Window.bind(on_resize=self.on_window_resize)

    def on_window_resize(self, instance, width, height):
        """Handle window resize to ensure layout adapts properly"""
        if hasattr(self, 'main_scroll'):
            # Ensure the scroll view adapts to the new size
            self.main_scroll.size = (width, height)

    def on_enter(self):
        """Called when the screen is entered - refresh content."""
        print("HomeScreen entered")
        self.build_ui()

    def build_ui(self):
        """Build the UI for the home screen."""
        self.clear_widgets()

        # Main scroll view to handle different screen sizes
        self.main_scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        # Main content layout inside scroll view
        main_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None,  # Required for scrolling
            height=dp(800)  # Will be adjusted below
        )

        # App title section
        title_section = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            padding=[0, dp(8)]
        )

        app_title = MDLabel(
            text="DreamTales",
            font_style="H4",
            halign="center",
            theme_text_color="Custom",
            text_color=theme.FLAX  # Use gold color for app title
        )
        title_section.add_widget(app_title)

        subtitle = MDLabel(
            text="Bedtime tales to whisk you away to dreamland",
            font_style="Body1",
            halign="center",
            theme_text_color="Custom",
            text_color=theme.DUTCH_WHITE
        )
        title_section.add_widget(subtitle)

        main_layout.add_widget(title_section)

        # "Choose Your Story" section - only if we have recordings
        story_section_title = MDLabel(
            text="Choose Your Story",
            font_style="H5",
            halign="center",
            theme_text_color="Custom",
            text_color=theme.ALABASTER,
            size_hint_y=None,
            height=dp(40)
        )
        main_layout.add_widget(story_section_title)

        # Story grid
        self.story_grid = MDGridLayout(
            cols=2,
            spacing=dp(16),
            size_hint_y=None,
            height=dp(260),
            padding=[0, dp(8)]
        )
        main_layout.add_widget(self.story_grid)

        # Navigation section title
        nav_section_title = MDLabel(
            text="Navigate To",
            font_style="H5",
            halign="center",
            theme_text_color="Custom",
            text_color=theme.DUTCH_WHITE,
            size_hint_y=None,
            height=dp(40)
        )
        main_layout.add_widget(nav_section_title)

        # Navigation grid
        self.nav_grid = MDGridLayout(
            cols=2,
            spacing=dp(16),
            size_hint_y=None,
            height=dp(180),
            padding=[0, dp(8)]
        )

        # Add navigation buttons
        nav_buttons = [
            {"text": "All Recordings", "icon": "playlist-music", "color": theme.NAV_BLUE, "screen": "file_list"},
            {"text": "Playlists", "icon": "playlist-star", "color": theme.NAV_GOLD, "screen": "playlist"},
            {"text": "Import Audio", "icon": "file-import", "color": theme.NAV_GREEN, "screen": "import"},
            {"text": "Settings", "icon": "cog", "color": theme.NAV_PURPLE, "screen": "settings"}
        ]

        for btn_data in nav_buttons:
            nav_card = MDCard(
                orientation="horizontal",
                size_hint=(1, 1),
                radius=dp(12),
                elevation=3,
                padding=dp(8)
            )
            nav_card.md_bg_color = btn_data["color"]

            # Icon
            icon = MDIconButton(
                icon=btn_data["icon"],
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                icon_size=dp(24),  # Use icon_size instead of user_font_size
                size_hint_x=0.3
            )
            nav_card.add_widget(icon)

            # Text
            label = MDLabel(
                text=btn_data["text"],
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                size_hint_x=0.7,
                halign="left",
                valign="center"
            )
            nav_card.add_widget(label)

            # Bind to navigation
            nav_card.screen = btn_data["screen"]
            nav_card.bind(on_release=lambda x: self.navigate_to(x.screen))

            self.nav_grid.add_widget(nav_card)

        main_layout.add_widget(self.nav_grid)

        # Bottom spacing
        main_layout.add_widget(MDBoxLayout(size_hint_y=0.1))

        # Calculate total height based on children
        total_height = 0
        for child in main_layout.children:
            if hasattr(child, 'height'):
                total_height += child.height

        # Add padding
        total_height += dp(100)

        # Set minimum height to ensure scrolling works properly
        main_layout.height = max(total_height, dp(800))

        # Add main layout to scroll view
        self.main_scroll.add_widget(main_layout)

        # Add scroll view to screen
        self.add_widget(self.main_scroll)

        # Load recordings after UI is built
        self.update_story_grid()

    def update_story_grid(self):
        """Update the story grid with recent recordings."""
        try:
            # Clear existing children
            self.story_grid.clear_widgets()
            print("Cleared story grid")

            # Get recent recordings
            app = App.get_running_app()
            recent_recordings = self.get_recent_recordings(app.database, limit=3)
            print(f"Found {len(recent_recordings) if recent_recordings else 0} recent recordings")

            # Add recordings as cards
            if recent_recordings:
                for recording in recent_recordings:
                    # Make sure we're getting the actual data, not the object's attributes
                    try:
                        recording_id, title, description, filepath, duration, date_created, cover_art = recording

                        # Create a color for the card
                        hue = random.random() * 0.1 + 0.1  # Bluer hues in the theme range
                        card_color = theme.PRUSSIAN_BLUE_3

                        # Create a card for the recording
                        story_card = StoryCard(
                            title=title if title and isinstance(title, str) else "Untitled Recording",
                            recording_id=recording_id,
                            color=card_color
                        )

                        self.story_grid.add_widget(story_card)
                        print(f"Added recording card: {title}")
                    except Exception as e:
                        print(f"Error displaying recording: {e}")

            # We're not adding "All Recordings" here anymore since it's in the nav section
            # Instead, add placeholder cards if needed
            while len(self.story_grid.children) < 1:
                placeholder_card = MDCard(
                    orientation="vertical",
                    size_hint=(1, 1),
                    radius=dp(15),
                    elevation=2,
                    padding=dp(12)
                )
                placeholder_card.md_bg_color = theme.PRUSSIAN_BLUE_2

                message = MDLabel(
                    text="No recordings yet.\nImport some stories to get started!",
                    halign="center",
                    valign="center",
                    theme_text_color="Custom",
                    text_color=theme.DUTCH_WHITE
                )
                placeholder_card.add_widget(message)

                self.story_grid.add_widget(placeholder_card)

                print("Added placeholder card")

        except Exception as e:
            print(f"Error updating story grid: {e}")

    def get_recent_recordings(self, database, limit=4):
        """Get the most recently added recordings."""
        if database:
            try:
                all_recordings = database.get_all_recordings()
                return all_recordings[:limit] if all_recordings else []
            except Exception as e:
                print(f"Error fetching recent recordings: {e}")
                return []
        return []

    def navigate_to(self, screen_name):
        """Navigate to another screen."""
        app = App.get_running_app()
        print(f"Navigating to: {screen_name}")
        try:
            if hasattr(app, 'root_layout'):
                app.root_layout.current = screen_name
            else:
                print("app.root_layout not found!")
        except Exception as e:
            print(f"Error in navigate_to: {e}")

    def play_recording_by_title(self, title):
        """Find a recording by title and play it."""
        app = App.get_running_app()
        try:
            # Search for the recording by title
            all_recordings = app.database.get_all_recordings()
            for recording in all_recordings:
                if recording[1] == title:  # title is at index 1
                    self.play_recording(recording[0])  # id is at index 0
                    return

            print(f"No recording found with title: {title}")
        except Exception as e:
            print(f"Error finding recording by title: {e}")

    def play_recording(self, recording_id):
        """Play a specific recording."""
        app = App.get_running_app()
        try:
            recording = app.database.get_recording(recording_id)

            if recording:
                # Navigate to the playback screen first
                app.root_layout.current = 'playback'

                # Access the playback screen
                playback_screen = app.root_layout.get_screen('playback')
                if not playback_screen:
                    print("Could not access playback screen")
                    return

                # Set the source screen to 'home' so back button works properly
                playback_screen.source_screen = 'home'

                filepath = recording[3]  # Get filepath from recording tuple

                # First load the file in our player
                success = app.player.load(filepath)
                if success:
                    # Update the playback screen
                    playback_screen.update_playback_info(recording)

                    # Wait a moment for UI to update before playing
                    def start_playback(dt):
                        app.player.play()

                    Clock.schedule_once(start_playback, 0.1)
                else:
                    print(f"Failed to load recording: {recording[1]}")
            else:
                print(f"Recording not found: ID {recording_id}")
        except Exception as e:
            print(f"Error playing recording: {e}")
