from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse, Rectangle
from datetime import datetime
import random
import os
import math

from miscel.audio_story_app import theme
from miscel.audio_story_app.button_icons import IconButton

# Define theme colors directly in this file to avoid import issues
BACKGROUND_COLOR = (0.1, 0.18, 0.32, 1)  # Deep navy - night sky
PRIMARY_COLOR = (0.48, 0.54, 0.93, 1)  # Soft lavender/blue
ACCENT_COLOR = (1, 0.83, 0.52, 1)  # Warm gold - like stars
SURFACE_COLOR = (0.15, 0.23, 0.4, 1)  # Slightly lighter navy
CARD_COLOR = (0.19, 0.28, 0.47, 1)  # Blue-purple card background
TEXT_COLOR = (1, 1, 1, 1)  # White text for readability
SECONDARY_TEXT_COLOR = (0.8, 0.84, 1, 1)  # Light blue-white text
SUCCESS_COLOR = (0.43, 0.86, 0.71, 1)  # Teal/mint
WARNING_COLOR = (1, 0.75, 0.33, 1)  # Amber
ERROR_COLOR = (1, 0.61, 0.54, 1)  # Soft coral/red
DIVIDER_COLOR = (0.22, 0.31, 0.5, 1)  # Light blue divider

# Additional color palette
STAR_GOLD = (1, 0.83, 0.52, 1)  # Golden yellow - main star color
STAR_WHITE = (1, 1, 1, 1)  # White - bright stars
STAR_BLUE = (0.7, 0.88, 1, 1)  # Light blue - distant stars


class RoundedSlider(Slider):
    """Custom slider with rounded appearance."""

    def __init__(self, **kwargs):
        super(RoundedSlider, self).__init__(**kwargs)

        # Update the slider appearance
        with self.canvas.before:
            # Background track
            Color(rgba=SURFACE_COLOR)
            self.track_bg = RoundedRectangle(
                pos=(self.x, self.center_y - dp(4)),
                size=(self.width, dp(8)),
                radius=[dp(4)]
            )

            # Progress track
            Color(rgba=ACCENT_COLOR)
            self.progress = RoundedRectangle(
                pos=(self.x, self.center_y - dp(4)),
                size=(0, dp(8)),
                radius=[dp(4)]
            )

        # Update rectangles when slider changes
        self.bind(pos=self.update_graphics, size=self.update_graphics, value=self.update_graphics)

    def update_graphics(self, instance, value):
        """Update graphics when slider properties change."""
        if self.max == 0:  # Avoid division by zero
            progress_width = 0
        else:
            progress_width = (self.value / self.max) * self.width

        # Update track background
        self.track_bg.pos = (self.x, self.center_y - dp(4))
        self.track_bg.size = (self.width, dp(8))

        # Update progress bar
        self.progress.pos = (self.x, self.center_y - dp(4))
        self.progress.size = (progress_width, dp(8))


