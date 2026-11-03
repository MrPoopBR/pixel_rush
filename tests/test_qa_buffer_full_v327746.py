# -*- coding: utf-8 -*-
"""QA v3.277.46: composicao completa de FUNDO da copia QA, byte-exata.

Usa ParallaxBackground PRODUCAO, profundidade cinematografica e Fase B,
clima real, cenas epicas e chao por quadro. NAO inclui sprites/fisica/audio.
Alternativa offscreen nao e ativada: comparacao falha se RGBA divergir.
"""
import os
import sys
import importlib
import random
import unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame

GAME_NAME='PixelRush_v3.277.11_PRODUCAO_ANDROID_RC'

def game_module():
    # O nome historico tem pontos (v3.277.11), nao e um nome Python importavel.
    # Executar com spec explicito, sem disparar o guard if __name__=='__main__'.
    name='pixelrush_qa_game_v327746'
    if name in sys.modules:
        return sys.modules[name]
    arquivo=ROOT/(GAME_NAME+'.py')
    spec=importlib.util.spec_from_file_location(name, arquivo)
    modulo=importlib.util.module_from_spec(spec)
    sys.modules[name]=modulo
    try:
        spec.loader.exec_module(modulo)
    except Exception:
        sys.modules.pop(name,None)
        raise
    return modulo

def rgba(s):
    return pygame.image.tobytes(s,'RGBA')

def criar_contexto(game,bioma,clima_tipo):
    bg=game.ParallaxBackground()
    bg.set_cenario(bioma)
    bg.world.lightweight=False
    clima=game.SistemaClima()
    clima.cenario=bioma
    clima.tipo=clima_tipo
    cenas=game.CenasMemoraveis()
    return bg,clima,cenas

def desenhar_fundo_integral(game,destino,bg,clima,cenas,frame,cor,night):
    cor_render=clima.aplicar_ceu(cor)
    bg.draw(destino,cor_render,night>=.5)
    game.profundidade_cinematografica(destino,bg.cenario,night,False)
    game.desenhar_profundidade_bioma(
        destino,bg.cenario,bg.world.travel,night,False,clima.tipo)
    if clima.tipo!='limpo':
        clima._desenhar_nuvens_clima(destino,cor_render)
    cenas.desenhar(destino,bg.cenario,bg.world.travel,frame,night,leve=False)

def overlay_por_quadro(game,destino,bg,frame):
    bg.draw_chao(destino)
    pygame.draw.rect(destino,(34,66,96),(0,0,450,43))
    pygame.draw.rect(destino,(242,197,91),(11,13,25+frame%80,13))
    pygame.draw.circle(destino,(249,216,105),(410,28),9)

def comparar_bioma(game,bioma,frames=24,cronometrar=False):
    from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA
    bg,clima,cenas=criar_contexto(game,bioma,'limpo')
    ref=pygame.Surface((450,800)).convert()
    alt=ref.copy()
    scratch=ref.copy()
    cache=CacheFundoUltraQA(periodo=5)
    tempos={'original':[],'offscreen':[],'orig_store':[],'offscreen_present':[]}
    equivalentes=0
    for i in range(frames):
        frame=19+i*11
        night=(0.,.3,.6,.95)[(i//5)%4]
        cor=(62+i%25,96+(i*2)%30,136)
        clima.tipo={'cidade':('limpo','chuva','tempestade'),'neve':('limpo','nevasca','neve'),'deserto':('limpo','areia','tempestade_areia')}[bioma][(i//5)%3]
        bg.clima_tipo=clima.tipo
        clima.tempo=frame
        bg.update(8.8)
        bg.peso_noite=night
        bg.world.night=night
        bg.world.climate=clima.tipo
        chave=(bioma,clima.tipo,night>=.5,False,ref.get_size())
        start=pygame.time.get_ticks() # timing real abaixo usa perf_counter_ns
        from time import perf_counter_ns
        t0=perf_counter_ns()
        hit=cache.reusar(ref,chave,True)
        if not hit:
            desenhar_fundo_integral(game,ref,bg,clima,cenas,frame,cor,night)
            t1=perf_counter_ns()
            cache.guardar(ref,chave,True)
            t2=perf_counter_ns()
        else:
            t1=t2=perf_counter_ns()
        overlay_por_quadro(game,ref,bg,frame)
        t3=perf_counter_ns()
        # Mesmo novo desenho, mesmo estado; a superficie offscreen nunca
        # recebe o HUD, evitando contaminacao dos frames reutilizados.
        if not hit:
            desenhar_fundo_integral(game,scratch,bg,clima,cenas,frame,cor,night)
        t4=perf_counter_ns()
        alt.blit(scratch,(0,0))
        t5=perf_counter_ns()
        overlay_por_quadro(game,alt,bg,frame)
        t6=perf_counter_ns()
        if rgba(ref)!=rgba(alt):
            raise AssertionError('divergencia do fundo integral %s frame %d (clima=%s noite=%s)'%
                                 (bioma,i,clima.tipo,night))
        equivalentes+=1
        if cronometrar and i>=5:
            tempos['original'].append((t3-t0)/1e6)
            tempos['offscreen'].append((t6-t3)/1e6)
            tempos['orig_store'].append((t2-t1)/1e6 if not hit else 0.)
            tempos['offscreen_present'].append((t5-t4)/1e6)
    return {'bioma':bioma,'frames_rgba_identicos':equivalentes,
            'redraws':cache.recriacoes,'hits':cache.passes_evitados,
            'tempos_ms':tempos,'cache_rgb_bytes':cache._quadro.get_pitch()*cache._quadro.get_height(),
            'buffer_alternativo_bytes':scratch.get_pitch()*scratch.get_height()}

class FundoIntegralQA746(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_integral_prod_cidade_neve_deserto_24_quadros(self):
        game=game_module()
        self.assertIs(game.LivingWorld.__mro__[0],game.LivingWorld)
        for biome in ('cidade','neve','deserto'):
            resposta=comparar_bioma(game,biome,frames=24)
            self.assertEqual(resposta['frames_rgba_identicos'],24)
            self.assertEqual(resposta['redraws']+resposta['hits'],24)
            self.assertEqual(resposta['buffer_alternativo_bytes'],resposta['cache_rgb_bytes'])

if __name__=='__main__':
    unittest.main(verbosity=2)
