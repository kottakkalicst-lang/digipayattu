[app]
title = DigiPayattu
package.name = digipayattu
package.domain = org.jithesh

source.dir = .
source.include_exts = py

version = 0.1

requirements = python3,kivy,sqlite3

orientation = portrait
fullscreen = 1

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