class IconToggleButton(ToggleButton):
    """Toggle button with icon and different states."""

    def __init__(self, icon_type='repeat', **kwargs):
        # No text, we'll use icons
        kwargs['text'] = ''
        super(IconToggleButton, self).__init__(**kwargs)
        self.icon_type = icon_type

        # Add background
        with self.canvas.before:
            Color(rgba=SURFACE_COLOR)
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)] * 4
            )

        # Add icon with different colors for different states
        with self.canvas.after:
            self.update_icon()

        # Bind to update when state or size changes
        self.bind(state=self.on_state_change, pos=self.update_rect, size=self.update_rect)

    def on_state_change(self, instance, value):
        """Handle state change (pressed/normal)."""
        # Update background color
        with self.canvas.before:
            if value == 'down':
                Color(rgba=ACCENT_COLOR)
            else:
                Color(rgba=SURFACE_COLOR)

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)] * 4
            )

        # Update icon
        self.update_icon()

    def update_rect(self, instance, value):
        """Update rectangle when size changes."""
        if hasattr(self, 'bg'):
            self.bg.pos = self.pos
            self.bg.size = self.size

        # Also update icon
        self.update_icon()

    def update_icon(self):
        """Draw the appropriate icon."""
        self.canvas.after.clear()

        with self.canvas.after:
            # Use white icon for active state, light blue for inactive
            if self.state == 'down':
                Color(rgba=TEXT_COLOR)  # White
            else:
                Color(rgba=SECONDARY_TEXT_COLOR)  # Light blue

            # Get centered position
            cx = self.x + self.width / 2
            cy = self.y + self.height / 2
            size = min(self.width, self.height) * 0.5

            if self.icon_type == 'repeat':
                # Draw repeat circle with arrow
                Line(
                    circle=(cx, cy, size / 2),
                    width=dp(2)
                )

                # Arrow head at bottom
                arrow_size = size / 4
                triangle_points = [
                    cx, cy - size / 2 - arrow_size / 2,  # Bottom point
                        cx - arrow_size / 2, cy - size / 2 + arrow_size / 2,  # Left point
                        cx + arrow_size / 2, cy - size / 2 + arrow_size / 2  # Right point
                ]
                Line(points=triangle_points, width=dp(2))

            elif self.icon_type == 'continue':
                # Draw next track icon (triangle with bar)
                tri_size = size * 0.6
                bar_width = size / 5

                # Triangle
                triangle_points = [
                    cx - tri_size / 2, cy - tri_size / 2,  # Left bottom
                    cx - tri_size / 2, cy + tri_size / 2,  # Left top
                    cx + tri_size / 2 - bar_width, cy  # Right middle
                ]
                Line(points=triangle_points, width=dp(2))

                # Bar
                Line(
                    points=[
                        cx + tri_size / 2 - bar_width, cy - tri_size / 2,
                        cx + tri_size / 2 - bar_width, cy + tri_size / 2
                    ],
                    width=dp(2)
                )


class RoundControlButton(Button):
    """Button with custom drawn icon and rounded appearance."""

    def __init__(self, icon_type='play', **kwargs):
        # No text, we'll use icons
        kwargs['text'] = ''
        super(RoundControlButton, self).__init__(**kwargs)
        self.icon_type = icon_type

        # Default background
        with self.canvas.before:
            Color(rgba=PRIMARY_COLOR)
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[min(self.width, self.height) / 2] * 4  # Fully rounded
            )

        # Add icon
        with self.canvas.after:
            self.draw_icon()

        # Bind to update when size changes
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, instance, value):
        """Update rectangle when size changes."""
        # Update background
        if hasattr(self, 'bg'):
            self.bg.pos = self.pos
            self.bg.size = self.size
            # Make sure it stays circular
            self.bg.radius = [min(self.width, self.height) / 2] * 4

        # Redraw icon
        self.canvas.after.clear()
        with self.canvas.after:
            self.draw_icon()

    def draw_icon(self):
        """Draw the appropriate icon."""
        # Get centered position
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        size = min(self.width, self.height) * 0.4  # Icon size relative to button

        # White icon for visibility
        Color(rgba=TEXT_COLOR)

        if self.icon_type == 'play':
            # Draw play triangle
            triangle_points = [
                cx - size / 2, cy - size / 2,  # Left bottom
                cx - size / 2, cy + size / 2,  # Left top
                cx + size / 2, cy  # Right middle
            ]
            Line(points=triangle_points, width=dp(2))

        elif self.icon_type == 'pause':
            # Draw two pause bars
            bar_width = size / 3
            bar_spacing = size / 4

            # Left bar
            Line(
                points=[
                    cx - bar_spacing - bar_width, cy - size / 2,
                    cx - bar_spacing - bar_width, cy + size / 2
                ],
                width=dp(2)
            )

            # Right bar
            Line(
                points=[
                    cx + bar_spacing, cy - size / 2,
                    cx + bar_spacing, cy + size / 2
                ],
                width=dp(2)
            )

        elif self.icon_type == 'back':
            # Left-pointing triangle
            triangle_points = [
                cx + size / 2, cy - size / 2,  # Right bottom
                cx + size / 2, cy + size / 2,  # Right top
                cx - size / 2, cy  # Left middle
            ]
            Line(points=triangle_points, width=dp(2))

        elif self.icon_type == 'rewind':
            # Draw rewind (double triangle)
            tri_size = size * 0.4
            spacing = tri_size / 4

            # Left triangle
            Line(
                points=[
                    cx - spacing - tri_size, cy,  # Left middle
                    cx - spacing, cy + tri_size / 2,  # Right top
                    cx - spacing, cy - tri_size / 2,  # Right bottom
                    cx - spacing - tri_size, cy  # Back to left middle
                ],
                width=dp(2)
            )

            # Right triangle
            Line(
                points=[
                    cx + spacing, cy,  # Right middle
                    cx + spacing + tri_size, cy + tri_size / 2,  # Left top
                    cx + spacing + tri_size, cy - tri_size / 2,  # Left bottom
                    cx + spacing, cy  # Back to right middle
                ],
                width=dp(2)
            )

        elif self.icon_type == 'forward':
            # Draw forward (double triangle)
            tri_size = size * 0.4
            spacing = tri_size / 4

            # Left triangle
            Line(
                points=[
                    cx - spacing - tri_size, cy + tri_size / 2,  # Left top
                    cx - spacing - tri_size, cy - tri_size / 2,  # Left bottom
                    cx - spacing, cy,  # Right middle
                    cx - spacing - tri_size, cy + tri_size / 2  # Back to left top
                ],
                width=dp(2)
            )

            # Right triangle
            Line(
                points=[
                    cx + spacing, cy + tri_size / 2,  # Right top
                    cx + spacing, cy - tri_size / 2,  # Right bottom
                    cx + spacing + tri_size, cy,  # Right middle
                    cx + spacing, cy + tri_size / 2  # Back to right top
                ],
                width=dp(2)
            )


