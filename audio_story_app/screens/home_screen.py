# from kivy.uix.screenmanager import Screen
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.gridlayout import GridLayout
# from kivy.uix.button import Button
# from kivy.uix.label import Label
# from kivy.metrics import dp
# from kivy.graphics import Color, RoundedRectangle, Line, Ellipse, Rectangle, Scale, Translate
# from kivy.app import App
# from kivy.clock import Clock
# import random
# from miscel.audio_story_app import theme
# from miscel.audio_story_app.button_icons import IconButton
# from kivy.uix.widget import Widget  # Add this import
# from kivy.lang import Builder
#
#
# # Load the kv file
# try:
#     Builder.load_file('kv_files/home_screen.kv')
# except Exception as e:
#     print(f"Error loading home_screen.kv: {e}")
#
#
# class StoryCard(BoxLayout):
#     """A story card widget representing a recording with an image."""
#
#     def __init__(self, title, image_color, recording_id=None, **kwargs):
#         super(StoryCard, self).__init__(**kwargs)
#         self.orientation = 'vertical'
#         self.size_hint_y = None
#         self.height = dp(160)
#         self.padding = dp(5)
#         self.spacing = dp(5)
#         self.recording_id = recording_id
#
#         # Create background with rounded corners
#         with self.canvas.before:
#             Color(rgba=image_color)
#             self.background = RoundedRectangle(
#                 pos=self.pos,
#                 size=self.size,
#                 radius=[dp(15)] * 4
#             )
#
#         # Bind to update positions when layout changes
#         self.bind(pos=self.update_rect, size=self.update_rect)
#
#         # Add star effects to the card background
#         self.create_star_effects()
#
#         # Create the image area (just a decorated space for now)
#         self.image_area = BoxLayout(
#             size_hint=(1, 0.7)
#         )
#
#         # Use a themed image for each story type
#         if 'night' in title.lower() or 'owl' in title.lower():
#             self.create_owl_image()
#         elif 'dragon' in title.lower():
#             self.create_dragon_image()
#         elif 'cloud' in title.lower() or 'rider' in title.lower():
#             self.create_cloud_rider_image()
#         elif 'fairy' in title.lower() or 'garden' in title.lower():
#             self.create_fairy_garden_image()
#         else:
#             # Default image - a moon with stars
#             self.create_default_image()
#
#         self.add_widget(self.image_area)
#
#         # Button with title
#         self.button = Button(
#             text=title,
#             size_hint=(1, 0.3),
#             background_normal='',
#             background_color=theme.BUTTON_COLOR,
#             color=theme.TEXT_COLOR,
#             font_size=dp(16),
#             bold=True
#         )
#
#         # Make button corners rounded
#         with self.button.canvas.before:
#             Color(rgba=theme.BUTTON_COLOR)
#             self.button_bg = RoundedRectangle(
#                 pos=self.button.pos,
#                 size=self.button.size,
#                 radius=[dp(10)] * 4
#             )
#
#         self.button.bind(pos=self.update_button_bg, size=self.update_button_bg)
#         self.button.bind(on_release=self.play_recording)
#
#         self.add_widget(self.button)
#
#     def create_star_effects(self):
#         """Add star decorations to the card."""
#         with self.canvas.after:
#             # Add some random decorative stars
#             for _ in range(10):
#                 x = random.random() * self.width * 0.9 + self.x
#                 y = random.random() * self.height * 0.7 + self.y + self.height * 0.3
#                 size = random.random() * 2 + 1
#                 alpha = random.random() * 0.7 + 0.3
#
#                 Color(rgba=(1, 1, 1, alpha))
#                 Ellipse(pos=(x, y), size=(size, size))
#
#     def create_owl_image(self):
#         """Create an owl on a moon image."""
#         with self.image_area.canvas:
#             # Moon circle
#             Color(rgba=(0, 0, 0, 1))  # Black background
#             Ellipse(pos=(self.width / 2 - dp(40), self.height / 2 - dp(30)), size=(dp(80), dp(80)))
#
#             # Small stars
#             for _ in range(6):
#                 x = random.random() * self.width * 0.8 + self.width * 0.1
#                 y = random.random() * self.height * 0.8 + self.height * 0.1
#                 size = random.random() * 3 + 1
#                 Color(rgba=theme.STAR_WHITE)
#                 Ellipse(pos=(x, y), size=(size, size))
#
#             # Simple owl silhouette
#             Color(rgba=(0.1, 0.1, 0.1, 1))  # Dark silhouette
#             # Owl body
#             Ellipse(pos=(self.width / 2 - dp(15), self.height / 2 - dp(20)), size=(dp(30), dp(40)))
#             # Owl ears/head
#             triangle_points = [
#                 self.width / 2 - dp(15), self.height / 2 + dp(15),  # Left bottom
#                 self.width / 2, self.height / 2 + dp(30),  # Top
#                 self.width / 2 + dp(15), self.height / 2 + dp(15)  # Right bottom
#             ]
#             Line(points=triangle_points, width=dp(2))
#
#             # Owl eyes
#             Color(rgba=theme.STAR_WHITE)
#             Ellipse(pos=(self.width / 2 - dp(10), self.height / 2 + dp(5)), size=(dp(6), dp(6)))
#             Ellipse(pos=(self.width / 2 + dp(4), self.height / 2 + dp(5)), size=(dp(6), dp(6)))
#
#     def create_dragon_image(self):
#         """Create a dragon on a sunset image."""
#         with self.image_area.canvas:
#             # Sunset background
#             Color(rgba=(0.95, 0.6, 0.1, 1))  # Orange/red sunset
#             Ellipse(pos=(self.width / 2 - dp(30), self.height * 0.2), size=(dp(60), dp(60)))
#
#             # Mountain silhouette
#             Color(rgba=(0.1, 0.1, 0.2, 1))  # Dark blue-black
#             triangle_points = [
#                 self.width * 0.1, self.height * 0.4,  # Left
#                 self.width * 0.9, self.height * 0.4,  # Right
#                 self.width * 0.5, self.height * 0.7  # Top
#             ]
#             Line(points=triangle_points, width=dp(2))
#
#             # Simple dragon silhouette
#             Color(rgba=(0.1, 0.1, 0.1, 1))
#             # Dragon body line
#             body_points = [
#                 self.width * 0.3, self.height * 0.55,
#                 self.width * 0.4, self.height * 0.6,
#                 self.width * 0.5, self.height * 0.55,
#                 self.width * 0.6, self.height * 0.6,
#                 self.width * 0.7, self.height * 0.55
#             ]
#             Line(points=body_points, width=dp(3))
#
#             # Dragon head
#             Ellipse(pos=(self.width * 0.7, self.height * 0.52), size=(dp(15), dp(15)))
#
#             # Dragon wings
#             wing_points = [
#                 self.width * 0.5, self.height * 0.55,  # Body connection
#                 self.width * 0.5, self.height * 0.7,  # Wing tip
#                 self.width * 0.6, self.height * 0.55  # Body connection
#             ]
#             Line(points=wing_points, width=dp(2))
#
#     def create_cloud_rider_image(self):
#         """Create a teddy bear on a cloud image."""
#         with self.image_area.canvas:
#             # Cloud background
#             Color(rgba=(0.2, 0.3, 0.5, 1))  # Dark blue night sky
#
#             # Stars
#             for _ in range(8):
#                 x = random.random() * self.width * 0.8 + self.width * 0.1
#                 y = random.random() * self.height * 0.7 + self.height * 0.15
#                 size = random.random() * 3 + 1
#                 Color(rgba=theme.STAR_WHITE)
#                 Ellipse(pos=(x, y), size=(size, size))
#
#             # Cloud
#             Color(rgba=(0.7, 0.7, 0.8, 0.8))
#             Ellipse(pos=(self.width / 2 - dp(40), self.height / 2 - dp(25)), size=(dp(35), dp(25)))
#             Ellipse(pos=(self.width / 2 - dp(20), self.height / 2 - dp(30)), size=(dp(40), dp(30)))
#             Ellipse(pos=(self.width / 2 + dp(5), self.height / 2 - dp(25)), size=(dp(35), dp(25)))
#
#             # Teddy bear silhouette
#             Color(rgba=(0.35, 0.25, 0.15, 1))  # Brown
#             # Bear body
#             Ellipse(pos=(self.width / 2 - dp(15), self.height / 2 - dp(15)), size=(dp(30), dp(30)))
#             # Bear head
#             Ellipse(pos=(self.width / 2 - dp(10), self.height / 2 + dp(10)), size=(dp(20), dp(20)))
#             # Bear ears
#             Ellipse(pos=(self.width / 2 - dp(12), self.height / 2 + dp(25)), size=(dp(8), dp(8)))
#             Ellipse(pos=(self.width / 2 + dp(4), self.height / 2 + dp(25)), size=(dp(8), dp(8)))
#
#     def create_fairy_garden_image(self):
#         """Create a fairy garden image."""
#         with self.image_area.canvas:
#             # Garden background
#             Color(rgba=(0.1, 0.25, 0.1, 1))  # Dark green
#             RoundedRectangle(pos=(self.width * 0.1, self.height * 0.1),
#                              size=(self.width * 0.8, self.height * 0.7),
#                              radius=[dp(10)])
#
#             # Fairy lights
#             for _ in range(15):
#                 x = random.random() * self.width * 0.7 + self.width * 0.15
#                 y = random.random() * self.height * 0.6 + self.height * 0.15
#                 size = random.random() * 4 + 2
#                 alpha = random.random() * 0.5 + 0.5
#
#                 # Randomize between gold and white
#                 if random.random() > 0.5:
#                     Color(rgba=(1, 0.9, 0.5, alpha))  # Gold
#                 else:
#                     Color(rgba=(1, 1, 1, alpha))  # White
#
#                 Ellipse(pos=(x, y), size=(size, size))
#
#             # Simple flower silhouettes
#             Color(rgba=(0.7, 0.4, 0.8, 0.7))  # Purple
#             for i in range(3):
#                 x = self.width * (0.3 + i * 0.2)
#                 y = self.height * 0.25
#                 # Stem
#                 Line(points=[x, y, x, y + dp(20)], width=dp(1))
#                 # Flower
#                 Ellipse(pos=(x - dp(5), y + dp(20)), size=(dp(10), dp(10)))
#
#     def create_default_image(self):
#         """Create a default starry night image."""
#         with self.image_area.canvas:
#             # Night sky background is already the card background
#
#             # Add a moon
#             Color(rgba=(0.95, 0.95, 0.8, 1))  # Slightly off-white
#             Ellipse(pos=(self.width / 2 - dp(25), self.height / 2 - dp(25)), size=(dp(50), dp(50)))
#
#             # Stars of various sizes
#             for _ in range(12):
#                 x = random.random() * self.width * 0.8 + self.width * 0.1
#                 y = random.random() * self.height * 0.6 + self.height * 0.2
#                 size = random.random() * 3 + 1
#                 alpha = random.random() * 0.7 + 0.3
#
#                 Color(rgba=(1, 1, 1, alpha))
#                 Ellipse(pos=(x, y), size=(size, size))
#
#     def update_rect(self, instance, value):
#         """Update the rectangle position when the layout changes."""
#         if hasattr(self, 'background'):
#             self.background.pos = self.pos
#             self.background.size = self.size
#
#         # Recreate star effects when size changes
#         if hasattr(self, 'canvas'):
#             # Only update star layers, not the entire canvas
#             for instr in self.canvas.after.children[:]:
#                 if isinstance(instr, Ellipse) and instr.size[0] < 5:  # Only remove small stars
#                     self.canvas.after.remove(instr)
#             self.create_star_effects()
#
#     def update_button_bg(self, instance, value):
#         """Update the button background rectangle."""
#         if hasattr(self, 'button_bg'):
#             self.button_bg.pos = instance.pos
#             self.button_bg.size = instance.size
#
#     def play_recording(self, recording_id):
#         """Play a specific recording."""
#         app = App.get_running_app()
#         try:
#             recording = app.database.get_recording(recording_id)
#
#             if recording:
#                 # Navigate to the playback screen first
#                 app.root_layout.current = 'playback'
#
#                 # Access the playback screen
#                 playback_screen = app.root_layout.get_screen('playback')
#                 if not playback_screen:
#                     print("Could not access playback screen")
#                     return
#
#                 filepath = recording[3]  # Get filepath from recording tuple
#
#                 # First load the file in our player
#                 success = app.player.load(filepath)
#                 if success:
#                     # Update the playback screen
#                     playback_screen.update_playback_info(recording)
#
#                     # Wait a moment for UI to update before playing
#                     from kivy.clock import Clock
#                     def start_playback(dt):
#                         app.player.play()
#
#                     Clock.schedule_once(start_playback, 0.1)
#                 else:
#                     print(f"Failed to load recording: {recording[1]}")
#             else:
#                 print(f"Recording not found: ID {recording_id}")
#         except Exception as e:
#             print(f"Error playing recording: {e}")
#
#
# class NavButton(Button):
#     """Custom navigation button with icon and rounded appearance."""
#
#     def __init__(self, icon_type='home', **kwargs):
#         # Init with empty text - we'll use icons instead
#         kwargs['text'] = ''
#         super(NavButton, self).__init__(**kwargs)
#
#         # Create rounded background
#         with self.canvas.before:
#             Color(rgba=theme.NAV_BAR_COLOR)
#             self.bg = RoundedRectangle(
#                 pos=self.pos,
#                 size=self.size,
#                 radius=[dp(15)] * 4
#             )
#
#         # Add the icon
#         self.icon = IconButton(
#             icon_type=icon_type,
#             background_color=(0, 0, 0, 0),  # Transparent
#             size_hint=(1, 1),
#             pos_hint={'center_x': 0.5, 'center_y': 0.5}
#         )
#         self.add_widget(self.icon)
#
#         # Bind to update positions
#         self.bind(pos=self.update_rect, size=self.update_rect)
#
#     def update_rect(self, instance, value):
#         """Update rectangle position when layout changes."""
#         if hasattr(self, 'bg'):
#             self.bg.pos = instance.pos
#             self.bg.size = instance.size
#
#
# class StarsBackground(Widget):
#     """Widget that creates a night sky with stars background."""
#
#     def __init__(self, **kwargs):
#         super(StarsBackground, self).__init__(**kwargs)
#         self.stars = []
#         self.bind(pos=self.update_stars, size=self.update_stars)
#         Clock.schedule_once(self.create_stars, 0)
#         # Animate stars every few seconds
#         Clock.schedule_interval(self.twinkle_stars, 2)
#
#     def create_stars(self, dt):
#         """Create the starry background."""
#         self.canvas.before.clear()
#
#         with self.canvas.before:
#             # Deep navy blue background
#             Color(rgba=theme.BACKGROUND_COLOR)
#             self.bg_rect = Rectangle(pos=self.pos, size=self.size)
#
#             # Create stars of different sizes and brightness
#             self.stars = []
#             for _ in range(50):  # Number of stars
#                 x = random.random() * self.width
#                 y = random.random() * self.height
#                 size = random.random() * 2.5 + 0.5  # Varied sizes
#                 alpha = random.random() * 0.7 + 0.3  # Varied brightness
#
#                 # Randomize between white and gold stars
#                 if random.random() > 0.7:
#                     color = theme.STAR_GOLD
#                 else:
#                     color = theme.STAR_WHITE
#
#                 Color(rgba=(color[0], color[1], color[2], alpha))
#                 star = Ellipse(pos=(x, y), size=(size, size))
#                 self.stars.append((star, color, alpha))
#
#     def update_stars(self, instance, value):
#         """Update stars when widget size changes."""
#         if hasattr(self, 'bg_rect'):
#             self.bg_rect.pos = self.pos
#             self.bg_rect.size = self.size
#
#         # Recreate stars for new size
#         Clock.schedule_once(self.create_stars, 0)
#
#     def twinkle_stars(self, dt):
#         """Animate stars by changing their alpha periodically."""
#         with self.canvas.before:
#             for i, (star, color, alpha) in enumerate(self.stars):
#                 # Randomly adjust brightness
#                 new_alpha = max(0.2, min(1.0, alpha + (random.random() - 0.5) * 0.3))
#                 Color(rgba=(color[0], color[1], color[2], new_alpha))
#
#                 # Update the star with same position but new color
#                 pos = star.pos
#                 size = star.size
#                 self.canvas.before.remove(star)
#                 new_star = Ellipse(pos=pos, size=size)
#                 self.stars[i] = (new_star, color, new_alpha)
#
#
# class HomeScreen(Screen):
#     """Main home screen for the app."""
#
#     def __init__(self, **kwargs):
#         super(HomeScreen, self).__init__(**kwargs)
#         print("HomeScreen initialized")
#
#     def on_enter(self):
#         """Called when the screen is entered - refresh content."""
#         print("HomeScreen entered")
#
#         try:
#             # Make sure we have story_grid in our IDs
#             if hasattr(self, 'ids') and hasattr(self.ids, 'story_grid'):
#                 # Update the story grid with recordings
#                 self.update_story_grid()
#                 print("Story grid updated")
#             else:
#                 print("WARNING: story_grid not found in ids!")
#         except Exception as e:
#             print(f"Error in HomeScreen.on_enter: {e}")
#
#     def update_story_grid(self):
#         """Update the story grid with recent recordings."""
#         try:
#             # Get reference to the grid layout
#             story_grid = self.ids.story_grid
#
#             # Clear existing children
#             story_grid.clear_widgets()
#             print("Cleared story grid")
#
#             # Get recent recordings
#             app = App.get_running_app()
#             recent_recordings = self.get_recent_recordings(app.database, limit=3)
#             print(f"Found {len(recent_recordings) if recent_recordings else 0} recent recordings")
#
#             # Add recordings as buttons
#             if recent_recordings:
#                 for recording in recent_recordings:
#                     # Make sure we're getting the actual data, not the object's attributes
#                     try:
#                         recording_id, title, description, filepath, duration, date_created, cover_art = recording
#
#                         # Create a button for each recording
#                         recording_btn = Button(
#                             text=title if title and isinstance(title, str) else "Untitled Recording",
#                             background_normal='',
#                             on_release=lambda x, rec_id=recording_id: self.play_recording(rec_id)
#                         )
#
#                         # Apply custom styling with rounded corners
#                         import random
#                         hue = random.random() * 0.2 + 0.2  # Random blue-ish hue
#                         recording_btn.background_color = (hue, hue + 0.2, 0.8, 1)
#
#                         # Add rounded corners
#                         with recording_btn.canvas.before:
#                             from kivy.graphics import Color, RoundedRectangle
#                             Color(*recording_btn.background_color)
#                             recording_btn._rect = RoundedRectangle(
#                                 pos=recording_btn.pos,
#                                 size=recording_btn.size,
#                                 radius=[10]
#                             )
#                         recording_btn.bind(pos=self.update_rect, size=self.update_rect)
#
#                         story_grid.add_widget(recording_btn)
#                         print(f"Added recording button: {title}")
#                     except Exception as e:
#                         print(f"Error displaying recording: {e}")
#
#             # Add "All Recordings" button if we have fewer than 4 recordings
#             if len(recent_recordings) < 4:
#                 all_btn = Button(
#                     text="All Recordings",
#                     background_normal='',
#                     background_color=(0.3, 0.7, 0.4, 1),
#                     on_release=lambda x: self.navigate_to('file_list')
#                 )
#
#                 # Add rounded corners
#                 with all_btn.canvas.before:
#                     from kivy.graphics import Color, RoundedRectangle
#                     Color(*all_btn.background_color)
#                     all_btn._rect = RoundedRectangle(
#                         pos=all_btn.pos,
#                         size=all_btn.size,
#                         radius=[10]
#                     )
#                 all_btn.bind(pos=self.update_rect, size=self.update_rect)
#
#                 story_grid.add_widget(all_btn)
#                 print("Added All Recordings button")
#
#         except Exception as e:
#             print(f"Error updating story grid: {e}")
#
#     def get_recent_recordings(self, database, limit=4):
#         """Get the most recently added recordings."""
#         if database:
#             try:
#                 all_recordings = database.get_all_recordings()
#                 return all_recordings[:limit] if all_recordings else []
#             except Exception as e:
#                 print(f"Error fetching recent recordings: {e}")
#                 return []
#         return []
#
#     def navigate_to(self, screen_name):
#         """Navigate to another screen."""
#         app = App.get_running_app()
#         print(f"Navigating to: {screen_name}")
#         try:
#             if hasattr(app, 'root_layout'):
#                 app.root_layout.current = screen_name
#             else:
#                 print("app.root_layout not found!")
#         except Exception as e:
#             print(f"Error in navigate_to: {e}")
#
#     def play_recording(self, recording_id):
#         """Play a specific recording."""
#         app = App.get_running_app()
#         try:
#             recording = app.database.get_recording(recording_id)
#
#             if recording:
#                 # Navigate to the playback screen first
#                 app.root_layout.current = 'playback'
#
#                 # Access the playback screen
#                 playback_screen = app.root_layout.get_screen('playback')
#                 if not playback_screen:
#                     print("Could not access playback screen")
#                     return
#
#                 filepath = recording[3]  # Get filepath from recording tuple
#
#                 # First load the file in our player
#                 success = app.player.load(filepath)
#                 if success:
#                     # Update the playback screen
#                     playback_screen.update_playback_info(recording)
#
#                     # Wait a moment for UI to update before playing
#                     from kivy.clock import Clock
#                     def start_playback(dt):
#                         app.player.play()
#
#                     Clock.schedule_once(start_playback, 0.1)
#                 else:
#                     print(f"Failed to load recording: {recording[1]}")
#             else:
#                 print(f"Recording not found: ID {recording_id}")
#         except Exception as e:
#             print(f"Error playing recording: {e}")


