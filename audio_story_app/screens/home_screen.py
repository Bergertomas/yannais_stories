from kivy.uix.screenmanager import Screen
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
from kivymd.uix.dialog import MDDialog


class StoryCard(MDCard):
    """A card widget for displaying a story item"""

    def __init__(self, title, recording_id=None, color=None, **kwargs):
        super(StoryCard, self).__init__(**kwargs)
        self.recording_id = recording_id
        self.md_bg_color = color or theme.NAV_BLUE
        self.radius = [dp(15)]
        self.elevation = 4
        self.padding = dp(12)
        self.orientation = "vertical"
        self.size_hint = (1, None)
        self.height = dp(120)  # Fixed height
        self.ripple_behavior = True

        # Title label
        self.title_label = MDLabel(
            text=title if title else "Untitled",
            font_style="H6",
            halign="center",
            valign="center",
            size_hint_y=0.6,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        self.add_widget(self.title_label)

        # Play button
        play_btn = MDIconButton(
            icon="play-circle-outline",
            pos_hint={"center_x": 0.5},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            icon_size=dp(36)
        )
        self.add_widget(play_btn)

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
        print("HomeScreen initialized")

    def on_enter(self):
        """Called when the screen is entered - refresh content."""
        print("HomeScreen entered")
        self.build_ui()

    def build_ui(self):
        """Build the UI for the home screen with strict vertical spacing."""
        self.clear_widgets()

        # Main container with fixed vertical layout
        main_container = MDBoxLayout(
            orientation='vertical',
            padding=0,
            spacing=0,
            md_bg_color=theme.BACKGROUND_COLOR  # Ensure background is set
        )

        # Create a scroll view for the content
        scroll_view = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(4),
            bar_color=theme.FLAX,
            effect_cls="ScrollEffect"
        )

        # Create main content that will be scrollable
        content_layout = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(40),  # Large spacing between major sections
            size_hint_y=None
        )
        # Bind height to ensure proper scrolling
        content_layout.bind(minimum_height=content_layout.setter('height'))

        # ========== HEADER SECTION ==========
        header_section = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=[0, dp(8)]
        )

        app_title = MDLabel(
            text="Yannai's DreamTales",
            font_style="H4",
            halign="center",
            theme_text_color="Custom",
            text_color=theme.FLAX,
            size_hint_y=None,
            height=dp(60)
        )
        header_section.add_widget(app_title)

        subtitle = MDLabel(
            text="Bedtime tales to whisk you away to dreamland",
            font_style="Body1",
            halign="center",
            theme_text_color="Custom",
            text_color=theme.DUTCH_WHITE,
            size_hint_y=None,
            height=dp(40)
        )
        header_section.add_widget(subtitle)

        content_layout.add_widget(header_section)

        # ========== RECENT STORIES SECTION ==========
        stories_section = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(16)
        )
        stories_section.bind(minimum_height=stories_section.setter('height'))

        stories_title = MDLabel(
            text="Recent Stories",
            font_style="H5",
            halign="center",
            theme_text_color="Custom",
            text_color=theme.ALABASTER,
            size_hint_y=None,
            height=dp(40)
        )
        stories_section.add_widget(stories_title)

        # Container for story cards
        self.stories_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(24),  # Increased spacing between cards
            size_hint_y=None
        )
        self.stories_container.bind(minimum_height=self.stories_container.setter('height'))
        stories_section.add_widget(self.stories_container)

        content_layout.add_widget(stories_section)

        # ========== VIEW ALL BUTTON SECTION ==========
        view_all_section = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(70),
            padding=[dp(20), dp(10)]
        )

        view_all_btn = MDRaisedButton(
            text="VIEW ALL RECORDINGS",
            font_style="Button",
            elevation=2,
            md_bg_color=theme.PRIMARY_COLOR,
            text_color=theme.TEXT_COLOR,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
            on_release=lambda x: self.navigate_to('file_list')
        )
        view_all_section.add_widget(view_all_btn)

        content_layout.add_widget(view_all_section)

        # ========== QUICK NAVIGATION SECTION ==========
        nav_section = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(16)
        )
        nav_section.bind(minimum_height=nav_section.setter('height'))

        nav_title = MDLabel(
            text="Quick Navigation",
            font_style="H5",
            halign="center",
            theme_text_color="Custom",
            text_color=theme.DUTCH_WHITE,
            size_hint_y=None,
            height=dp(50)  # Increased height
        )
        nav_section.add_widget(nav_title)

        # Navigation grid - 2x2 grid
        self.nav_grid = MDGridLayout(
            cols=2,
            spacing=dp(20),  # Increased spacing between items
            size_hint_y=None,
            height=dp(260),  # Fixed height for the grid
            padding=[0, dp(10)]
        )
        nav_section.add_widget(self.nav_grid)

        content_layout.add_widget(nav_section)

        # ========== BOTTOM SPACING FOR MINI PLAYER ==========
        bottom_space = MDBoxLayout(
            size_hint_y=None,
            height=dp(80)  # Space for mini player
        )
        content_layout.add_widget(bottom_space)

        # Add the content layout to the scroll view
        scroll_view.add_widget(content_layout)

        # Add the scroll view to the main container
        main_container.add_widget(scroll_view)

        # Add the main container to the screen
        self.add_widget(main_container)

        # Load navigation cards and recordings
        self.populate_navigation_grid()
        self.load_recent_stories()

    def populate_navigation_grid(self):
        """Add navigation cards to the grid."""
        # Clear existing widgets
        self.nav_grid.clear_widgets()

        nav_items = [
            {
                "text": "Playlists",
                "icon": "playlist-music",
                "color": theme.NAV_GOLD,
                "screen": "playlist"
            },
            {
                "text": "Import Audio",
                "icon": "file-upload",
                "color": theme.NAV_GREEN,
                "screen": "import"
            },
            {
                "text": "Settings",
                "icon": "cog",
                "color": theme.NAV_PURPLE,
                "screen": "settings"
            },
            {
                "text": "Help",
                "icon": "help-circle",
                "color": theme.CHARCOAL,
                "screen": "home",
                "action": self.show_help
            }
        ]

        for item in nav_items:
            card = MDCard(
                orientation="horizontal",
                size_hint=(1, None),
                height=dp(100),  # Taller cards
                radius=[dp(12)],
                elevation=3,
                ripple_behavior=True,
                padding=dp(12),
                md_bg_color=item["color"]
            )

            # Icon
            icon = MDIconButton(
                icon=item["icon"],
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                icon_size=dp(32),
                size_hint_x=0.3
            )
            card.add_widget(icon)

            # Text
            label = MDLabel(
                text=item["text"],
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                size_hint_x=0.7,
                halign="left",
                valign="center"
            )
            card.add_widget(label)

            # Store screen name or action function
            if "action" in item:
                card.bind(on_release=lambda x, action=item["action"]: action())
            else:
                card.bind(on_release=lambda x, screen=item["screen"]: self.navigate_to(screen))

            self.nav_grid.add_widget(card)

    def load_recent_stories(self):
        """Load and display recent stories."""
        # Clear existing stories
        self.stories_container.clear_widgets()

        # Get app instance
        app = App.get_running_app()

        if not hasattr(app, 'database') or not app.database:
            self.add_placeholder_card("Database not available")
            return

        # Try to get recent recordings
        try:
            recent_recordings = self.get_recent_recordings(app.database, limit=2)

            if recent_recordings:
                for i, recording in enumerate(recent_recordings):
                    recording_id, title, description, filepath, duration, date_created, cover_art = recording

                    # Use alternating colors
                    colors = [theme.NAV_BLUE, theme.ULTRA_VIOLET]
                    color = colors[i % len(colors)]

                    story_card = StoryCard(
                        title=title if title else "Untitled",
                        recording_id=recording_id,
                        color=color
                    )

                    self.stories_container.add_widget(story_card)
            else:
                self.add_placeholder_card("No recordings yet.\nImport some stories to get started!")

        except Exception as e:
            print(f"Error loading recordings: {e}")
            self.add_placeholder_card("Error loading recordings")

    def add_placeholder_card(self, message):
        """Add a placeholder card when no recordings are available."""
        placeholder = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120),
            radius=[dp(15)],
            md_bg_color=theme.PRUSSIAN_BLUE_2,
            elevation=2,
            padding=dp(16)
        )

        message_label = MDLabel(
            text=message,
            theme_text_color="Custom",
            text_color=theme.DUTCH_WHITE,
            halign="center",
            valign="center"
        )
        placeholder.add_widget(message_label)

        if "Import" in message or "import" in message:
            import_btn = MDFlatButton(
                text="IMPORT NOW",
                theme_text_color="Custom",
                text_color=theme.FLAX,
                pos_hint={"center_x": 0.5},
                on_release=lambda x: self.navigate_to('import')
            )
            placeholder.add_widget(import_btn)

        self.stories_container.add_widget(placeholder)

    def get_recent_recordings(self, database, limit=2):
        """Get the most recently added recordings."""
        if database:
            try:
                all_recordings = database.get_all_recordings()
                return all_recordings[:limit] if all_recordings else []
            except Exception as e:
                print(f"Error fetching recordings: {e}")
        return []

    def navigate_to(self, screen_name):
        """Navigate to another screen."""
        app = App.get_running_app()
        try:
            if hasattr(app, 'root_layout'):
                app.root_layout.current = screen_name
            else:
                print("root_layout not found")
        except Exception as e:
            print(f"Error navigating: {e}")

    def play_recording(self, recording_id):
        """Play a specific recording."""
        app = App.get_running_app()
        try:
            recording = app.database.get_recording(recording_id)

            if recording and app.player:
                if app.player.load(recording[3]):  # filepath at index 3
                    # Navigate to playback screen
                    app.root_layout.current = 'playback'

                    # Configure playback screen
                    playback_screen = app.root_layout.get_screen('playback')
                    if playback_screen:
                        playback_screen.source_screen = 'home'
                        playback_screen.update_playback_info(recording)

                        # Start playback with slight delay
                        Clock.schedule_once(lambda dt: app.player.play(), 0.1)
        except Exception as e:
            print(f"Error playing recording: {e}")
            self.show_error_dialog("Error playing recording")

    def show_error_dialog(self, message):
        """Show an error dialog."""
        dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=theme.PRIMARY_COLOR,
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()

    def show_help(self):
        """Show a help dialog with usage instructions."""
        dialog = MDDialog(
            title="How to Use",
            text=(
                "Yannai's DreamTales - Audio Story Player\n\n"
                "• Import audio files from the Import screen\n"
                "• Organize stories into playlists\n"
                "• Tap on a story to play it\n"
                "• Use the playback controls to play, pause, and skip\n"
                "• Adjust volume and other settings from the Settings screen\n\n"
                "Enjoy your bedtime stories!"
            ),
            buttons=[
                MDFlatButton(
                    text="CLOSE",
                    theme_text_color="Custom",
                    text_color=theme.PRIMARY_COLOR,
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()
