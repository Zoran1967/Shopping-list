[app]
title = Soping Lista
package.name = sopinglista
package.domain = org.teodora
source.dir = app
source.include_exts = py,pyc,kv,png,jpg,txt
version = 0.1
requirements = python3,kivy==2.3.1,sqlite3,fpdf2,camera4kivy,filetype,requests,certifi,chardet,idna,urllib3,six
icon.filename = %(source.dir)s/icon.png
orientation = portrait
fullscreen = 0
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,INTERNET
android.api = 34
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
