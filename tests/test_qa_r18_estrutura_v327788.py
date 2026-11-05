# -*- coding: utf-8 -*-
"""QA788: codigo real da Cidade esta em src; imports antigos continuam identicos."""
import ast
import importlib
import os
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame

MODULES={
 "pixelrush_qa_city_scaled_budget_v327785":"src.pixelrush.performance.city.cache_budget",
 "pixelrush_qa_city_opaque_overdraw_v327786":"src.pixelrush.performance.city.opaque_overdraw",
 "pixelrush_qa_city_technical_cover_v327787":"src.pixelrush.performance.city.technical_maps",
}

class EstruturaQA788(unittest.TestCase):
 def test_legado_e_canonico_sao_a_mesma_instancia(self):
    for legacy,new in MODULES.items():
      a=importlib.import_module(legacy)
      b=importlib.import_module(new)
      self.assertIs(a,b,legacy)
      self.assertEqual(a.__file__,b.__file__)
      self.assertTrue(Path(a.__file__).is_file())
      self.assertTrue(str(a.__file__).endswith(".py"))
      self.assertIn("src/pixelrush/performance/city",str(a.__file__).replace("\\","/"))

 def test_imports_privados_e_rollback_qa785_qa786_qa787(self):
    cache=importlib.import_module("pixelrush_qa_city_scaled_budget_v327785")
    opaque=importlib.import_module("pixelrush_qa_city_opaque_overdraw_v327786")
    tech=importlib.import_module("pixelrush_qa_city_technical_cover_v327787")
    self.assertTrue(callable(cache.instalar))
    self.assertTrue(callable(opaque.instalar))
    self.assertTrue(callable(tech._audit_scene))
    self.assertIs(opaque._STATS,
                  importlib.import_module(MODULES[
                  "pixelrush_qa_city_opaque_overdraw_v327786"])._STATS)
    self.assertIsNone(cache._ORIGINAL)
    self.assertFalse(cache.diagnostico()["instalado"])
    self.assertFalse(opaque.diagnostico()["instalado"])
    self.assertFalse(tech.diagnostico()["instalado"])

 def test_entrypoint_alternativo_nao_executa_o_jogo_ao_importar(self):
    a=importlib.import_module("src.main")
    b=importlib.import_module("src.pixelrush.game")
    self.assertIs(a.iniciar_desktop,b.iniciar_desktop)
    self.assertEqual((ROOT/"JOGAR.py").is_file(),True)
    self.assertIsNotNone(ast.parse((ROOT/"src/main.py").read_text("utf8")))

 def test_arquivos_antigos_sem_blobs_duplicados(self):
    from tools.auditar_estrutura_v327788 import diagnostico
    info=diagnostico()
    self.assertFalse(info["erros"],info["erros"])
    self.assertEqual(info["arquivos_arquivados_integridade_ok"],
                     info["arquivos_manifesto"])
    self.assertGreaterEqual(info["arquivos_manifesto"],70)
    self.assertEqual(info["modulos_qa_migrados"],3)
    self.assertTrue(info["main_android_preservado"])

if __name__=="__main__":
 unittest.main(verbosity=2)
