[app]
title = NIFTY AI Scanner
package.name = niftyaiscanner
package.domain = com.niftyai
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,html
version = 0.1.0
requirements = python3,kivy,requests,urllib3,idna,charset-normalizer,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 34
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
