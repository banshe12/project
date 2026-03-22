[app]
title = OSINT Deep Scan
package.name = osint_tool
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,aiohttp,certifi,idna,charset-normalizer,multidict,yarl,frozenlist,aiosignal,attrs

orientation = portrait
fullscreen = 1

# Android permissions
android.permissions = INTERNET

# Android API level
android.api = 33
android.minapi = 21

[buildozer]
log_level = 2
warn_on_root = 1