class StarryNightBackground(BoxLayout):
    """Background with animated stars for the playback screen."""

    def __init__(self, **kwargs):
        super(StarryNightBackground, self).__init__(**kwargs)
        self.stars = []
        Clock.schedule_once(self.create_stars, 0)
        Clock.schedule_interval(self.animate_stars, 2)  # Twinkle every 2 seconds

    def create_stars(self, dt):
        """Create the initial star field."""
        self.canvas.before.clear()

        with self.canvas.before:
            # Background gradient (approximated with rectangles)
            Color(rgba=BACKGROUND_COLOR)
            self.bg = Rectangle(pos=self.pos, size=self.size)

            # Create stars
            self.stars = []
            for _ in range(30):  # Number of stars
                x = random.random() * self.width
                y = random.random() * self.height
                size = random.random() * 2.5 + 0.5

                # Randomize color between white and gold
                if random.random() > 0.7:
                    color = STAR_GOLD
                    alpha = random.random() * 0.8 + 0.2
                else:
                    color = STAR_WHITE
                    alpha = random.random() * 0.7 + 0.3

                Color(rgba=(color[0], color[1], color[2], alpha))
                star = Ellipse(pos=(x, y), size=(size, size))
                self.stars.append((star, color, alpha))

    def animate_stars(self, dt):
        """Animate stars by changing brightness."""
        with self.canvas.before:
            for i, (star, color, alpha) in enumerate(self.stars):
                # Randomly adjust brightness
                new_alpha = max(0.1, min(1.0, alpha + (random.random() - 0.5) * 0.3))

                # Update star color
                Color(rgba=(color[0], color[1], color[2], new_alpha))

                # Recreate star with same position/size
                pos = star.pos
                size = star.size
                self.canvas.before.remove(star)
                new_star = Ellipse(pos=pos, size=size)
                self.stars[i] = (new_star, color, new_alpha)

    def on_size(self, *args):
        """Handle size changes."""
        Clock.schedule_once(self.create_stars, 0)


