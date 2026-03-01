[app]
title = Clash AI Trainer
package.name = clashai
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1

requirements = python3, kivy, pyjnius, opencv-python-headless, requests, urllib3, certifi, idna, charset-normalizer

android.permissions = SYSTEM_ALERT_WINDOW, FOREGROUND_SERVICE, FOREGROUND_SERVICE_MEDIA_PROJECTION, INTERNET

android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b

android.archs = arm64-v8a, armeabi-v7a

# (str) Foreground service name
# android.services = clashservice:service.py

[buildozer]
log_level = 2
warn_on_root = 1
