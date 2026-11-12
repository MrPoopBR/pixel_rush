#!/usr/bin/env python3
"""R155: aplicar fix minimo sobre fonte R154 EXATA ja transferida ao GitHub."""
from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(sys.argv[1]).resolve()
checks = {
    "src/pixelrush/platform/legacy_imports_v327797.py": (
        "05a448eff1d9cf30227961bed06280390c00e99831cc68332e396041fb5ba00e",
        "eb8b1875e8ab234dec108deb4255ffbb49129edb67333d79119be69322a39146"),
    "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py": (
        "b3f6b0c593fb778c25f19be53b9c6a2133e25296aa1bf3c6a24388aa424b795a",
        "ae41876a127ef5af26ec4163576c3a720c8ad2cbebf41c62b7b46c489b2c9976"),
    "buildozer.spec": (
        "ce1fc45a094e86c865774bb689f97b693c5c2056b63e1ca1629bd0b0de1755ec",
        "3fcdbe952068bc585b3c2a509e4440e4e6880323814a4191dcaac79e6f8e286b"),
    "VERSAO_ATUAL.txt": (
        "b74628d49ad83a8c395e8316e96e4f12a44bf420ef71dfb50b8be4e901ba90a1",
        "7176e554214fe0d14b3d774b1a0d2a8f6847b4034d33b66adf07b5a889afe1e6"),
}

def sha(content):
    return hashlib.sha256(content).hexdigest()

for filename, (old, new) in checks.items():
    f = ROOT / filename
    if not f.is_file() or sha(f.read_bytes()) != old:
        raise SystemExit("Fonte R154 alterada! Recusando patch: " + filename)

file = ROOT / "src/pixelrush/platform/legacy_imports_v327797.py"
s = file.read_text(encoding="utf8")
s = s.replace("class _LegacyFinder(importlib.abc.MetaPathFinder):", '''class _LegacyBytecodeLoader(importlib.machinery.SourcelessFileLoader):
    """R155: p4a distribui .pyc ao lado do modulo e remove o .py.

    Carrega bytecode existente sem recompilacao no boot do Android e mantem
    o __file__ historico virtual como no loader original.
    """
    def exec_module(self, module):
        module.__file__ = str(_ROOT / (module.__name__ + '.py'))
        super().exec_module(module)


class _LegacyFinder(importlib.abc.MetaPathFinder):''')
old = '''        real_file = _ROOT / relative
        loader = _LegacySourceLoader(fullname, str(real_file))
        return importlib.util.spec_from_file_location(fullname, real_file, loader=loader)'''
new = '''        real_file = _ROOT / relative
        if real_file.is_file():
            loader = _LegacySourceLoader(fullname, str(real_file))
            origin = real_file
        else:
            # python-for-android converte .py -> .pyc no mesmo diretorio.
            # SourceFileLoader nao encontra esse bytecode quando o .py foi removido.
            bytecode = real_file.with_suffix('.pyc')
            if not bytecode.is_file():
                return None
            loader = _LegacyBytecodeLoader(fullname, str(bytecode))
            origin = bytecode
        return importlib.util.spec_from_file_location(fullname, origin, loader=loader)'''
if old not in s:
    raise SystemExit("Ponto de troca loader nao encontrado")
file.write_text(s.replace(old, new), encoding="utf8")

engine = ROOT / "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py"
s = engine.read_text(encoding="utf8")
old = 'VERSAO = "v3.279.06-ANDROID-RC"'
if s.count(old) != 1:
    raise SystemExit("Versao R154 inesperada")
engine.write_text(s.replace(old, 'VERSAO = "v3.279.07-ANDROID-RC"'), encoding="utf8")

spec = ROOT / "buildozer.spec"
s = spec.read_text(encoding="utf8")
if not re.search(r'^version = 3\.279\.06$', s, re.M) or not re.search(r'^android.numeric_version = 327906$',s,re.M):
    raise SystemExit("Buildozer R154 inesperado")
s = re.sub(r'^version = 3\.279\.06$', "version = 3.279.07", s, flags=re.M)
s = re.sub(r'^android.numeric_version = 327906$', "android.numeric_version = 327907", s, flags=re.M)
spec.write_text(s, encoding="utf8")

(ROOT / "VERSAO_ATUAL.txt").write_text(
    "PIXEL RUSH v3.279.07-ANDROID-RC — R155: correção de inicialização Android com importador legado compatível com bytecode .pyc do python-for-android. Fallback .py original preservado; sem alterações de física, RGBA/RNG, jogabilidade, assets ou áudio. Package ID com.bigheadmobile_pixelrush preservado. APK Android novo requer testes em aparelho e emulador.\n",
    encoding="utf8")

for filename, (old, new) in checks.items():
    if sha((ROOT / filename).read_bytes()) != new:
        raise SystemExit("R155 divergiu do ZIP local oficial: " + filename)
print("R155 aplicado de forma exata aos quatro arquivos.", "versionCode 327907, package com.bigheadmobile_pixelrush")
