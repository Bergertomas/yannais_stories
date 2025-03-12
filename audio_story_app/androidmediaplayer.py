from jnius import autoclass
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.event import EventDispatcher
from kivy.clock import Clock
import os

# Android Java classes
MediaPlayer = autoclass('android.media.MediaPlayer')
Uri = autoclass('android.net.Uri')
Context = autoclass('android.content.Context')
File = autoclass('java.io.File')
PythonActivity = autoclass('org.kivy.android.PythonActivity')


class AudioPlayer(EventDispatcher):
    """Audio player using Android's native MediaPlayer."""

    current_pos = NumericProperty(0)
    duration = NumericProperty(100)
    is_playing = BooleanProperty(False)
    current_file = StringProperty("")
    volume = NumericProperty(1.0)

    def __init__(self, **kwargs):
        self.register_event_type('on_track_finished')
        super(AudioPlayer, self).__init__(**kwargs)
        self.player = MediaPlayer()
        self.sound = True  # For compatibility
        self.update_event = None

        # Set up completion listener
        self.player.setOnCompletionListener(MediaPlayer.OnCompletionListener({
            'onCompletion': self._on_completion
        }))

    def _on_completion(self, mp):
        """Handle playback completion."""
        self.is_playing = False
        self.current_pos = 0
        Clock.schedule_once(lambda dt: self.dispatch('on_track_finished'), 0)

    def load(self, filepath):
        """Load an audio file."""
        print(f"Loading file: {filepath}")

        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return False

        # Stop and reset any current playback
        self.stop()
        self.player.reset()

        try:
            # Convert filepath to Android Uri
            file_obj = File(filepath)
            uri = Uri.fromFile(file_obj)

            # Set up the media player
            context = PythonActivity.mActivity
            self.player.setDataSource(context, uri)
            self.player.prepare()

            # Get duration in milliseconds and convert to seconds
            self.duration = self.player.getDuration() / 1000.0
            self.current_file = filepath
            self.current_pos = 0

            # Start position updates
            if self.update_event:
                self.update_event.cancel()
            self.update_event = Clock.schedule_interval(self.update_position, 0.1)

            print(f"File loaded successfully. Duration: {self.duration}s")
            return True
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False

    def play(self):
        """Play or resume audio."""
        if not self.player:
            return

        try:
            self.player.start()
            self.is_playing = True
            print("Playback started")
        except Exception as e:
            print(f"Error playing: {e}")

    def pause(self):
        """Pause playback."""
        if not self.player or not self.is_playing:
            return

        try:
            self.player.pause()
            self.is_playing = False
            print("Playback paused")
        except Exception as e:
            print(f"Error pausing: {e}")

    def stop(self):
        """Stop playback and reset position."""
        if not self.player:
            return

        try:
            self.player.stop()
            self.is_playing = False
            self.current_pos = 0
            print("Playback stopped")
        except Exception as e:
            print(f"Error stopping: {e}")

    def seek(self, position):
        """Seek to a specific position."""
        if not self.player:
            return

        try:
            # Convert to milliseconds for Android
            pos_ms = int(position * 1000)
            self.player.seekTo(pos_ms)
            self.current_pos = position
            print(f"Seeked to position: {position}s")
        except Exception as e:
            print(f"Error seeking: {e}")

    def set_volume(self, volume):
        """Set playback volume."""
        if not self.player:
            return

        try:
            # Android MediaPlayer uses left/right volume
            self.player.setVolume(volume, volume)
            self.volume = volume
            print(f"Volume set to: {volume}")
        except Exception as e:
            print(f"Error setting volume: {e}")

    def update_position(self, dt):
        """Update current position from the player."""
        if not self.player:
            return

        try:
            if self.is_playing:
                # Get position in milliseconds, convert to seconds
                pos_ms = self.player.getCurrentPosition()
                self.current_pos = pos_ms / 1000.0
        except Exception as e:
            print(f"Error updating position: {e}")

    def __del__(self):
        """Clean up resources when the object is deleted."""
        if self.player:
            self.player.release()

    def on_track_finished(self, *args):
        """Event handler for track completion."""
        pass


# Create singleton
player = AudioPlayer()
