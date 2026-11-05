# -*- coding: utf-8 -*-
"""R23: movimentação em massa, SHA idêntico e imports sem perda de identidade."""
import importlib
import json
import os
import pathlib
import subprocess
import sys
import unittest
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
pygame.init()
pygame.display.set_mode((450,800))
DOC=ROOT/"docs/arquitetura/MANIFESTO_R23_MIGRACAO_v327793.json"
M=json.loads(DOC.read_text("utf8"))

class TesteMigracoes(unittest.TestCase):
    def test_42_modulos_mesmos_bytes_e_imports(self):
        self.assertEqual(len(M["migrated"]),42)
        for entry in M["migrated"]:
            old,new=entry["legacy"],entry["canonical"]
            with self.subTest(old=old):
                before=subprocess.check_output(["git","show",M["base_commit"]+":"+old],cwd=ROOT)
                self.assertEqual(before,(ROOT/new).read_bytes(),old)
                wrapper=(ROOT/old).read_text("utf8")
                self.assertIn("_sys.modules[__name__]",wrapper)
                self.assertIn("import_module(",wrapper)
                original=importlib.import_module(old[:-3])
                canonical=importlib.import_module(new[:-3].replace("/","."))
                self.assertIs(original,canonical)
                self.assertEqual(pathlib.Path(canonical.__file__).resolve(),(ROOT/new).resolve())
                self.assertIs(sys.modules[old[:-3]],canonical)

    def test_candidatos_risco_preservados_na_raiz(self):
        # Estes dependem de caminhos reais para atlas/profiler ou são entrypoints.
        for filename in ("pixelrush_inimigos_v3221.py","pixelrush_profiler_v3204.py",
                         "pixelrush_avisos_raros_i18n_v3247.py","main.py","JOGAR.py"):
            self.assertTrue((ROOT/filename).is_file())
        self.assertEqual(M["root_python_files_removed"],0)

if __name__=="__main__":
    unittest.main(verbosity=2)
