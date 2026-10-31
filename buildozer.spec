[app]
title = PIXEL RUSH
# Identidade original do repositório preservada. Confirmar na Play Console antes de publicar.
package.name = bigheadmobile_pixelrush
package.domain = com
source.dir = .
# Recursos usados pela candidata Android v3.277.11 (não somente arquivos Python).
source.include_exts = py,json,png,ttf,txt,atlas,pbuf,tiles,rgbaz,pcmz
source.exclude_dirs = .git,.buildozer,bin,p4a-recipes,__pycache__,ferramentas,QA_BUILD_LOCAL
version = 3.277.11
# Valor de TESTE: confirmar versionCode em Google Play antes de assinar/publicar.
android.numeric_version = 327711
# p4a/develop usa NumPy 2.3.0 (Python >=3.11). Python e hostpython devem coincidir.
requirements = python3==3.12.12,hostpython3==3.12.12,pygame-ce,numpy,pyjnius,plyer
orientation = portrait
fullscreen = 1
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
# Instável entre commits: fixar SHA de p4a após um primeiro build validado.
p4a.branch = develop
p4a.local_recipes = p4a-recipes

[buildozer]
warn_on_root = 0
