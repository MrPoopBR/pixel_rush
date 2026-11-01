#!/usr/bin/env python3
"""Regressao do encaminhamento de patches da receita python3 Android RC.

Garante que o overlay local use os patches da receita oficial do p4a,
que arquivos ausentes sejam detectados e que metodos herdados permaneçam
intactos. Nao requer NDK ou modifica codigo de jogo.
"""
from pathlib import Path
import runpy
import sys
import tempfile
import types


PATCHES_PY312 = (
    'patches/pyconfig_detection.patch',
    'patches/reproducible-buildinfo.diff',
    'patches/cpython-311-ctypes-find-library.patch',
    'patches/py3.8.1_fix_cortex_a8.patch',
)


def main():
    with tempfile.TemporaryDirectory(prefix='pixelrush-p4a-patches-') as td:
        upstream_dir = Path(td) / 'p4a' / 'pythonforandroid' / 'recipes' / 'python3'
        upstream_dir.mkdir(parents=True)
        (upstream_dir / '__init__.py').write_text('# upstream fake\n')
        for name in PATCHES_PY312:
            target = upstream_dir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('patch de teste: ' + name)

        paths = []

        class FakeUpstreamPython3Recipe:
            def apply_patch(self, filename, arch, build_dir=None):
                # Modelo fiel: Receita base faz join(local_dir, filename).
                from os.path import join
                candidate = Path(join('p4a-recipes/python3', filename))
                if not candidate.is_file():
                    raise FileNotFoundError(str(candidate))
                paths.append((candidate.resolve(), arch, build_dir))
                return 'APLICADO'

        FakeUpstreamPython3Recipe.__module__ = 'pythonforandroid.recipes.python3'
        root = types.ModuleType('pythonforandroid')
        recipes = types.ModuleType('pythonforandroid.recipes')
        upstream = types.ModuleType('pythonforandroid.recipes.python3')
        upstream.__file__ = str(upstream_dir / '__init__.py')
        upstream.Python3Recipe = FakeUpstreamPython3Recipe
        keys = ('pythonforandroid', 'pythonforandroid.recipes',
                'pythonforandroid.recipes.python3')
        saved = {name: sys.modules.get(name) for name in keys}
        try:
            for name, mod in zip(keys, (root, recipes, upstream)):
                sys.modules[name] = mod
            recipe = runpy.run_path('p4a-recipes/python3/__init__.py')['recipe']
            assert recipe.version == '3.12.12'

            for name in PATCHES_PY312:
                result = recipe.apply_patch(name, 'arm64-v8a', build_dir='/build/py312')
                assert result == 'APLICADO'
            assert len(paths) == len(PATCHES_PY312)
            assert all(actual == (upstream_dir / name).resolve()
                       for (actual, arch, dest), name in zip(paths, PATCHES_PY312))
            assert all(arch == 'arm64-v8a' and dest == '/build/py312'
                       for _, arch, dest in paths)

            # Arquivo inexistente: interrompe com erro claro antes de rodar patch.
            missing = upstream_dir / PATCHES_PY312[0]
            missing.unlink()
            try:
                recipe.apply_patch(PATCHES_PY312[0], 'arm64-v8a')
            except FileNotFoundError as exc:
                assert str(missing) in str(exc)
            else:
                raise AssertionError('patch ausente nao foi detectado')
            assert len(paths) == len(PATCHES_PY312)

            # Nao desvia nomes que nao sao patches oficiais.
            plain = Path('p4a-recipes/python3/probe.txt')
            try:
                plain.write_text('temporario')
                assert recipe.apply_patch('probe.txt', 'arm64-v8a') == 'APLICADO'
                assert paths[-1][0] == plain.resolve()
            finally:
                plain.unlink(missing_ok=True)
        finally:
            for name, mod in saved.items():
                if mod is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = mod

    print('APROVADO: patches oficiais presentes, ausentes, caminho absoluto e heranca')


if __name__ == '__main__':
    main()
