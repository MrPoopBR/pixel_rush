# -*- coding: utf-8 -*-
"""QA792: equivalencia AST, RNG, RGBA, pools e imports historicos."""
import ast
import importlib
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame

BASE="aafbb354b78fc7be50013176cd9847f6ff4729bc"
ENGINE="PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py"
CLASSES={
    "MonitorQualidadeVisual":"src/pixelrush/performance/quality_monitor.py",
    "Moeda":"src/pixelrush/entities/collectibles.py",
    "PoolManager":"src/pixelrush/entities/collectibles.py",
}
MODULES={
    "pixelrush_touch_v3229.py":"src/pixelrush/systems/touch_v3229.py",
    "pixelrush_aprendizado_v3208.py":"src/pixelrush/systems/contextual_learning_v3208.py",
    "pixelrush_feedback_v3190.py":"src/pixelrush/ui/feedback_v3190.py",
    "pixelrush_percursos_v3191.py":"src/pixelrush/systems/route_variety_v3191.py",
    "pixelrush_rotas_v3225.py":"src/pixelrush/systems/biome_routes_v3225.py",
    "pixelrush_hidrante_cidade_v3276.py":"src/pixelrush/entities/enemies/city_hydrant_v3276.py",
}

def baseline():
    return subprocess.check_output(["git","show",BASE+":"+ENGINE],cwd=ROOT).decode("utf8")

def old_classes(names,globals_ns):
    tree=ast.parse(baseline())
    nodes=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name in names]
    assert len(nodes)==len(names)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),ENGINE,"exec"),globals_ns)
    return globals_ns

