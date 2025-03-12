[app]
title = Audio Story App
package.name = audiostoryapp
package.domain = org.yourdomain
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,mp3
version = 1.0

requirements = python3,kivy,pyjnius

# Indicate that we need the MediaPlayer feature
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 29
android.minapi = 21
android.ndk = 21b
android.arch = armeabi-v7a
android.allow_backup = True

# p4a branch to use
p4a.branch = master

# Android specific commands
android.add_src = androidmediaplayer.py

[buildozer]
log_level = 2
warn_on_root = 1
