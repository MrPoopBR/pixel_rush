# -*- coding: utf-8 -*-
"""QA789: modularizacao real de mundo/render, imports antigos e zero duplicacao."""
import importlib
import json
import os
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame

class ModulosMigradosQA789(unittest.TestCase):
    def test_imports_legacy_e_modulares_mesma_instancia(self):
        manifest=json.loads((ROOT/"docs/arquitetura/MANIFESTO_MODULOS_v327789.json").read_text("utf8"))
        self.assertEqual(len(manifest["modulos"]),25)
        pygame.init()
        pygame.display.set_mode((450,800))
        for item in manifest["modulos"]:
            old=item["antigo"][:-3]
            new=item["novo"][:-3].replace("/",".")
            with self.subTest(old=old):
                orig=importlib.import_module(old)
                canon=importlib.import_module(new)
                self.assertIs(orig,canon)
                self.assertIs(sys.modules[old],sys.modules[new])
                self.assertEqual(Path(orig.__file__).resolve(),(ROOT/item["novo"]).resolve())
                self.assertTrue(callable(getattr(orig,"__getattribute__",None)))
        pygame.quit()

    def test_chain_cidade_em_uso_real_qa785_786_787(self):
        pygame.init()
        pygame.display.set_mode((450,800))
        from pixelrush_qa_city_bootstrap_v327759 import instalar as boot
        from pixelrush_qa_city_scaled_budget_v327785 import instalar as budget
        from pixelrush_qa_city_opaque_overdraw_v327786 import instalar as overdraw
        from pixelrush_qa_city_technical_cover_v327787 import instalar as tech
        from pixelrush_city2_v3125 import CityPilotScene
        from src.pixelrush.world.city.v3125 import CityPilotScene as Canon
        self.assertIs(CityPilotScene,Canon)
        old=os.environ.get("PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW")
        oldtech=os.environ.get("PIXELRUSH_QA_CITY_TECH_COVER")
        try:
            boot()
            budget()
            os.environ["PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW"]="1"
            os.environ["PIXELRUSH_QA_CITY_TECH_COVER"]="1"
            overdraw()
            tech()
            scene=CityPilotScene()
            self.assertEqual(scene._scaled_limit,20)
            self.assertIn("geometry",scene._qa_tech_cutoffs)
            self.assertIn("normal",scene._qa_opaque_maps_srcs)
            self.assertTrue(scene.layers)
        finally:
            from pixelrush_qa_city_technical_cover_v327787 import restaurar_para_teste as stop_tech
            from pixelrush_qa_city_opaque_overdraw_v327786 import restaurar_para_teste as stop_overdraw
            from pixelrush_qa_city_scaled_budget_v327785 import restaurar_para_teste as stop_budget
            from pixelrush_qa_city_bootstrap_v327759 import restaurar_para_teste as stop_boot
            stop_tech();stop_overdraw();stop_budget();stop_boot()
            if old is None:os.environ.pop("PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW",None)
            else:os.environ["PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW"]=old
            if oldtech is None:os.environ.pop("PIXELRUSH_QA_CITY_TECH_COVER",None)
            else:os.environ["PIXELRUSH_QA_CITY_TECH_COVER"]=oldtech
            pygame.quit()

    def test_nova_arquitetura_nao_usa_import_hook_por_quadro(self):
        for path in ("main.py","JOGAR.py","pixelrush_qa_render_v327729.py"):
            self.assertTrue((ROOT/path).is_file())
        self.assertFalse((ROOT/"src/pixelrush/world/city/v3118.py").exists(),
                         "SHA preflight antigo impede migracao cega do 3118")
        self.assertFalse((ROOT/"src/pixelrush/world/city/v3122.py").exists())
        self.assertTrue((ROOT/"src/pixelrush/performance/city/cache_budget.py").is_file())
        self.assertTrue((ROOT/"docs/arquitetura/QA_RAIZ_PROTEGIDA_v327789.md").is_file())

    def test_docs_relocalizados_sem_exclusao_de_historico(self):
        m=json.loads((ROOT/"docs/arquitetura/MANIFESTO_DOCUMENTOS_v327789.json").read_text("utf8"))
        self.assertEqual(len(m["arquivos"]),3)
        for d in m["arquivos"]:
            self.assertFalse((ROOT/d["antigo"]).exists())
            self.assertTrue((ROOT/d["novo"]).is_file())

if __name__=="__main__":
    unittest.main(verbosity=2)
