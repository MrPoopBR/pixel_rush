#!/usr/bin/env python3
"""Regressao offline: encodings deve iniciar mesmo sem zlib dinamico.

Simula a receita p4a criando um stdlib comprimido e exige que a receita local
transforme o ZIP para STORED mantendo todos os bytes e os metadados.
"""
import importlib.util
import marshal
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED


def main():
    sample = {
        'encodings/__init__.pyc': b'\xcb\r\r\n' + bytes(12) + b'ENCODINGS',
        'encodings/utf_8.pyc': b'\xcb\r\r\n' + bytes(12) + b'UTF8',
        'codecs.pyc': b'\xcb\r\r\n' + bytes(12) + b'CODECS',
        'example/extra.pyc': b'\xcb\r\r\n' + bytes(12) + b'EXTRA',
    }

    class FakeUpstreamPython3Recipe:
        def create_python_bundle(self, dirn, arch):
            with ZipFile(Path(dirn) / 'stdlib.zip', 'w', compression=ZIP_DEFLATED) as z:
                for name, data in sample.items():
                    z.writestr(name, data)
            return 'UPSTREAM_RESULT'

    fake_pkg = types.ModuleType('pythonforandroid')
    fake_recipes = types.ModuleType('pythonforandroid.recipes')
    fake_python3 = types.ModuleType('pythonforandroid.recipes.python3')
    fake_python3.Python3Recipe = FakeUpstreamPython3Recipe
    orig = {key: sys.modules.get(key) for key in
            ('pythonforandroid', 'pythonforandroid.recipes', 'pythonforandroid.recipes.python3')}
    try:
        sys.modules['pythonforandroid'] = fake_pkg
        sys.modules['pythonforandroid.recipes'] = fake_recipes
        sys.modules['pythonforandroid.recipes.python3'] = fake_python3
        local_recipe = runpy.run_path('p4a-recipes/python3/__init__.py')['recipe']
        assert local_recipe.version == '3.12.12'
        with tempfile.TemporaryDirectory() as td:
            with patch.object(type(local_recipe), '_link_cpython_extensions', return_value=56) as link:
                assert local_recipe.create_python_bundle(td, None) == 'UPSTREAM_RESULT'
                link.assert_called_once_with(Path(td) / 'modules')
            path = Path(td) / 'stdlib.zip'
            with ZipFile(path) as z:
                assert len(z.infolist()) == len(sample)
                assert all(info.compress_type == ZIP_STORED for info in z.infolist())
                assert {name: z.read(name) for name in z.namelist()} == sample
                assert z.testzip() is None
    finally:
        for key, item in orig.items():
            if item is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = item

    # Testa a dependencia de DEFLATE em zlib sem precisar de Android.
    with tempfile.TemporaryDirectory() as td:
        bytecode = importlib.util.MAGIC_NUMBER + bytes(12) + marshal.dumps(
            compile('READY = True\n', 'bootmodule.py', 'exec'))
        for method, name, expected in ((ZIP_DEFLATED, 'deflate.zip', False),
                                       (ZIP_STORED, 'stored.zip', True)):
            path = Path(td) / name
            with ZipFile(path, 'w', compression=method) as z:
                z.writestr('bootmodule.pyc', bytecode)
            script = (
                "import sys, zipimport; "
                "sys.modules['zlib']=None; "
                "sys.path[:]=[%r]; "
                "zipimport.zipimporter(%r).get_code('bootmodule')" %
                (str(path), str(path))
            )
            proc = subprocess.run([sys.executable, '-I', '-S', '-E', '-c', script],
                                  capture_output=True, text=True)
            if expected and proc.returncode:
                raise AssertionError('ZIP STORED falhou sem zlib: ' + proc.stderr)
            if not expected and (
                proc.returncode == 0 or 'zlib not available' not in proc.stderr
            ):
                raise AssertionError('ZIP DEFLATED nao reproduziu falha de zlib')
    print('APROVADO: receita local, ZIP STORED, CRC, codecs e teste de zlib isolado')


if __name__ == '__main__':
    main()
