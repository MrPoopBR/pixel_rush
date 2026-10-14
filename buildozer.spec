[app]
title = PIXEL RUSH
package.name = bigheadmobile_pixelrush
package.domain = com
source.dir = .
source.include_exts = py,json
source.exclude_dirs = .git,.buildozer,bin,p4a-recipes,__pycache__
version = 3.2.5
android.numeric_version = 2
requirements = python3==3.10.12,hostpython3==3.10.12,pygame-ce
orientation = portrait
fullscreen = 1

# O jogo desenha gráficos e sintetiza áudio no próprio código.
android.permissions = VIBRATE
android.private_storage = True
android.allow_backup = True
android.api = 36
android.minapi = 26
android.ndk_api = 26
android.ndk = 28c
android.archs = arm64-v8a
android.accept_sdk_license = True
android.release_artifact = aab
android.debug_artifact = apk
android.copy_libs = True

p4a.bootstrap = sdl2
p4a.branch = develop
p4a.local_recipes = p4a-recipes

[buildozer]
warn_on_root = 0