from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.app import App
import os
import theme


class HomeScreen(Screen):
    """Main home screen for the app."""

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        print("HomeScreen initialized")

    def on_enter(self):
        """Called when the screen is entered - refresh content."""
        print("HomeScreen entered")

        try:
            # Make sure we have story_grid in our IDs
            if hasattr(self, 'ids') and hasattr(self.ids, 'story_grid'):
                # Update the story grid with recordings
                self.update_story_grid()
                print("Story grid updated")
            else:
                print("WARNING: story_grid not found in ids!")
        except Exception as e:
            print(f"Error in HomeScreen.on_enter: {e}")

    def update_story_grid(self):
        """Update the story grid with recent recordings."""
        try:
            # Get reference to the grid layout
            story_grid = self.ids.story_grid

            # Clear existing children
            story_grid.clear_widgets()
            print("Cleared story grid")

            # Get recent recordings
            app = App.get_running_app()
            recent_recordings = self.get_recent_recordings(app.database, limit=3)
            print(f"Found {len(recent_recordings) if recent_recordings else 0} recent recordings")

            # Add recordings as buttons
            if recent_recordings:
                for recording in recent_recordings:
                    # Make sure we're getting the actual data, not the object's attributes
                    try:
                        recording_id, title, description, filepath, duration, date_created, cover_art = recording

                        # Create a button for each recording
                        recording_btn = Button(
                            text=title if title and isinstance(title, str) else "Untitled Recording",
                            background_normal='',
                            on_release=lambda x, rec_id=recording_id: self.play_recording(rec_id)
                        )

                        # Apply custom styling with rounded corners
                        import random
                        hue = random.random() * 0.2 + 0.2  # Random blue-ish hue
                        recording_btn.background_color = (hue, hue + 0.2, 0.8, 1)

                        # Add rounded corners
                        with recording_btn.canvas.before:
                            from kivy.graphics import Color, RoundedRectangle
                            Color(*recording_btn.background_color)
                            recording_btn._rect = RoundedRectangle(
                                pos=recording_btn.pos,
                                size=recording_btn.size,
                                radius=[10]
                            )
                        recording_btn.bind(pos=self.update_rect, size=self.update_rect)

                        story_grid.add_widget(recording_btn)
                        print(f"Added recording button: {title}")
                    except Exception as e:
                        print(f"Error displaying recording: {e}")

            # Add "All Recordings" button if we have fewer than 4 recordings
            if len(recent_recordings) < 4:
                all_btn = Button(
                    text="All Recordings",
                    background_normal='',
                    background_color=(0.3, 0.7, 0.4, 1),
                    on_release=lambda x: self.navigate_to('file_list')
                )

                # Add rounded corners
                with all_btn.canvas.before:
                    from kivy.graphics import Color, RoundedRectangle
                    Color(*all_btn.background_color)
                    all_btn._rect = RoundedRectangle(
                        pos=all_btn.pos,
                        size=all_btn.size,
                        radius=[10]
                    )
                all_btn.bind(pos=self.update_rect, size=self.update_rect)

                story_grid.add_widget(all_btn)
                print("Added All Recordings button")

        except Exception as e:
            print(f"Error updating story grid: {e}")

    def update_rect(self, instance, value):
        """Update button rectangle on size/pos changes."""
        if hasattr(instance, '_rect'):
            instance._rect.pos = instance.pos
            instance._rect.size = instance.size

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

                filepath = recording[3]  # Get filepath from recording tuple

                # First load the file in our player
                success = app.player.load(filepath)
                if success:
                    # Update the playback screen
                    playback_screen.update_playback_info(recording)

                    # Wait a moment for UI to update before playing
                    from kivy.clock import Clock
                    def start_playback(dt):
                        app.player.play()

                    Clock.schedule_once(start_playback, 0.1)
                else:
                    print(f"Failed to load recording: {recording[1]}")
            else:
                print(f"Recording not found: ID {recording_id}")
        except Exception as e:
            print(f"Error playing recording: {e}")