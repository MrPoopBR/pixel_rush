# -*- coding: utf-8 -*-
"""QA765 — equivalencia exata da apresentacao/camera real, com rollback."""
import os,sys,unittest
from pathlib import Path
from collections import OrderedDict
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
from pixelrush_qa_unified_post_v327750 import finalizar_quadro

def rgba(s):return pygame.image.tobytes(s,'RGBA')

class Camera:
    def __init__(self):self.calls=0
    def aplicar(self,img,jogador,vel,momento,ativo):
        self.calls+=1
        s=img.copy()
        pygame.draw.rect(s,(75,111,157),(3,3,12,12))
        return s

def referencia(imagem,tela,tamanho,pos,cache,camera,usa):
    if usa:imagem=camera.aplicar(imagem,None,9,True,True)
    if tamanho==imagem.get_size():
        final=imagem
    else:
        final=cache.get(tamanho)
        if final is None:
            try:final=pygame.Surface(tamanho).convert()
            except pygame.error:final=pygame.Surface(tamanho)
            cache[tamanho]=final
            if len(cache)>3:cache.popitem(last=False)
        else:cache.move_to_end(tamanho)
        pygame.transform.scale(imagem,tamanho,final)
    tela.blit(final,pos)
    pygame.display.flip()

class Post765(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((200,150))
    @classmethod
    def tearDownClass(cls):pygame.quit()

    def test_pipeline_equivale_blit_final_original_sem_camera_e_com_camera(self):
        for src_alpha in (False,True):
            for dst_alpha in (False,True):
                for usa in (False,True):
                    for size,pos in (((120,80),(6,9)),((180,120),(0,0)),
                                     ((200,150),(0,0))):
                        src=pygame.Surface((120,80),pygame.SRCALPHA if src_alpha else 0)
                        src.fill((11,62,99,0 if src_alpha else 255))
                        pygame.draw.rect(src,(81,32,176,193 if src_alpha else 255),
                                         (11,13,39,35))
                        a=pygame.Surface((200,150),pygame.SRCALPHA if dst_alpha else 0)
                        b=a.copy()
                        a.fill((19,71,98,0 if dst_alpha else 255));b.fill((19,71,98,0 if dst_alpha else 255))
                        ca,cb=Camera(),Camera()
                        with patch.object(pygame.display,'flip',return_value=None):
                            referencia(src,a,size,pos,OrderedDict(),ca,usa)
                            finalizar_quadro(src,b,size,pos,OrderedDict(),cb,None,
                                            9,True,usa,lambda x:None,lambda:None,
                                            lambda x:None)
                        self.assertEqual(rgba(a),rgba(b),
                                         (src_alpha,dst_alpha,usa,size,pos))
                        self.assertEqual(ca.calls,cb.calls)

    def test_reuso_lru_e_tela_auto_blit_opaca_e_rgba(self):
        for alpha in (False,True):
            flags=pygame.SRCALPHA if alpha else 0
            tela=pygame.Surface((200,150),flags)
            tela.fill((35,68,90,170 if alpha else 255))
            pygame.draw.rect(tela,(120,77,60,45 if alpha else 255),
                             (20,20,40,30))
            legacy=tela.copy()
            cache_a,cache_b=OrderedDict(),OrderedDict()
            with patch.object(pygame.display,'flip',return_value=None):
                referencia(legacy,legacy,(200,150),(0,0),cache_a,Camera(),False)
                finalizar_quadro(tela,tela,(200,150),(0,0),cache_b,Camera(),None,
                                8,False,False,lambda x:None,lambda:None,
                                lambda x:None)
            self.assertEqual(rgba(legacy),rgba(tela),alpha)
            self.assertEqual(len(cache_b),0)

if __name__=='__main__':
    unittest.main(verbosity=2)
