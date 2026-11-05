# -*- coding: utf-8 -*-
"""QA790: imports, funcoes do motor e prototipos historicos sem regresao."""
import ast
import datetime
import importlib
import json
import os
import pathlib
import random
import subprocess
import sys
import unittest
from types import SimpleNamespace

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
import pygame

BASE="c968515568f02375565fe132ba35c1987bd88df2"
ENGINE="PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py"

def original_engine():
    return subprocess.check_output(["git","show",BASE+":"+ENGINE],
                                   cwd=ROOT).decode("utf8")

class QA790ModularizarMotor(unittest.TestCase):
    def test_dez_funcoes_motor_mesmo_ast_e_import_sem_wrappers(self):
        report=json.loads((ROOT/"docs/arquitetura/MANIFESTO_FUNCOES_MOTOR_v327790.json").read_text("utf8"))
        old=ast.parse(original_engine())
        new=ast.parse((ROOT/ENGINE).read_text("utf8"))
        self.assertEqual(len(report["funcoes"]),10)
        for row in report["funcoes"]:
            name,canon=row["nome"],row["destino"]
            oldFns=[x for x in old.body if isinstance(x,ast.FunctionDef) and x.name==name]
            self.assertEqual(len(oldFns),1,name)
            code=ast.parse((ROOT/canon).read_text("utf8"))
            newFns=[x for x in code.body if isinstance(x,ast.FunctionDef) and x.name==name]
            self.assertEqual(len(newFns),1,name)
            self.assertEqual(ast.dump(oldFns[0],include_attributes=False),
                             ast.dump(newFns[0],include_attributes=False),name)
            self.assertFalse(any(isinstance(x,ast.FunctionDef) and x.name==name
                                 for x in new.body),name)
            expected="src."+canon.removeprefix("src/").removesuffix(".py").replace("/",".")
            self.assertTrue(any(isinstance(x,ast.ImportFrom) and
                x.module==expected and
                any(i.name==name for i in x.names) for x in new.body),name)

    def test_jogador_colisao_skins_e_desafios_equivalentes(self):
        import src.pixelrush.entities.player.animation_state as state
        from src.pixelrush.entities.player.skin_rules import raridade_de_skin,nivel_visual_skin
        from src.pixelrush.entities.enemies.laser_collision import hitbox_disparo_laser
        from src.pixelrush.systems.challenge_helpers import (chave_periodo_semanal,
                                                              gerar_missoes_rodada)
        from src.pixelrush.world.day_night_math import _suavizar_intervalo
        from src.pixelrush.rendering.color_helpers import saturar_cor,misturar_cores
        jogador=SimpleNamespace(morrendo=False,descida_rapida=False,no_chao=True,
            jetpack_fase=None,agachado=False,anim_pouso_ticks=0,tempo_turbo=0,
            tempo_turbo_fantasma=0)
        self.assertEqual(state._estado_skin_jogador(jogador,11),("CORRER",5))
        jogador.morrendo=True;jogador.morte_por_buraco=False;jogador.tempo_morte=35
        self.assertEqual(state._estado_skin_jogador(jogador,11),("MORRER",2))
        self.assertFalse(state.jogador_invencivel_por_velocidade(jogador,10))
        jogador.morrendo=False
        self.assertTrue(state.jogador_invencivel_por_velocidade(jogador,10))
        self.assertEqual(raridade_de_skin("PLATINA"),"Lendário")
        self.assertEqual(nivel_visual_skin({}),1)
        laser=SimpleNamespace(rect=pygame.Rect(13,24,44,20))
        self.assertEqual(hitbox_disparo_laser(laser),pygame.Rect(13,29,44,10))
        self.assertEqual(chave_periodo_semanal(datetime.date(2026,11,5)),"2026-W45")
        random.seed(12771)
        x=gerar_missoes_rodada()
        random.seed(12771)
        y=gerar_missoes_rodada()
        self.assertEqual(x,y)
        self.assertEqual(len(x),3)
        self.assertAlmostEqual(_suavizar_intervalo(0,10,5),.5)
        self.assertEqual(saturar_cor((10,20,30),1.0),(10,20,30))
        self.assertEqual(misturar_cores((0,0,0),(255,255,255),.5),(127,127,127))

    def test_oito_modulos_reais_iguais_e_mesma_instancia(self):
        m=json.loads((ROOT/"docs/arquitetura/MANIFESTO_QA_R20_v327790.json").read_text("utf8"))
        self.assertEqual(len(m["modulos_ativos"]),8)
        pygame.init()
        pygame.display.set_mode((450,800))
        for row in m["modulos_ativos"]:
            old=row["anterior"].removesuffix(".py")
            new=row["canonico"].removesuffix(".py").replace("/",".")
            with self.subTest(name=old):
                legacy=importlib.import_module(old)
                canonical=importlib.import_module(new)
                self.assertIs(legacy,canonical)
                self.assertIs(sys.modules[old],sys.modules[new])
                self.assertEqual(pathlib.Path(legacy.__file__).resolve(),
                    (ROOT/row["canonico"]).resolve())
        pygame.quit()

    def test_arquivo_historico_e_qa_pinados_inviolados(self):
        from hashlib import sha1
        m=json.loads((ROOT/"docs/arquitetura/MANIFESTO_QA_R20_v327790.json").read_text("utf8"))
        self.assertEqual(len(m["prototipos_arquivados"]),8)
        for row in m["prototipos_arquivados"]:
            before=subprocess.check_output(["git","show",BASE+":"+row["anterior"]],cwd=ROOT)
            after=(ROOT/row["arquivo"]).read_bytes()
            self.assertEqual(before,after)
            self.assertFalse((ROOT/row["anterior"]).exists())
            self.assertTrue(row["arquivo"].startswith("archive/prototipos_tutorial/"))
        for p in ("pixelrush_apresentacao_v3273.py",
                  "prototipo_tutorial_v3273.py",
                  "pixelrush_tutorial_prod_v32771.py",
                  "pixelrush_tutorial_corrida_v3277.py",
                  "pixelrush_qa_render_v327729.py",
                  "pixelrush_qa_gles_exact_v327736.py",
                  "pixelrush_qa_camera_v327733.py"):
            with self.subTest(p=p):
                self.assertEqual(subprocess.check_output(["git","show",BASE+":"+p],cwd=ROOT),
                                 (ROOT/p).read_bytes())

if __name__=="__main__":
    unittest.main(verbosity=2)
