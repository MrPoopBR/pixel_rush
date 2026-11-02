# -*- coding: utf-8 -*-
"""QA v3.277.32: equivalencia visual, reuso e protecao da jogabilidade."""
import ast
from collections import OrderedDict
from functools import lru_cache
import os
from pathlib import Path
import unittest

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame

ROOT = Path(__file__).resolve().parents[1]


def pixels(s):
    return pygame.image.tobytes(s, 'RGBA' if s.get_flags() & pygame.SRCALPHA else 'RGB')


class PerformanceQA327732(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450, 800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_fabrik_scratch_idempotente_e_pixel_igual(self):
        from pixelrush_profissional_v3108 import ArticulacaoFABRIK
        rig=ArticulacaoFABRIK(120, seed=17)
        src=pygame.Surface((120,120),pygame.SRCALPHA)
        for y in range(120):
            pygame.draw.line(src,(y*3%256,y*7%256,y*11%256,y*13%256),(0,y),(119,y))
        scratch=None
        for frame in range(90):
            rig.update(frame,wind=(-1 if frame%2 else 1)*1.2,wake=float(frame%3==0))
            ref,refpad=rig.deform(src)
            out,pad=rig.deform(src,target=scratch)
            self.assertEqual(refpad,pad)
            self.assertEqual(pixels(ref),pixels(out), 'FABRIK '+str(frame))
            if scratch is not None:
                self.assertIs(out,scratch)
            scratch=out
        # Caso de tamanho alterado exige buffer novo, sem erro ou truncamento.
        new,pad=rig.deform(pygame.Surface((36,55),pygame.SRCALPHA),target=scratch)
        self.assertEqual(new.get_size(),(88,55))

    def test_alpha_transicao_sem_copia_equivalente(self):
        for flags in (0,pygame.SRCALPHA):
            trans=pygame.Surface((120,170),flags,32)
            for y in range(170):
                pygame.draw.line(trans,(y*3%256,y*5%256,y*7%256,y*9%256),
                                 (0,y),(119,y))
            for alpha in (0,1,28,77,131,210,255):
                base=pygame.Surface((120,170)).convert()
                base.fill((31,74,113))
                reference=base.copy()
                copied=trans.copy()
                copied.set_alpha(alpha)
                reference.blit(copied,(0,0))
                out=base.copy()
                original=trans.get_alpha()
                trans.set_alpha(alpha)
                try:
                    out.blit(trans,(0,0))
                finally:
                    trans.set_alpha(original)
                self.assertEqual(original,trans.get_alpha())
                self.assertEqual(pixels(reference),pixels(out))

    def test_cached_icon_laser_identico(self):
        from pixelrush_fase_b_visuais_v3272 import _icone_laser_qa
        self.assertEqual(_icone_laser_qa.cache_info().maxsize,3)
        for faixa in range(3):
            cached=_icone_laser_qa(faixa)
            self.assertIs(cached,_icone_laser_qa(faixa))
            legacy=pygame.Surface((75,70),pygame.SRCALPHA)
            pygame.draw.rect(legacy,(8,27,43,220),(0,0,75,70),border_radius=8)
            pygame.draw.rect(legacy,(225,245,249,165),(0,0,75,70),2,border_radius=8)
            for pos,nivel in enumerate((2,1,0)):
                y=8+pos*20
                perigo=nivel==faixa
                cor=(245,128,113,229) if perigo else (101,207,206,195)
                pygame.draw.rect(legacy,cor,(8,y,59,14),border_radius=3)
                if perigo:
                    pygame.draw.line(legacy,(20,33,47),(35,y+3),(43,y+11),3)
                    pygame.draw.line(legacy,(20,33,47),(43,y+3),(35,y+11),3)
                    for dx in (12,18,24,49,55):
                        pygame.draw.line(legacy,(57,48,51,150),(dx,y+12),(dx+4,y+3),1)
                else:
                    for dx in (31,39):
                        pygame.draw.lines(legacy,(13,54,65),False,[(dx,y+3),(dx+4,y+7),(dx,y+11)],2)
            self.assertEqual(pixels(cached),pixels(legacy))

    def test_escala_de_rotulos_sem_diferenca(self):
        # Extrair a funcao REAL do jogo sem importar o entrypoint Android.
        arquivo=ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py'
        arvore=ast.parse(arquivo.read_text('utf8'),filename=str(arquivo))
        f=next(x for x in arvore.body
               if isinstance(x,ast.FunctionDef) and x.name=='_qa_cache_escala_rotulo')
        # Decorator precisa ser resolvido no namespace do teste.
        namespace={'pygame':pygame, '_qa_lru_cache_rotulos':lru_cache}
        exec(compile(ast.Module(body=[f],type_ignores=[]),str(arquivo),'exec'),namespace)
        cache=namespace['_qa_cache_escala_rotulo']
        original=pygame.Surface((112,36),pygame.SRCALPHA)
        for i in range(10):
            pygame.draw.circle(original,(i*23%256,i*17%256,90,100+i*13),(i*10+10,18),10)
        for size in ((38,12),(56,18),(83,27),(101,32)):
            esperado=pygame.transform.smoothscale(original,size)
            obtido=cache(original,size)
            self.assertEqual(pixels(esperado),pixels(obtido))
            self.assertIs(obtido,cache(original,size))

    def test_versao_e_escopo(self):
        source=(ROOT/'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py').read_text('utf8')
        world=(ROOT/'pixelrush_world_v3130.py').read_text('utf8')
        code=(ROOT/'pixelrush_profissional_v3108.py').read_text('utf8')
        assert 'VERSAO = "v3.277.37-QA-ANDROID-RC"' in source
        for invariant in ('MAX_PASSOS_POR_FRAME = 8 if E_ANDROID else 15',
                          'FPS_RENDER = 30 if E_ANDROID else 60',
                          'PIXELRUSH_DEV_BUILD = False',
                          'CacheFundoUltraQA(periodo=5)'):
            self.assertIn(invariant,source)
        self.assertIn("pygame.transform.flip(piece, True, False)",world)
        self.assertIn("rig.deform(pp,target=deform_target)",world)
        self.assertIn("def deform(self, image, strip=4, target=None):",code)


if __name__=='__main__':
    unittest.main(verbosity=2)
