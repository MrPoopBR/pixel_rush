# -*- coding: utf-8 -*-
"""QA777 - mesma composicao RGBA com/sem cronometros internos City."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ['PIXELRUSH_QA_ANDROID']='1'
os.environ['PIXELRUSH_QA_R11_CHUNK_PASSES']='1'
import unittest
from unittest.mock import patch
import pygame
import pixelrush_city2_v3118 as base
from pixelrush_world_v3130 import LivingWorld
from pixelrush_qa_city_bootstrap_v327759 import instalar as boot,restaurar_para_teste as restore

def raw(s):return pygame.image.tobytes(s,'RGBA')
class QA777Chunks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800));boot()
    @classmethod
    def tearDownClass(cls):
        restore();pygame.quit()
    def test_rgba_real_e_pareamento(self):
        self.assertTrue(base._R11_CHUNK_TRACE)
        for flags,bpp in ((0,16),(0,24),(0,32),(pygame.SRCALPHA,32)):
            w=LivingWorld('cidade')
            w.update(6.,.58,'chuva',.65)
            a=pygame.Surface((450,800),flags,bpp)
            a.fill((21,67,91,0) if flags else (21,67,91))
            b=a.copy()
            with patch.object(base,'_R11_CHUNK_TRACE',False):
                w.draw(a)
            begin=[];end=[]
            with patch.object(base,'_r11_sub_inicio',lambda name:begin.append(name)), patch.object(base,'_r11_sub_fim',lambda:end.append(1)):
                w.draw(b)
            self.assertEqual(raw(a),raw(b),(flags,bpp))
            self.assertIn('r11_city_chunk_base',begin)
            self.assertIn('r11_city_chunk_sprites',begin)
            self.assertEqual(len(begin),len(end))
            self.assertEqual(begin.count('r11_city_chunk_base'),begin.count('r11_city_chunk_sprites'))
if __name__=='__main__':unittest.main(verbosity=2)
