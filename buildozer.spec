[app]
title = نظام بطاقات الطلاب - جامعة المغتربين
package.name = studentcards
package.domain = org.amughtaribeen
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,kv,txt
version = 1.0
requirements = python3,kivy,plyer
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 23
android.archs = arm64-v8a,armeabi-v7a
android.permissions = READ_MEDIA_IMAGES,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
