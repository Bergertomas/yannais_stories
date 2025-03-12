from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty
from kivy.event import EventDispatcher
import os


class AudioPlayer(EventDispatcher):
    """Audio player for managing and controlling audio playback."""

    current_pos = NumericProperty(0)
    duration = NumericProperty(0)
    is_playing = BooleanProperty(False)
    current_file = StringProperty("")
    volume = NumericProperty(1.0)
    sound = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        # Register events first
        self.register_event_type('on_track_finished')
        super(AudioPlayer, self).__init__(**kwargs)
        self.update_event = None

    def load(self, filepath):
        """Load an audio file for playback."""
        print(f"Loading file: {filepath}")
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return False

        # Stop current sound if playing
        self.stop()

        # Load new sound
        try:
            self.sound = SoundLoader.load(filepath)
            if self.sound:
                print(f"Sound loaded successfully: {filepath}")
                self.current_file = filepath
                self.duration = self.sound.length
                self.current_pos = 0
                return True
            else:
                print(f"Failed to load sound: {filepath}")
                return False
        except Exception as e:
            print(f"Error loading sound: {e}")
            return False

    def play(self):
        """Play or resume the current audio file."""
        if not self.sound:
            print("No sound loaded")
            return

        try:
            if not self.is_playing:
                print(f"Playing sound, current_pos: {self.current_pos}")
                if self.current_pos > 0 and self.current_pos < self.duration:
                    # Resume from position
                    self.sound.seek(self.current_pos)
                # Start or resume playback
                self.sound.play()
                self.is_playing = True

                # Start update timer
                if self.update_event:
                    self.update_event.cancel()
                self.update_event = Clock.schedule_interval(self.update_position, 0.1)
        except Exception as e:
            print(f"Error playing sound: {e}")

    def stop(self):
        """Stop playback and reset position."""
        if not self.sound:
            return

        try:
            if self.sound.state != 'stop':
                self.sound.stop()
            if self.update_event:
                self.update_event.cancel()
                self.update_event = None
            self.is_playing = False
            self.current_pos = 0
        except Exception as e:
            print(f"Error stopping sound: {e}")

    def pause(self):
        """Pause the current playback."""
        if not self.sound or not self.is_playing:
            return

        try:
            # Get current position first
            self.current_pos = self.sound.get_pos()
            print(f"Pausing at position: {self.current_pos}")

            # Then stop the sound (which preserves the position)
            self.sound.stop()

            # Update state
            self.is_playing = False

            # Cancel update timer
            if self.update_event:
                self.update_event.cancel()
                self.update_event = None
        except Exception as e:
            print(f"Error pausing sound: {e}")

    def seek(self, position):
        """Seek to a specific position in the audio file."""
        if not self.sound:
            print("No sound loaded")
            return

        try:
            if position < 0:
                position = 0
            elif position > self.duration:
                position = self.duration

            print(f"Seeking to position: {position}")
            was_playing = self.is_playing

            # Store the desired position
            self.current_pos = position

            # We need to stop and restart the sound to seek
            if was_playing:
                self.sound.stop()
                self.sound.seek(position)
                self.sound.play()
            else:
                self.sound.seek(position)

        except Exception as e:
            print(f"Error seeking: {e}")

    def set_volume(self, volume):
        """Set the playback volume (0.0 to 1.0)."""
        if not self.sound:
            return

        try:
            volume = max(0.0, min(1.0, volume))
            self.sound.volume = volume
            self.volume = volume
        except Exception as e:
            print(f"Error setting volume: {e}")

    def update_position(self, dt):
        """Update the current position property (called by Clock)."""
        if not self.sound:
            return

        try:
            if self.sound.state == 'play':
                new_pos = self.sound.get_pos()
                # Update current position
                self.current_pos = new_pos

                # Check if we reached the end
                if new_pos >= self.duration:
                    print("Track finished")
                    self.stop()
                    self.dispatch('on_track_finished')
        except Exception as e:
            print(f"Error updating position: {e}")

    def __del__(self):
        """Clean up resources when the object is deleted."""
        self.stop()
        if self.sound:
            self.sound.unload()

    # Event handler - must be implemented
    def on_track_finished(self, *args):
        pass


# Create a singleton instance for global use
player = AudioPlayer()