class PlaybackScreen(Screen):
    """Playback screen with rounded UI and starry background."""

    def __init__(self, **kwargs):
        super(PlaybackScreen, self).__init__(**kwargs)
        self.current_recording = None
        self.position_slider = None
        self.time_label = None
        self.title_label = None
        self.play_pause_btn = None
        self.update_event = None
        self.is_slider_being_dragged = False
        self.description_label = None
        self.date_label = None
        self.repeat_enabled = False
        self.repeat_btn = None  # Add this line
        self._handling_track_finish = False  # Add this line
        self.current_playlist_id = None
        # Build UI during initialization
        self.build_ui()

    def on_enter(self):
        """Called when the screen is entered."""
        # Start the UI update timer
        if not self.update_event:
            self.update_event = Clock.schedule_interval(self.update_ui, 0.1)

        # Update the UI based on current playback state
        self.update_play_pause_button()

        # Register for track finished event
        app = App.get_running_app()
        if app.player:
            app.player.bind(on_track_finished=self.on_track_finished)

    def build_ui(self):
        """Build the UI for the playback screen."""
        self.clear_widgets()

        # Use a fixed layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint=(1, 1)
        )

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
            background_normal='',
            background_color=theme.PRIMARY_COLOR,
            on_release=self.go_back
        )
        self.apply_rounded_style(back_btn, theme.PRIMARY_COLOR)
        header.add_widget(back_btn)

        self.title_label = Label(
            text="Now Playing",
            font_size=dp(20),
            halign='center'
        )
        header.add_widget(self.title_label)

        main_layout.add_widget(header)

        # Recording info section
        info_layout = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            size_hint_y=None,
            height=dp(120)
        )

        # Description label
        self.description_label = Label(
            text="",
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle'
        )
        info_layout.add_widget(self.description_label)

        # Date created
        self.date_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14)
        )
        info_layout.add_widget(self.date_label)

        main_layout.add_widget(info_layout)

        # Spacer
        main_layout.add_widget(BoxLayout(size_hint_y=0.2))

        # Playback controls section
        controls_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
            height=dp(220)
        )

        # Time and position slider
        time_layout = BoxLayout(
            size_hint_y=None,
            height=dp(30)
        )

        self.time_label = Label(
            text="00:00 / 00:00",
            size_hint_x=1.0
        )
        time_layout.add_widget(self.time_label)

        controls_layout.add_widget(time_layout)

        # Position slider with custom appearance
        self.position_slider = Slider(
            min=0,
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(30),
            cursor_size=(dp(20), dp(20))
        )
        self.position_slider.bind(on_touch_down=self.on_slider_touch_down)
        self.position_slider.bind(on_touch_up=self.on_slider_touch_up)
        controls_layout.add_widget(self.position_slider)

        # Playback buttons
        buttons_layout = BoxLayout(
            size_hint_y=None,
            height=dp(70),
            spacing=dp(20),
            padding=[dp(20), 0]
        )

        # Use text labels that clearly show the button purpose instead of Unicode
        # Rewind button
        rewind_btn = Button(
            text="<<",  # Use regular text instead of Unicode
            font_size=dp(24),
            background_normal='',
            background_color=theme.PRIMARY_COLOR,
            on_release=self.rewind
        )
        self.apply_rounded_style(rewind_btn, theme.PRIMARY_COLOR)
        buttons_layout.add_widget(rewind_btn)

        # Play/Pause button
        self.play_pause_btn = Button(
            text="Play",  # Start with simple text
            font_size=dp(24),
            background_normal='',
            background_color=theme.ACCENT_COLOR,
            on_release=self.toggle_play_pause
        )
        self.apply_rounded_style(self.play_pause_btn, theme.ACCENT_COLOR)
        buttons_layout.add_widget(self.play_pause_btn)

        # Forward button
        forward_btn = Button(
            text=">>",  # Use regular text instead of Unicode
            font_size=dp(24),
            background_normal='',
            background_color=theme.PRIMARY_COLOR,
            on_release=self.forward
        )
        self.apply_rounded_style(forward_btn, theme.PRIMARY_COLOR)
        buttons_layout.add_widget(forward_btn)

        controls_layout.add_widget(buttons_layout)

        # Additional control buttons
        extra_buttons = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(20),
            padding=[dp(20), 0]
        )

        # Repeat button
        self.repeat_btn = Button(
            text="Repeat",  # Use regular text
            font_size=dp(16),
            background_normal='',
            background_color=theme.SURFACE_COLOR,
            on_release=self.toggle_repeat
        )
        self.apply_rounded_style(self.repeat_btn, theme.SURFACE_COLOR)
        extra_buttons.add_widget(self.repeat_btn)

        # Add to playlist button
        playlist_btn = Button(
            text="Playlist",  # Use regular text
            font_size=dp(16),
            background_normal='',
            background_color=theme.SURFACE_COLOR,
            on_release=self.add_to_playlist
        )
        self.apply_rounded_style(playlist_btn, theme.SURFACE_COLOR)
        extra_buttons.add_widget(playlist_btn)

        controls_layout.add_widget(extra_buttons)

        # Volume slider
        volume_layout = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        volume_label = Label(
            text="Volume",
            font_size=dp(16),
            size_hint_x=0.2
        )
        volume_layout.add_widget(volume_label)

        volume_slider = Slider(
            min=0,
            max=1,
            value=1,
            size_hint_x=0.8
        )
        volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(volume_slider)
        controls_layout.add_widget(volume_layout)

        main_layout.add_widget(controls_layout)

        # Add a spacer at the bottom to push content up
        main_layout.add_widget(BoxLayout(size_hint_y=0.1))

        self.add_widget(main_layout)

    def apply_rounded_style(self, button, color):
        """Apply rounded style to a button."""
        button.canvas.before.clear()
        with button.canvas.before:
            Color(*color)
            button._rect = RoundedRectangle(pos=button.pos, size=button.size, radius=[dp(10)])
        button.bind(pos=self.update_button_rect, size=self.update_button_rect)

    def update_button_rect(self, instance, value):
        """Update button rectangle on size/pos changes."""
        if hasattr(instance, '_rect'):
            instance._rect.pos = instance.pos
            instance._rect.size = instance.size

    def update_header_bg(self, instance, value):
        """Update header background when layout changes."""
        if hasattr(self, 'header_bg'):
            self.header_bg.pos = instance.pos
            self.header_bg.size = instance.size

    def update_visual_bg(self, instance, value):
        """Update visualization card background when layout changes."""
        if hasattr(self, 'visual_bg'):
            self.visual_bg.pos = instance.pos
            self.visual_bg.size = instance.size

    def update_controls_bg(self, instance, value):
        """Update controls card background when layout changes."""
        if hasattr(self, 'controls_bg'):
            self.controls_bg.pos = instance.pos
            self.controls_bg.size = instance.size

    def update_playlist_btn_bg(self, instance, value):
        """Update playlist button background when layout changes."""
        if hasattr(self, 'playlist_btn_bg'):
            self.playlist_btn_bg.pos = instance.pos
            self.playlist_btn_bg.size = instance.size

    def toggle_repeat(self, instance):
        """Toggle repeat mode."""
        # Ensure the attribute exists
        if not hasattr(self, 'repeat_enabled'):
            self.repeat_enabled = False

        # Toggle the repeat mode
        self.repeat_enabled = not self.repeat_enabled

        # Update button appearance
        if self.repeat_enabled:
            self.repeat_btn.background_color = theme.ACCENT_COLOR
            self.apply_rounded_style(self.repeat_btn, theme.ACCENT_COLOR)
            print("Repeat mode enabled")
        else:
            self.repeat_btn.background_color = theme.SURFACE_COLOR
            self.apply_rounded_style(self.repeat_btn, theme.SURFACE_COLOR)
            print("Repeat mode disabled")

    def update_playback_info(self, recording):
        """Update the UI with recording information."""
        if not recording:
            print("No recording provided")
            return

        print(f"Updating playback info with recording: {recording}")
        self.current_recording = recording

        try:
            recording_id, title, description, filepath, duration, date_created, cover_art = recording

            # Update title
            if title and isinstance(title, str):
                self.title_label.text = title
            else:
                self.title_label.text = "Untitled Recording"

            # Update description
            if description and isinstance(description, str):
                self.description_label.text = description
            else:
                self.description_label.text = "No description"

            # Update date
            try:
                if date_created and isinstance(date_created, str):
                    dt = datetime.fromisoformat(date_created)
                    formatted_date = dt.strftime("%b %d, %Y %H:%M")
                else:
                    formatted_date = "Unknown date"
            except Exception as e:
                print(f"Error formatting date: {e}")
                formatted_date = "Invalid date"

            self.date_label.text = formatted_date

            # Update slider max value
            app = App.get_running_app()
            if app.player and app.player.duration > 0:
                self.position_slider.max = app.player.duration
                print(f"Setting slider max to {app.player.duration}")
            elif duration and duration > 0:
                self.position_slider.max = duration
                print(f"Setting slider max to {duration}")
            else:
                self.position_slider.max = 100  # Default
                print("Using default slider max of 100")

            # Update play/pause button
            self.update_play_pause_button()

        except Exception as e:
            print(f"Error updating playback info: {e}")


    def update_ui(self, dt):
        """Update UI based on playback state."""
        app = App.get_running_app()

        if not app.player or not app.player.sound:
            return

        try:
            # Update position slider if not being dragged
            if not self.is_slider_being_dragged:
                self.position_slider.value = app.player.current_pos

            # Update time label
            current_pos = app.player.current_pos
            duration = app.player.duration

            # Format time as MM:SS / MM:SS
            current_min = int(current_pos) // 60
            current_sec = int(current_pos) % 60
            total_min = int(duration) // 60
            total_sec = int(duration) % 60

            self.time_label.text = f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}"

            # Update play/pause button
            self.update_play_pause_button()

        except Exception as e:
            print(f"Error updating UI: {e}")

    def update_play_pause_button(self):
        """Update the play/pause button text based on playback state."""
        app = App.get_running_app()
        try:
            if app.player and app.player.is_playing:
                self.play_pause_btn.text = "Pause"  # Simple text that will definitely work
            else:
                self.play_pause_btn.text = "Play"  # Simple text that will definitely work
        except Exception as e:
            print(f"Error updating play/pause button: {e}")

    def toggle_play_pause(self, instance):
        """Toggle between play and pause states."""
        app = App.get_running_app()

        if not app.player or not app.player.sound:
            print("No sound loaded to toggle playback")
            return

        try:
            if app.player.is_playing:
                print("Pausing playback via button press")
                app.player.pause()
            else:
                print("Starting/resuming playback via button press")
                app.player.play()

            # Update button immediately
            self.update_play_pause_button()

        except Exception as e:
            print(f"Error toggling play/pause: {e}")

    def rewind(self, instance):
        """Rewind by 10 seconds."""
        app = App.get_running_app()

        if not app.player or not app.player.sound:
            return

        try:
            # Reset track finished state if seeking
            if self.is_track_finished:
                self.is_track_finished = False

            # Seek backward 10 seconds
            new_pos = max(0, app.player.current_pos - 10)
            print(f"Rewinding to position: {new_pos}")
            app.player.seek(new_pos)

        except Exception as e:
            print(f"Error rewinding: {e}")

    def forward(self, instance):
        """Forward by 10 seconds."""
        app = App.get_running_app()

        if not app.player or not app.player.sound:
            return

        try:
            # Seek forward 10 seconds
            new_pos = min(app.player.duration, app.player.current_pos + 10)
            print(f"Fast forwarding to position: {new_pos}")
            app.player.seek(new_pos)

        except Exception as e:
            print(f"Error fast forwarding: {e}")

    def on_slider_touch_down(self, instance, touch):
        """Handle slider touch down with proper seeking."""
        if instance.collide_point(*touch.pos):
            print("Slider touch down - starting drag")
            self.is_slider_being_dragged = True

            # Reset track finished state when seeking
            self.is_track_finished = False

            # Calculate position based on touch
            value = self.calculate_slider_value(instance, touch)
            instance.value = value

            # Update time label during dragging
            self.update_time_during_drag(value)

            # Apply immediate seek for better feedback
            app = App.get_running_app()
            if app.player and app.player.sound:
                app.player.seek(value)

            return True
        return False

    def calculate_slider_value(self, slider, touch):
        """Calculate slider value based on touch position."""
        # Get available width for slider movement
        available_width = slider.width

        # Calculate relative position (0 to 1)
        rel_x = max(0, min(1, (touch.x - slider.x) / available_width))

        # Convert to slider value
        value = slider.min + rel_x * (slider.max - slider.min)

        # Ensure it's within bounds
        return max(slider.min, min(slider.max, value))

    def on_slider_touch_move(self, instance, touch):
        """Handle slider movement with responsive updates."""
        if self.is_slider_being_dragged and touch.grab_current == instance:
            # Calculate new value based on touch position
            value = self.calculate_slider_value(instance, touch)

            # Only update if value changed significantly
            if abs(instance.value - value) > 0.1:
                instance.value = value

                # Update time display during drag
                self.update_time_during_drag(value)

                # Perform seek during dragging for better feedback
                app = App.get_running_app()
                if app.player and app.player.sound:
                    app.player.seek(value)

            return True
        return False

    def on_slider_touch_up(self, instance, touch):
        """Handle slider touch up with final seek."""
        if self.is_slider_being_dragged and touch.grab_current == instance:
            # Final seek on release
            app = App.get_running_app()
            if app.player and app.player.sound:
                app.player.seek(instance.value)

            # Reset dragging state
            self.is_slider_being_dragged = False

            # Update time display
            self.update_time_during_drag(instance.value)

            # Ensure UI updates
            self.update_play_pause_button()

            return True

        self.is_slider_being_dragged = False
        return False

    def update_time_during_drag(self, value):
        """Update time label during slider dragging."""
        app = App.get_running_app()
        if app.player and app.player.sound:
            # Format as MM:SS / MM:SS
            current_min = int(value) // 60
            current_sec = int(value) % 60
            total_min = int(app.player.duration) // 60
            total_sec = int(app.player.duration) % 60

            time_text = f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}"
            self.time_label.text = time_text

    def on_volume_change(self, instance, value):
        """Change playback volume."""
        app = App.get_running_app()

        if not app.player:
            return

        try:
            app.player.set_volume(value)
        except Exception as e:
            print(f"Error changing volume: {e}")

    def add_to_playlist(self, instance):
        """Show dialog to add current recording to a playlist."""
        app = App.get_running_app()
        if not self.current_recording:
            return

        # Get the recording ID
        recording_id = self.current_recording[0]

        # Show the playlist selection dialog
        file_list_screen = app.root_layout.get_screen('file_list')
        if hasattr(file_list_screen, 'show_playlist_options'):
            file_list_screen.show_playlist_options(recording_id)

    def on_track_finished(self, *args):
        """Handle track completion event."""
        try:
            print("Track finished event received in playback screen")

            # First check if repeat mode is enabled
            if hasattr(self, 'repeat_enabled') and self.repeat_enabled:
                print("Repeat enabled, restarting track")
                app = App.get_running_app()
                if app.player and app.player.sound:
                    # Schedule the restart for the next frame to avoid VLC issues
                    Clock.schedule_once(lambda dt: app.player.play(), 0.1)

            # If not repeating, try to play next track in playlist
            elif hasattr(self, 'current_playlist_id') and self.current_playlist_id:
                success = self.play_next_in_playlist()
                if not success:
                    print("No next track available or error playing next track")
            else:
                print("Repeat not enabled and not in playlist, track will remain stopped")

        except Exception as e:
            print(f"Error handling track finished: {e}")

    def restart_track(self):
        """Restart the current track from beginning."""
        app = App.get_running_app()
        if app.player and app.player.sound and self.current_recording:
            print("Performing track restart")
            # Reload the file to ensure proper restart
            filepath = self.current_recording[3]
            if app.player.load(filepath):
                # Update UI
                self.is_track_finished = False
                # Start playback
                app.player.play()
                # Update button state
                self.update_play_pause_button()

    def play_recording(self, recording_id, playlist_id=None):
        """Play a specific recording, optionally as part of a playlist."""
        app = App.get_running_app()
        try:
            # Store the playlist ID if provided
            if playlist_id is not None:
                self.current_playlist_id = playlist_id
            else:
                # Clear playlist ID if not playing from a playlist
                self.current_playlist_id = None

            recording = app.database.get_recording(recording_id)

            if recording:
                # Make sure we're on the playback screen
                app.root_layout.current = 'playback'

                # Get the filepath from the recording
                filepath = recording[3]  # filepath is at index 3

                # Load the recording into the player
                success = app.player.load(filepath)
                if success:
                    # Update playback info
                    self.current_recording = recording
                    self.update_playback_info(recording)

                    # Start playback
                    app.player.play()
                    print(f"Playing recording: {recording[1]}")  # title is at index 1
                else:
                    print(f"Failed to load recording: {recording[1]}")
            else:
                print(f"Recording not found: ID {recording_id}")
        except Exception as e:
            print(f"Error playing recording: {e}")

    def play_next_track(self):
        """Play the next track in the list."""
        if not self.current_recording:
            return

        app = App.get_running_app()
        recording_id = self.current_recording[0]

        # Get all recordings from database
        all_recordings = app.database.get_all_recordings()

        # Find current recording index
        current_index = -1
        for i, rec in enumerate(all_recordings):
            if rec[0] == recording_id:
                current_index = i
                break

        # Play next if available
        if current_index >= 0 and current_index < len(all_recordings) - 1:
            next_recording = all_recordings[current_index + 1]
            print(f"Playing next track: {next_recording[1]}")

            try:
                next_filepath = next_recording[3]
                if app.player.load(next_filepath):
                    # Update info and play
                    self.update_playback_info(next_recording)
                    app.player.play()
                    self.is_track_finished = False
                    self.update_play_pause_button()
            except Exception as e:
                print(f"Error playing next track: {e}")
        else:
            print("No next track available or at end of list")

    def go_back(self, instance):
        """Navigate back to previous screen."""
        app = App.get_running_app()
        app.root_layout.current = 'home'

    def play_next_in_playlist(self):
        """Play the next track in the current playlist if available."""
        app = App.get_running_app()

        # Check if we're in a playlist
        if not hasattr(self, 'current_playlist_id') or not self.current_playlist_id:
            print("Not in a playlist - can't play next track")
            return False

        try:
            # Get all recordings in the current playlist
            playlist_recordings = app.database.get_playlist_recordings(self.current_playlist_id)

            if not playlist_recordings or len(playlist_recordings) <= 1:
                print("Playlist empty or has only one item")
                return False

            # Find current recording's position in playlist
            current_position = None
            for i, rec in enumerate(playlist_recordings):
                if rec[0] == self.current_recording[0]:  # Compare recording IDs
                    current_position = i
                    break

            if current_position is None:
                print("Current recording not found in playlist")
                return False

            # Check if there's a next track
            if current_position < len(playlist_recordings) - 1:
                next_recording = playlist_recordings[current_position + 1]
                print(f"Playing next track: {next_recording[1]}")  # Title is at index 1

                # Play the next recording
                self.play_recording(next_recording[0])
                return True
            else:
                print("End of playlist reached")
                return False

        except Exception as e:
            print(f"Error playing next track: {e}")
            return False

    def on_leave(self):
        """Called when the screen is exited."""
        # Stop the UI update timer
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None

        # Unbind from track finished event
        app = App.get_running_app()
        if app.player:
            app.player.unbind(on_track_finished=self.on_track_finished)

