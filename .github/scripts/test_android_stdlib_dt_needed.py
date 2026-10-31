#!/usr/bin/env python3
"""Teste isolado do contrato DT_NEEDED dos modulos CPython/Android ARM64."""
from pathlib import Path
from unittest.mock import patch
import runpy
import sys
import tempfile
import types


def main():
    class FakeUpstream:
        pass

    keys = ('pythonforandroid', 'pythonforandroid.recipes', 'pythonforandroid.recipes.python3')
    old = {k: sys.modules.get(k) for k in keys}
    root = types.ModuleType(keys[0])
    recipes = types.ModuleType(keys[1])
    mod = types.ModuleType(keys[2]); mod.Python3Recipe = FakeUpstream
    try:
        sys.modules.update(zip(keys, (root, recipes, mod)))
        clazz = runpy.run_path('p4a-recipes/python3/__init__.py')['PixelRushPython3Recipe']
        with tempfile.TemporaryDirectory(prefix='pixelrush-needed-test-') as td:
            d = Path(td)
            modules = ['math', 'zlib', '_ctypes', '_ssl', '_json']
            for name in modules:
                (d / (name + '.cpython-312.so')).write_bytes(b'\x7fELF')
            # Extension from other package or different Python ABI is ignored.
            (d / 'pygame.base.so').write_bytes(b'\x7fELF')
            (d / 'other.cpython-313.so').write_bytes(b'\x7fELF')
            needed = {str(p): [] for p in d.glob('*.cpython-312.so')}
            wanted = 'libpython3.12.so'
            commands = []

            def fake_run(args, **kwargs):
                assert kwargs.get('check') and kwargs.get('capture_output')
                assert kwargs.get('text')
                commands.append(args)
                p = args[-1]
                if '--print-needed' in args:
                    return types.SimpleNamespace(stdout='\n'.join(needed[p]))
                assert args[1:5] == ['--page-size', '16384', '--add-needed', wanted]
                needed[p].append(wanted)
                return types.SimpleNamespace(stdout='')

            with patch('shutil.which', return_value=None):
                # The recipe imports `which` directly, patch where it is used.
                with patch.dict(clazz._link_cpython_extensions.__globals__, {'which': lambda s: None}):
                    try:
                        clazz._link_cpython_extensions(d)
                    except RuntimeError as exc:
                        assert 'patchelf nao encontrado' in str(exc)
                    else:
                        raise AssertionError('sem patchelf nao interrompeu')

            with patch.dict(clazz._link_cpython_extensions.__globals__, {
                'which': lambda x: '/usr/bin/patchelf', 'run': fake_run}):
                assert clazz._link_cpython_extensions(d) == 5
                assert all(v == [wanted] for v in needed.values())
                assert len([c for c in commands if '--add-needed' in c]) == 5
                commands.clear()
                assert clazz._link_cpython_extensions(d) == 5
                assert not [c for c in commands if '--add-needed' in c]
                (d / '_ssl.cpython-312.so').unlink()
                try:
                    clazz._link_cpython_extensions(d)
                except RuntimeError as exc:
                    assert '_ssl' in str(exc)
                else:
                    raise AssertionError('extensao critica ausente nao detectada')
    finally:
        for k, mod in old.items():
            if mod is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = mod
    print('APROVADO: DT_NEEDED, patchelf, 16 KiB, repeticao idempotente, falhas seguras')


if __name__ == '__main__':
    main()
