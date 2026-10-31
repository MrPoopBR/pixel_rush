"""Python 3.12 Android RC: remover dependencia circular de zlib no boot.

O zipimport precisa do modulo zlib para descompactar ZIP_DEFLATED. Durante
Py_InitializeFromConfig, encodings e codecs precisam estar disponiveis antes
que as extensoes nativas possam ser importadas com confianca. Esta receita
preserva a compilacao Python 3.12 original do p4a e altera APENAS a forma de
armazenamento de stdlib.zip de DEFLATED para STORED.
"""
from os import replace
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED

from pythonforandroid.recipes.python3 import Python3Recipe as UpstreamPython3Recipe


REQUIRED_BOOT_MODULES = (
    'encodings/__init__.pyc', 'encodings/utf_8.pyc', 'codecs.pyc'
)


class PixelRushPython3Recipe(UpstreamPython3Recipe):
    name = 'python3'
    version = '3.12.12'

    def create_python_bundle(self, dirn, arch):
        result = super().create_python_bundle(dirn, arch)
        stdlib = Path(dirn) / 'stdlib.zip'
        temporary = stdlib.with_name('stdlib-pixelrush-stored.tmp')
        if not stdlib.is_file():
            raise RuntimeError('python3: stdlib.zip nao foi gerado pelo p4a')
        try:
            with ZipFile(stdlib, 'r') as source, ZipFile(
                temporary, 'w', compression=ZIP_STORED, allowZip64=True
            ) as target:
                entries = source.infolist()
                if not entries:
                    raise RuntimeError('python3: stdlib.zip vazio')
                names = {item.filename for item in entries}
                missing = set(REQUIRED_BOOT_MODULES) - names
                if missing:
                    raise RuntimeError(f'python3: codecs ausentes: {sorted(missing)}')
                for entry in entries:
                    content = source.read(entry)
                    # Mantem metadados, timestamps e CRC do arquivo original.
                    entry.compress_type = ZIP_STORED
                    target.writestr(entry, content)
            with ZipFile(temporary, 'r') as check:
                if check.testzip() is not None:
                    raise RuntimeError('python3: stdlib STORED com CRC invalido')
                if any(item.compress_type != ZIP_STORED for item in check.infolist()):
                    raise RuntimeError('python3: ZIP_DEFLATED persistiu no stdlib')
                for name in REQUIRED_BOOT_MODULES:
                    if check.read(name)[:4] != b'\xcb\r\r\n':
                        raise RuntimeError(f'python3: magic de bytecode 3.12 invalido: {name}')
            replace(temporary, stdlib)
        finally:
            temporary.unlink(missing_ok=True)
        return result


recipe = PixelRushPython3Recipe()
