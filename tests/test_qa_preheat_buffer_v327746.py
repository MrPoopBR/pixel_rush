# -*- coding: utf-8 -*-
"""PIXEL RUSH QA v3.277.46: atlas PROD e alternativas de buffer pixel-exatas."""
import os
import random
import sys
import unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame

def rgba(s):
    return pygame.image.tobytes(s,'RGBA')

class PreheatBufferQA746(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_preheat_fora_do_jogo_e_limites_de_rss(self):
        from pixelrush_world_prod_v32777 import LivingWorld
        from pixelrush_qa_biome_preheat_v327746 import preparar_fora_da_corrida
        w=LivingWorld('cidade',lightweight=True)
        snap=(w.biome,w.travel,w.frame,random.getstate())
        denied=preparar_fora_da_corrida(w,'neve','JOGANDO')
        self.assertEqual(denied['estado'],'estado_proibido')
        denied=preparar_fora_da_corrida(w,'neve','INICIO',teto_rss_mib=1.0)
        self.assertEqual(denied['estado'],'orcamento_insuficiente')
        self.assertFalse(w.modular)
        self.assertEqual((w.biome,w.travel,w.frame),snap[:3])
        self.assertEqual(random.getstate(),snap[3])

    def test_atlas_prod_preparado_e_reutilizado_sem_duplicar(self):
        from pixelrush_world_prod_v32777 import LivingWorld
        from pixelrush_qa_biome_preheat_v327746 import preparar_fora_da_corrida
        for biome in ('neve','deserto'):
            w=LivingWorld('cidade',lightweight=True)
            old_random=random.getstate()
            result=preparar_fora_da_corrida(
                w,biome,'CARREGANDO',teto_rss_mib=9999,max_aumento_mib=64)
            self.assertEqual(result['estado'],'preparado',result)
            self.assertEqual(len(w.modular),1)
            ref=w.modular[biome]
            self.assertEqual(random.getstate(),old_random)
            again=preparar_fora_da_corrida(
                w,biome,'CARREGANDO',teto_rss_mib=9999,max_aumento_mib=64)
            self.assertEqual(again['estado'],'ja_preparado')
            self.assertIs(ref,w.modular[biome])
            other='deserto' if biome=='neve' else 'neve'
            denied=preparar_fora_da_corrida(
                w,other,'CARREGANDO',teto_rss_mib=9999,max_aumento_mib=64)
            self.assertEqual(denied['estado'],'slot_ocupado')
            w.switch(biome)
            self.assertIs(ref,w._get_modular())
            self.assertLessEqual(len(w.modular),1)
            self.assertEqual(random.getstate(),old_random)

    def test_atlas_preparado_e_fallback_prod_pixel_exato(self):
        from pixelrush_world_prod_v32777 import LivingWorld
        from pixelrush_qa_biome_preheat_v327746 import preparar_fora_da_corrida
        for biome in ('neve','deserto'):
            a=LivingWorld('cidade',lightweight=True)
            b=LivingWorld('cidade',lightweight=True)
            out=preparar_fora_da_corrida(
                b,biome,'INICIO',teto_rss_mib=9999,max_aumento_mib=64)
            self.assertEqual(out['estado'],'preparado')
            a.switch(biome)
            b.switch(biome)
            for i in range(6):
                for w in (a,b):
                    w.update(7.75,night=.13*(i%5),climate='limpo',phase=.52)
                x=pygame.Surface((450,800)).convert()
                y=x.copy()
                x.fill((36,51,63)); y.fill((36,51,63))
                a.draw(x); b.draw(y)
                self.assertEqual(rgba(x),rgba(y),(biome,i))
                self.assertLessEqual(len(b.modular),1)

    def test_producao_ja_usa_atlas_verificado(self):
        from pixelrush_world_prod_v32777 import LivingWorld
        from pixelrush_world_prod_v32775 import LivingWorld as Anterior
        from pixelrush_atlas_prod_v32776 import _ATLAS, _HASHES
        self.assertTrue(issubclass(LivingWorld,Anterior))
        self.assertIn('neve_lite',_HASHES)
        self.assertIn('deserto_lite',_HASHES)
        self.assertTrue((_ATLAS/'neve_lite.atlas').is_file())
        self.assertTrue((_ATLAS/'deserto_lite.atlas').is_file())

if __name__=='__main__':
    unittest.main(verbosity=2)
