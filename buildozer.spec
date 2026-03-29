[app]
title = Ultimate Mega AI Commander
package.name = megacommander
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

requirements = python3, kivy, pyjnius, opencv-python-headless, requests, urllib3, certifi, idna, charset-normalizer

# Android 14 (API 34) specific permissions and service rules
android.permissions = SYSTEM_ALERT_WINDOW, FOREGROUND_SERVICE, FOREGROUND_SERVICE_MEDIA_PROJECTION, INTERNET, POST_NOTIFICATIONS, QUERY_ALL_PACKAGES

# Foreground service type (Required for Android 14 API 34+)
android.foreground_service_type = mediaProjection

android.api = 34
android.minapi = 26
android.sdk = 34
android.ndk = 25b

android.archs = arm64-v8a, armeabi-v7a

# Foreground service name
android.services = aicommander:service.py

# Allow the app to query for installed packages to launch game
# android.manifest.queries = <package android:name="com.supercell.clashroyale" />

[buildozer]
log_level = 2
warn_on_root = 1
