# -*- coding: utf-8 -*-
"""QA791: AST integral, classes com estado, pygame-ce/RGBA e RNG preservados."""
import ast
import importlib
import pathlib
import random
import subprocess
import sys
import unittest
import os
from types import SimpleNamespace

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame

BASE="854f3906d31f15f4d4fe09d8212535ad835fa654"
ENGINE="PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py"
CLASSES={
    "_FonteHindiComFallback":"src/pixelrush/ui/i18n_fonts.py",
    "_FontePainelLocalizado":"src/pixelrush/ui/i18n_fonts.py",
    "Particula":"src/pixelrush/entities/particles.py",
}

def old_engine():
    return subprocess.check_output(["git","show",BASE+":"+ENGINE],cwd=ROOT).decode("utf-8")

def old_class(name, original):
    tree=ast.parse(original)
    cls=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name==name)
    import pixelrush_traducoes_v3247 as translations
    ns={"pygame":pygame,"random":random,"Sprite":pygame.sprite.Sprite,"_i18n247":translations}
    exec(compile(ast.Module(body=[cls],type_ignores=[]),ENGINE,"exec"),ns)
    return ns[name]

class QA791Classes(unittest.TestCase):
    def test_ast_de_tres_classes_e_motor_inteiro(self):
        original=ast.parse(old_engine())
        current=ast.parse((ROOT/ENGINE).read_text("utf8"))
        oldclasses={n.name:n for n in original.body if isinstance(n,ast.ClassDef)}
        for nome,path in CLASSES.items():
            source=ast.parse((ROOT/path).read_text("utf8"))
            extracted=[n for n in source.body if isinstance(n,ast.ClassDef) and n.name==nome]
            self.assertEqual(len(extracted),1,nome)
            self.assertEqual(ast.dump(oldclasses[nome],include_attributes=False),
                             ast.dump(extracted[0],include_attributes=False),nome)
            self.assertFalse(any(isinstance(n,ast.ClassDef) and n.name==nome for n in current.body))
            module=path.removesuffix(".py").replace("/",".")
            self.assertTrue(any(isinstance(n,ast.ImportFrom) and n.module==module
                      and any(x.name==nome for x in n.names) for n in current.body),nome)
        # Um único diff AST global permitido: 3 classes -> imports e versao.
        class Expected(ast.NodeTransformer):
            def visit_ClassDef(self,node):
                if node.name in CLASSES:
                    path=CLASSES[node.name]
                    return ast.copy_location(ast.ImportFrom(
                        module=path.removesuffix(".py").replace("/","."),
                        names=[ast.alias(name=node.name)], level=0),node)
                return self.generic_visit(node)
            def visit_Assign(self,node):
                if any(isinstance(t,ast.Name) and t.id=="VERSAO" for t in node.targets):
                    if isinstance(node.value,ast.Constant) and node.value.value=="v3.277.90-QA-ANDROID-RC":
                        node.value=ast.Constant("v3.277.91-QA-ANDROID-RC")
                return self.generic_visit(node)
        expect=Expected().visit(original)
        self.assertEqual(ast.dump(expect,include_attributes=False),
                         ast.dump(current,include_attributes=False))

    def test_particula_estado_rng_surface_rgba_identicos(self):
        from src.pixelrush.entities.particles import Particula
        velha=old_class("Particula",old_engine())
        pygame.init()
        pygame.display.set_mode((450,800))
        try:
            for seed in (0,1,47,789,791):
                resultados=[]
                for klass in (velha,Particula):
                    random.seed(seed)
                    p=klass(22,31,(17,83,239),None,None,8,5)
                    imagens=[pygame.image.tobytes(p.image,"RGBA")]
                    estado=random.getstate()
                    rects=[tuple(p.rect)]
                    alphas=[p.image.get_alpha()]
                    for _ in range(10):
                        p.update()
                        imagens.append(pygame.image.tobytes(p.image,"RGBA"))
                        rects.append(tuple(p.rect))
                        alphas.append(p.image.get_alpha())
                    resultados.append((estado,rects,alphas,imagens,p.ativo))
                self.assertEqual(resultados[0],resultados[1],seed)
            # Pool reutiliza identidade e apenas devolve o objeto uma vez.
            p=Particula(4,5,vx=0,vy=0)
            mgr=SimpleNamespace(particulas_disponiveis=[])
            p.pool_manager=mgr
            p.kill(); p.kill()
            self.assertEqual(mgr.particulas_disponiveis,[p])
        finally:
            pygame.quit()

    def test_fontes_localizadas_rgba_identico(self):
        from src.pixelrush.ui.i18n_fonts import _FonteHindiComFallback,_FontePainelLocalizado
        original=old_engine()
        pygame.init()
        pygame.display.set_mode((450,800))
        try:
            for nome,novo,argumentos,textos in (
                ("_FonteHindiComFallback",_FonteHindiComFallback,
                 (pygame.font.Font(None,22),pygame.font.Font(None,22)),
                 ("Olá 123", "a\\u0905b 17", "")),
                ("_FontePainelLocalizado",_FontePainelLocalizado,
                 (pygame.font.Font(None,22),"pt_BR"),
                 ("INICIAR","Você ganhou!", "PIXEL RUSH"))):
                velha=old_class(nome,original)
                a,b=velha(*argumentos),novo(*argumentos)
                self.assertEqual(a.__slots__,b.__slots__)
                for txt in textos:
                    self.assertEqual(a.size(txt),b.size(txt))
                    x,y=a.render(txt,True,(245,201,65)),b.render(txt,True,(245,201,65))
                    self.assertEqual(x.get_size(),y.get_size())
                    self.assertEqual(pygame.image.tobytes(x,"RGBA"),
                                     pygame.image.tobytes(y,"RGBA"))
        finally:
            pygame.quit()

if __name__=="__main__":
    unittest.main(verbosity=2)
