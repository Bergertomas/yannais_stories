import vlc
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.event import EventDispatcher
import os
import time


class AudioPlayer(EventDispatcher):
    """Audio player using VLC for reliable playback control."""

    current_pos = NumericProperty(0)
    duration = NumericProperty(100)
    is_playing = BooleanProperty(False)
    current_file = StringProperty("")
    volume = NumericProperty(1.0)
    _track_finished = False  # Track whether we've already dispatched a finish event

    def __init__(self, **kwargs):
        self.register_event_type('on_track_finished')
        super(AudioPlayer, self).__init__(**kwargs)

        # Initialize VLC instance with proper path
        self.vlc_instance = None
        self.player = None
        self.sound = None  # For compatibility
        self.update_event = None
        self.initialize_vlc()

    def initialize_vlc(self):
        """Initialize VLC with more aggressive path finding."""
        try:
            # Try to find the actual VLC binary path
            import subprocess

            try:
                # Try to get VLC path from the system
                result = subprocess.run(['which', 'vlc'], capture_output=True, text=True)
                vlc_binary = result.stdout.strip()

                if vlc_binary:
                    # Get the directory containing VLC
                    vlc_dir = os.path.dirname(vlc_binary)
                    print(f"Found VLC binary at: {vlc_dir}")

                    # Use this to find the lib directory
                    if "/Applications/VLC.app" in vlc_dir:
                        # Mac app bundle
                        plugin_path = '/Applications/VLC.app/Contents/MacOS/lib'
                    else:
                        # Try common relative paths from the binary
                        possible_lib_paths = [
                            os.path.join(vlc_dir, '..', 'lib'),
                            os.path.join(vlc_dir, '..', 'lib', 'vlc'),
                            os.path.join(vlc_dir, 'lib'),
                            os.path.join(vlc_dir, 'lib', 'vlc')
                        ]

                        for path in possible_lib_paths:
                            if os.path.exists(path):
                                plugin_path = path
                                break

                    if plugin_path:
                        print(f"Using VLC plugin path: {plugin_path}")
                        self.vlc_instance = vlc.Instance(f'--plugin-path={plugin_path}')
                    else:
                        # Fall back to default
                        self.vlc_instance = vlc.Instance()
                else:
                    # Fall back to default
                    self.vlc_instance = vlc.Instance()
            except Exception as e:
                print(f"Error finding VLC path: {e}")
                self.vlc_instance = vlc.Instance()

            self.player = self.vlc_instance.media_player_new()
            print("VLC initialized successfully")
        except Exception as e:
            print(f"Error initializing VLC: {e}")

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

        try:
            # Reset track finished flag when loading new track
            self._track_finished = False

            # Create a new media
            media = self.vlc_instance.media_new(filepath)

            # Set up the player
            self.player.set_media(media)

            # Get media information
            media.parse()

            # Set media properties
            self.current_file = filepath

            # Get duration from media directly first - more reliable
            duration_ms = media.get_duration()
            if duration_ms <= 0:
                # Fall back to player if media doesn't have duration
                duration_ms = self.player.get_length()

            # Set duration based on what we found
            if duration_ms > 0:
                self.duration = duration_ms / 1000.0
                print(f"Duration detected: {self.duration:.3f} seconds")
            else:
                # If we have a database with the file, get duration from there
                app = App.get_running_app()
                if hasattr(app, 'database'):
                    try:
                        # Try to find the file in the database
                        all_recordings = app.database.get_all_recordings()
                        for rec in all_recordings:
                            if rec[3] == filepath:  # filepath is at index 3
                                self.duration = rec[4]  # duration is at index 4
                                print(f"Using database duration: {self.duration:.3f}s")
                                break
                    except Exception as e:
                        print(f"Error getting duration from database: {e}")

                # If still no duration, use fallback
                if self.duration <= 0:
                    self.duration = 100
                    print("Could not determine duration, using default (100s)")

            # Reset position
            self.current_pos = 0

            # Set flag for compatibility
            self.sound = True

            # Start position updates
            if self.update_event:
                self.update_event.cancel()
            self.update_event = Clock.schedule_interval(self.update_position, 0.1)

            print(f"File loaded successfully. Duration: {self.duration}s")
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
            # Get current state
            state = self.player.get_state()

            # If track has ended, we need to completely reset it
            if state == vlc.State.Ended:
                print("Track ended, restarting from beginning")
                # Stop first to reset the player state
                self.player.stop()
                # Slight delay to ensure internal VLC state is reset
                time.sleep(0.1)
                # Then play will start from the beginning
                self.player.play()
            else:
                # Normal play for non-ended tracks
                self.player.play()

            # Update state
            self._track_finished = False
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
            # Reset finished state
            self._track_finished = False
            print("Stopped playback")
        except Exception as e:
            print(f"Error stopping: {e}")

    def seek(self, position):
        """Seek to a specific position in seconds."""
        if not self.vlc_instance or not self.player:
            return

        try:
            # Reset track finished state when seeking
            self._track_finished = False

            # Convert to milliseconds for VLC
            ms_position = int(position * 1000)

            # Get current state
            state = self.player.get_state()

            # If the track has ended, we need to reset it completely
            if state == vlc.State.Ended:
                print(f"Track ended, seeking to {position}s requires restart")
                # Stop and reset
                self.player.stop()
                time.sleep(0.1)  # Short delay to ensure VLC state is reset
                self.player.play()  # Start playback
                time.sleep(0.1)  # Allow playback to start

                # Then seek to the desired position
                self.player.set_time(ms_position)

                # If we're not actually wanting to play, pause immediately
                if not self.is_playing:
                    self.player.pause()
            else:
                # Normal seek
                self.player.set_time(ms_position)

            # Update our position tracking
            self.current_pos = position
            print(f"Seeking to position: {position}s (Result: Success)")
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
        """Update the current position property."""
        if not self.vlc_instance or not self.player:
            return

        try:
            # Get current time in milliseconds and convert to seconds
            time_ms = self.player.get_time()
            if time_ms >= 0:
                self.current_pos = time_ms / 1000.0

            # Check if we've reached the end
            state = self.player.get_state()

            # Check for end state directly from VLC state
            if state == vlc.State.Ended:
                # Only dispatch event if we haven't already marked this track as finished
                if not self._track_finished:
                    print("Track finished")
                    self.is_playing = False
                    # Do NOT reset current_pos here, keep at the end so we know
                    # self._track_finished = True
                    self.dispatch('on_track_finished')
                    # Mark track as finished, but don't reset position
                    self._track_finished = True
            elif state != vlc.State.Ended and self._track_finished:
                # Reset finished state if track is no longer at the end
                self._track_finished = False
        except Exception as e:
            print(f"Error updating position: {e}")

    def on_track_finished(self, *args):
        """Event handler for track completion."""
        pass


# Create singleton
player = AudioPlayer()
