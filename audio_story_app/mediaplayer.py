import vlc
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.event import EventDispatcher
import os
import platform as sys_platform


class AudioPlayer(EventDispatcher):
    """Audio player using VLC for reliable playback control."""

    current_pos = NumericProperty(0)
    duration = NumericProperty(100)
    is_playing = BooleanProperty(False)
    current_file = StringProperty("")
    volume = NumericProperty(1.0)

    def __init__(self, **kwargs):
        self.register_event_type('on_track_finished')
        super(AudioPlayer, self).__init__(**kwargs)

        # Initialize VLC instance with proper path
        self.vlc_instance = None
        self.player = None
        self.sound = None  # For compatibility
        self.update_event = None
        self.end_reached = False
        self.initialize_vlc()

    def initialize_vlc(self):
        """Initialize VLC with better platform detection."""
        try:
            # Platform-specific initialization
            system = sys_platform.system()
            plugin_path = None

            print(f"Detected platform: {system}")

            if system == "Darwin":  # macOS
                possible_paths = [
                    '/Applications/VLC.app/Contents/MacOS/lib',
                    '/Applications/VLC.app/Contents/MacOS/plugins'
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        plugin_path = path
                        break

            elif system == "Windows":
                # Windows paths
                possible_paths = [
                    r"C:\Program Files\VideoLAN\VLC\plugins",
                    r"C:\Program Files (x86)\VideoLAN\VLC\plugins"
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        plugin_path = path
                        break

            elif system == "Linux":
                # Linux paths
                possible_paths = [
                    '/usr/lib/vlc/plugins',
                    '/usr/lib/x86_64-linux-gnu/vlc/plugins',
                    '/usr/local/lib/vlc/plugins'
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        plugin_path = path
                        break

            # Create the VLC instance
            if plugin_path:
                print(f"Using VLC plugin path: {plugin_path}")
                self.vlc_instance = vlc.Instance(f'--plugin-path={plugin_path}')
            else:
                print("No VLC plugin path found, using default instance")
                self.vlc_instance = vlc.Instance()

            # Create the media player
            self.player = self.vlc_instance.media_player_new()

            print("VLC initialized successfully")
        except Exception as e:
            print(f"Error initializing VLC: {e}")
            # Try a simple initialization as fallback
            try:
                self.vlc_instance = vlc.Instance()
                self.player = self.vlc_instance.media_player_new()
                print("Fallback VLC initialization succeeded")
            except Exception as e2:
                print(f"Fallback VLC initialization failed: {e2}")

    def load(self, filepath):
        """Load an audio file."""
        print(f"Loading file: {filepath}")

        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return False

        if not self.vlc_instance or not self.player:
            print("VLC not initialized")
            return False

        # Stop any current playback
        self.stop()

        # Reset end reached flag
        self.end_reached = False

        try:
            # Create a new media
            media = self.vlc_instance.media_new(filepath)

            # Set up the player
            self.player.set_media(media)

            # Get media information
            media.parse()

            # Set media properties
            self.current_file = filepath

            # Get duration (in milliseconds) and convert to seconds
            # Try to get duration after a small delay to ensure parsing is complete
            def get_duration(dt):
                duration_ms = self.player.get_length()
                if duration_ms > 0:
                    self.duration = duration_ms / 1000.0
                    print(f"Duration updated to {self.duration} seconds")
                else:
                    # Try a direct query to the media itself
                    media_duration = media.get_duration()
                    if media_duration > 0:
                        self.duration = media_duration / 1000.0
                        print(f"Media duration: {self.duration} seconds")
                    else:
                        # If VLC can't determine length, use fallback
                        self.duration = 100
                        print("Using fallback duration of 100 seconds")

            Clock.schedule_once(get_duration, 0.5)

            # Reset position
            self.current_pos = 0

            # Set flag for compatibility
            self.sound = True

            # Start position updates
            if self.update_event:
                self.update_event.cancel()
            self.update_event = Clock.schedule_interval(self.update_position, 0.1)

            print(f"File loaded successfully.")
            return True
        except Exception as e:
            print(f"Error loading audio file: {e}")
            self.sound = None
            return False

    def play(self):
        """Play or resume audio."""
        if not self.vlc_instance or not self.player:
            return

        try:
            # Reset end reached flag when playing
            self.end_reached = False
            self.player.play()
            self.is_playing = True
            print("Started/resumed playback")
        except Exception as e:
            print(f"Error playing audio: {e}")

    def pause(self):
        """Pause playback."""
        if not self.vlc_instance or not self.player:
            return

        try:
            self.player.pause()
            self.is_playing = False
            print("Paused playback")
        except Exception as e:
            print(f"Error pausing: {e}")

    def stop(self):
        """Stop playback and reset position."""
        if not self.vlc_instance or not self.player:
            return

        try:
            self.player.stop()
            self.is_playing = False
            self.current_pos = 0
            print("Stopped playback")
        except Exception as e:
            print(f"Error stopping: {e}")

    def seek(self, position):
        """Enhanced seek to a specific position in seconds."""
        if not self.vlc_instance or not self.player:
            print("Cannot seek: VLC not initialized")
            return

        try:
            # Convert to milliseconds for VLC
            ms_position = int(position * 1000)

            # Check if the position is valid
            if ms_position < 0:
                ms_position = 0

            # Get the current media length in case duration isn't updated yet
            length = self.player.get_length()
            if length > 0 and ms_position > length:
                ms_position = length

            # Perform the seek
            print(f"Seeking to {position}s ({ms_position}ms)")

            # Remember playback state
            was_playing = self.player.is_playing()

            # Reset end reached flag when seeking
            self.end_reached = False

            # Perform actual seek operation
            result = self.player.set_time(ms_position)

            # Update current position property
            self.current_pos = position

            print(f"Seek result: {'Success' if result != -1 else 'Failed'}")

            # Ensure playback continues if it was playing before
            if was_playing and not self.player.is_playing():
                self.player.play()

        except Exception as e:
            print(f"Error seeking: {e}")

    def set_volume(self, volume):
        """Set playback volume (0.0 to 1.0)."""
        if not self.vlc_instance or not self.player:
            return

        try:
            # VLC volume is 0-100
            vlc_volume = int(volume * 100)
            self.player.audio_set_volume(vlc_volume)
            self.volume = volume
            print(f"Volume set to: {volume}")
        except Exception as e:
            print(f"Error setting volume: {e}")

    def update_position(self, dt):
        """Update the current position property and check for end of track."""
        if not self.vlc_instance or not self.player:
            return

        try:
            # Get current time in milliseconds and convert to seconds
            time_ms = self.player.get_time()
            if time_ms >= 0:
                self.current_pos = time_ms / 1000.0

            # Update duration if it wasn't available at load time
            if self.duration <= 0 or self.duration == 100:  # If using the fallback duration
                length_ms = self.player.get_length()
                if length_ms > 0:
                    self.duration = length_ms / 1000.0

            # Check for end of playback - compare current position to duration
            if (not self.end_reached and
                    self.current_pos > 0 and
                    self.duration > 0 and
                    self.current_pos >= self.duration - 0.5):  # 0.5 second buffer

                print("Track reached end - position:", self.current_pos, "duration:", self.duration)
                self.end_reached = True
                self.is_playing = False

                # When end reached, reset position
                self.current_pos = 0

                # Dispatch the track finished event
                self.dispatch('on_track_finished')

            # Alternative end detection method - check state
            if not self.end_reached and self.player.get_state() == vlc.State.Ended:
                print("Track ended (state detection)")
                self.end_reached = True
                self.is_playing = False
                self.current_pos = 0
                self.dispatch('on_track_finished')

        except Exception as e:
            print(f"Error updating position: {e}")

    def on_track_finished(self, *args):
        """Event handler for track completion - to be overridden by subscribers."""
        print("Track finished event raised from player")


# Create singleton
player = AudioPlayer()