class QA792Testes(unittest.TestCase):
    def test_ast_integral_motor_sem_diffs_involuntarios(self):
        old=ast.parse(baseline())
        new=ast.parse((ROOT/ENGINE).read_text("utf8"))
        for name,path in CLASSES.items():
            orig=[n for n in old.body if isinstance(n,ast.ClassDef) and n.name==name]
            curr=[n for n in ast.parse((ROOT/path).read_text("utf8")).body if isinstance(n,ast.ClassDef) and n.name==name]
            self.assertEqual(len(orig),len(curr)==1 and 1 or 0,name)
            self.assertEqual(ast.dump(orig[0],include_attributes=False),
                             ast.dump(curr[0],include_attributes=False),name)
            self.assertFalse(any(isinstance(n,ast.ClassDef) and n.name==name for n in new.body),name)
        expected_monitor=ast.parse("""from src.pixelrush.performance import quality_monitor as _quality_monitor
_quality_monitor.E_ANDROID = E_ANDROID
from src.pixelrush.performance.quality_monitor import MonitorQualidadeVisual""").body
        expected_coins=ast.parse("""from src.pixelrush.entities import collectibles as _collectibles
_collectibles.CHAVE_TRANSPARENCIA_SPRITES = CHAVE_TRANSPARENCIA_SPRITES
_collectibles.AMARELO_MOEDA = AMARELO_MOEDA
_collectibles.PRETO = PRETO
from src.pixelrush.entities.collectibles import Moeda, PoolManager""").body
        class Transform(ast.NodeTransformer):
            def visit_ClassDef(self,node):
                if node.name=="MonitorQualidadeVisual": return expected_monitor
                if node.name=="Moeda": return expected_coins
                if node.name=="PoolManager": return []
                return self.generic_visit(node)
            def visit_Assign(self,node):
                if any(isinstance(t,ast.Name) and t.id=="VERSAO" for t in node.targets):
                    if isinstance(node.value,ast.Constant) and node.value.value=="v3.277.91-QA-ANDROID-RC":
                        node.value=ast.Constant("v3.277.92-QA-ANDROID-RC")
                return self.generic_visit(node)
        converted=Transform().visit(old)
        self.assertEqual(ast.dump(converted,include_attributes=False),
                         ast.dump(new,include_attributes=False))

    def test_modulos_legados_mesmo_objeto_e_blob_intacto(self):
        import hashlib
        for previous,canon in MODULES.items():
            with self.subTest(module=previous):
                content=(ROOT/canon).read_bytes()
                old=subprocess.check_output(["git","show",BASE+":"+previous],cwd=ROOT)
                self.assertEqual(old,content)
                wrapper=(ROOT/previous).read_text("utf8")
                self.assertIn("_sys.modules[__name__]",wrapper)
                self.assertIn("import_module(",wrapper)
                legacy=importlib.import_module(previous[:-3])
                current=importlib.import_module(canon[:-3].replace("/","."))
                self.assertIs(legacy,current)
                self.assertIs(sys.modules[previous[:-3]],current)
                self.assertEqual(Path(current.__file__).resolve(),(ROOT/canon).resolve())

    def test_monitor_qualidade_visual_android_e_desktop(self):
        import src.pixelrush.performance.quality_monitor as mod
        original=mod.E_ANDROID
        try:
            for android in (False,True):
                old=old_classes({"MonitorQualidadeVisual"},{"E_ANDROID":android})["MonitorQualidadeVisual"]()
                mod.E_ANDROID=android
                new=mod.MonitorQualidadeVisual()
                sequencia=[(12,0.016,"auto",True)]*160+[(75,0.016,"auto",True)]*820
                sequencia.extend([(29,0.016,"manual",True),(0,0.016,"auto",False)])
                for fps,dt,modo,jogando in sequencia:
                    old.atualizar(fps,dt,modo,jogando)
                    new.atualizar(fps,dt,modo,jogando)
                    self.assertEqual(vars(old),vars(new))
        finally:
            mod.E_ANDROID=original

    def test_moeda_e_pool_rng_rgba_pygame_ce(self):
        import src.pixelrush.entities.collectibles as c
        from src.pixelrush.entities.particles import Particula
        ns={"pygame":pygame,"random":random,"math":math,"Sprite":pygame.sprite.Sprite,
            "Particula":Particula,
            "CHAVE_TRANSPARENCIA_SPRITES":(255,0,255),
            "AMARELO_MOEDA":(255,215,0),"PRETO":(0,0,0)}
        old_classes({"Moeda","PoolManager"},ns)
        oldmoeda,oldpool=ns["Moeda"],ns["PoolManager"]
        self.assertIs(c.Particula,Particula)
        self.assertEqual((c.CHAVE_TRANSPARENCIA_SPRITES,c.AMARELO_MOEDA,c.PRETO),
                         ((255,0,255),(255,215,0),(0,0,0)))
        pygame.init()
        pygame.display.set_mode((450,800))
        try:
            for seed in (0,1,83,792):
                results=[]
                for coin,manager in ((oldmoeda,oldpool),(c.Moeda,c.PoolManager)):
                    coin._imagens_variantes=None
                    random.seed(seed)
                    pool=manager()
                    self.assertEqual((len(pool.particulas_pool),len(pool.moedas_pool)),(250,120))
                    p=pool.obter_moeda(120,450)
                    player=SimpleNamespace(tempo_ima=20,morrendo=False,rect=pygame.Rect(145,430,40,65))
                    frames=[]
                    for _ in range(15):
                        p.update(4.7,player)
                        frames.append((tuple(p.rect),p._x_float,p._y_float,
                            pygame.image.tobytes(p.image,"RGBA"),p.ativo))
                    state=random.getstate()
                    rect_before=tuple(p.rect)
                    p.kill(); p.kill()
                    self.assertEqual(pool.moedas_disponiveis.count(p),1)
                    p2=pool.obter_moeda(42,390)
                    self.assertIs(p,p2)
                    results.append((state,rect_before,frames,tuple(p2.rect),
                                    pygame.image.tobytes(p2.image,"RGBA"),
                                    len(pool.moedas_disponiveis),len(pool.particulas_disponiveis)))
                self.assertEqual(results[0],results[1],f"seed={seed}")
        finally:
            pygame.quit()

    def test_imports_e_comportamento_touch_aprendizado_hidrante(self):
        touch=importlib.import_module("pixelrush_touch_v3229")
        self.assertEqual(touch.passos_jetpack(90),2)
        self.assertEqual(touch.passos_jetpack(-90),-2)
        self.assertEqual(touch.ancorar_jetpack(100,162,2),160)
        aprender=importlib.import_module("pixelrush_aprendizado_v3208").AprendizadoContextual()
        aprender.registrar("buraco")
        self.assertEqual(aprender.mensagem("pt_BR")[0],"QUEDA NO BURACO")
        aprender.limpar()
        self.assertIsNone(aprender.mensagem())
        pygame.init()
        pygame.display.set_mode((450,800))
        try:
            fonte=importlib.import_module("pixelrush_hidrante_cidade_v3276").HidranteCidade
            a=fonte(310)
            rects=(tuple(a.rect),tuple(a._hitboxes_precisas_v342))
            img=pygame.image.tobytes(a.image,"RGBA")
            # Executar classe-fonte original isoladamente com mesmo pygame.
            original=subprocess.check_output(["git","show",BASE+":pixelrush_hidrante_cidade_v3276.py"],cwd=ROOT).decode("utf8")
            ns={"pygame":pygame}
            exec(compile(original,"hidrante_original.py","exec"),ns)
            b=ns["HidranteCidade"](310)
            self.assertEqual(rects,(tuple(b.rect),tuple(b._hitboxes_precisas_v342)))
            self.assertEqual(img,pygame.image.tobytes(b.image,"RGBA"))
            for vel in (2.5,8.2,11.0):
                a.update(vel);b.update(vel)
                self.assertEqual(tuple(a.rect),tuple(b.rect))
        finally:
            pygame.quit()

if __name__=="__main__":
    unittest.main(verbosity=2)
