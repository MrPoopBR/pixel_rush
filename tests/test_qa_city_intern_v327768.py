# -*- coding: utf-8 -*-
"""QA768 — internacao imutavel de atlas Cidade multi-instancia, RGBA completo."""
import os,sys,gc,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
from pixelrush_city2_v3125 import CityPilotScene
import pixelrush_qa_city_bootstrap_v327759 as boot
import pixelrush_qa_city_intern_v327768 as intern

def rgba(s):
    return pygame.image.tobytes(s,'RGBA')

def sintetico(rgb):
    def tex():
        s=pygame.Surface((16,12),pygame.SRCALPHA)
        s.fill((rgb[0],rgb[1],rgb[2],0))
        s.set_at((2,3),(255,170,19,137))
        return s
    v=SimpleNamespace(geometry=tex(),normal=tex(),material=tex(),
                      flow=tex(),fxmask=tex())
    return SimpleNamespace(layers=[SimpleNamespace(variants=[v])]),v

class InternCity768(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):
        boot.restaurar_para_teste()
        intern.restaurar_para_teste()
        pygame.quit()

    def test_rgb_oculto_igualdade_sem_atalho_incorreto(self):
        a,va=sintetico((42,67,92))
        b,vb=sintetico((42,67,92))
        c,vc=sintetico((43,67,92))
        intern.compartilhar(a)
        intern.compartilhar(b)
        intern.compartilhar(c)
        for kind in ('geometry','normal','material','flow','fxmask'):
            self.assertIs(getattr(va,kind),getattr(vb,kind))
            self.assertIsNot(getattr(va,kind),getattr(vc,kind))
            self.assertEqual(rgba(getattr(va,kind)),rgba(getattr(vb,kind)))
        self.assertGreater(intern.diagnostico()['bytes_evitaram'],0)

    def test_cidade_real_duas_instancias_6_canais_equivalentes(self):
        boot.instalar()
        first=CityPilotScene()
        second=CityPilotScene()
        count=0
        for layer1,layer2 in zip(first.layers,second.layers):
            for v1,v2 in zip(layer1.variants,layer2.variants):
                for kind in ('geometry','normal','material','flow','fxmask'):
                    if getattr(v1,kind) is getattr(v2,kind):
                        count+=1
        self.assertGreater(count,0,'Nenhum atlas imutavel compartilhado')
        self.assertGreater(intern.diagnostico()['bytes_evitaram'],0)
        with patch.dict(os.environ,{'PIXELRUSH_QA_CITY_GLOBAL_INTERN':'0'}):
            reference=CityPilotScene()
        for kind in ('image','geometry','normal','material','flow','fxmask'):
            for scene in (first,second,reference):
                scene.visual_quality=1
            buffers=[]
            for scene in (first,second,reference):
                dst=pygame.Surface((450,500),pygame.SRCALPHA)
                dst.fill((49,97,121,0))
                scene.render_scene(dst,134.75,27,.38,'limpo',.43,
                                   map_kind=kind)
                buffers.append(rgba(dst))
            self.assertEqual(buffers[0],buffers[1],kind)
            self.assertEqual(buffers[0],buffers[2],kind)
        # Os ambientes sao independentes: compartilhar textura nao compartilha
        # estado de frame, clima, cache de imagem ou quality.
        self.assertIsNot(first._scaled,second._scaled)
        self.assertIsNot(first.layers,second.layers)

    def test_desativacao_nao_compartilha_e_tabela_weak(self):
        a,va=sintetico((12,31,77));b,vb=sintetico((12,31,77))
        with patch.dict(os.environ,{'PIXELRUSH_QA_CITY_GLOBAL_INTERN':'0'}):
            self.assertFalse(intern.compartilhar(a))
            self.assertFalse(intern.compartilhar(b))
        self.assertIsNot(va.geometry,vb.geometry)
        intern.restaurar_para_teste()
        def montar():
            scene,variant=sintetico((91,120,24))
            intern.compartilhar(scene)
        montar()
        gc.collect()
        self.assertEqual(intern.diagnostico()['tabela'],0)

if __name__=='__main__':
    unittest.main(verbosity=2)
