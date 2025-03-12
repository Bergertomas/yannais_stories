# Replace mediaplayer.py with androidmediaplayer.py when on Android
import os
import sys

# Check if we're on Android
if 'ANDROID_BOOTLOGO' in os.environ:
    # Use Android-specific implementation
    from androidmediaplayer import player
else:
    # Use development implementation
    from mediaplayer import player

# Continue with normal imports
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
# ... rest of your imports ...

# Rest of your application code
# ...

if __name__ == '__main__':
    AudioStoryApp().run()

