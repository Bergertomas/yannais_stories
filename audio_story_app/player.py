from kivy.core.audio import SoundLoader


class Player:
    def __init__(self):
        self.current_sound = None
        self.current_position = 0
        self.is_playing = False

    def play(self, audio_path):
        if self.current_sound:
            self.stop()
        self.current_sound = SoundLoader.load(audio_path)
        if self.current_sound:
            self.current_sound.play()
            self.is_playing = True
        else:
            print(f"Error: Could not load audio file {audio_path}")

    def pause(self):
        if self.current_sound and self.is_playing:
            self.current_position = self.current_sound.get_pos()
            self.current_sound.stop()
            self.is_playing = False

    def resume(self):
        if self.current_sound and not self.is_playing:
            self.current_sound.play()
            self.current_sound.seek(self.current_position)
            self.is_playing = True

    def stop(self):
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound = None
            self.current_position = 0
            self.is_playing = False

    def seek(self, position):
        if self.current_sound:
            self.current_sound.seek(position)
            self.current_position = position

    def set_volume(self, volume):
        if self.current_sound:
            self.current_sound.volume = volume
