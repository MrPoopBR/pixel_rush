# -*- coding: utf-8 -*-
"""QA780: regressao temporal do fundo 2.5D, scroll e camera real pygame-ce.

Nao usa emulador/GLES mock como aprovacao do Mali. No video SDL dummy,
compara bytes RGBA de sequencias independentes e mede custos p50/p95.
"""
import os
import sys
import json
import statistics
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame

def rgba(s):
    return pygame.image.tobytes(s, "RGBA")

def percentil(valores, parte):
    a=sorted(valores)
    return round(a[min(len(a)-1,round((len(a)-1)*parte))],3) if a else None

def textura(largura=253,altura=64,alpha=False):
    s=pygame.Surface((largura,altura),pygame.SRCALPHA if alpha else 0,32)
    for y in range(altura):
        for x in range(largura):
            r=(x*29+y*13)%256
            g=(x*7+y*23)%256
            b=(x*11+y*17)%256
            a=(x*19+y*31)%256 if alpha else 255
            s.set_at((x,y),(r,g,b,a))
    return s

class TemporalRGBA780(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
        cls.medicoes={}

    @classmethod
    def tearDownClass(cls):
        (ROOT/"qa-temporal-rgba-v327780.json").write_text(json.dumps({
            "schema":"pixelrush.qa.temporal.v327780",
            "pygame_ce":pygame.version.ver,
            "android_real":False,
            "aprovacao_gpu_android":False,
            "medicoes":cls.medicoes,
        },indent=2,ensure_ascii=False),encoding="utf8")
        pygame.quit()

    def test_scroll_incremental_sequencia_rgb_e_rgba_oculto(self):
        from pixelrush_qa_rolling_v327740 import (
            FaixaPersistenteQA,mosaico_referencia)
        for alpha in (False,True):
            with self.subTest(alpha=alpha):
                fonte=textura(alpha=alpha)
                sc=FaixaPersistenteQA(450)
                custos=[]
                offsets=(list(range(0,300,3))+[302,301,295,400,900,0,900,45])
                for pos in offsets:
                    t0=time.perf_counter_ns()
                    atual=sc.gerar(fonte,pos)
                    custos.append((time.perf_counter_ns()-t0)/1e6)
                    esperado=mosaico_referencia(fonte,pos,450)
                    self.assertEqual(rgba(atual),rgba(esperado),
                                     ("scroll_RGBA",alpha,pos))
                self.medicoes["scroll_alpha_"+str(alpha)]={
                    "amostras":len(offsets),
                    "p50_ms":percentil(custos,.50),
                    "p95_ms":percentil(custos,.95),
                    "pixels_reconstruidos":sc.pixels_reconstruidos,
                }

    def test_fundo_2d_cache_5_temporal_referencial(self):
        from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA
        cache=CacheFundoUltraQA(periodo=5)
        # O cache real armazena Surface RGB display, nunca SRCALPHA.
        fundo=pygame.Surface((450,800)).convert()
        alvo=pygame.Surface((450,800)).convert()
        fundos_redesenhados=0
        for frame in range(80):
            # O fundo do jogo tem animacoes; paridade so pode ser reivindicada
            # nos quadros em que o contrato original efetivamente redesenha.
            # Mudanca de clima/bioma deve sempre invalidar a chave.
            etapa=frame//23
            base=(etapa*43)%256
            fundo.fill((base,51+etapa,91))
            pygame.draw.rect(fundo,(245,12,63),(18,22,10,14))
            alvo.fill((0,0,0))
            if not cache.reusar(alvo,("cidade",etapa),True):
                alvo.blit(fundo,(0,0))
                cache.guardar(alvo,("cidade",etapa),True)
                fundos_redesenhados+=1
            ref=pygame.Surface((450,800)).convert()
            ref.fill((0,0,0))
            ref.blit(fundo,(0,0))
            self.assertEqual(rgba(alvo),rgba(ref),(frame,etapa))
            # Uma camada animada deve ser aplicada DEPOIS de guardar o fundo.
            pygame.draw.circle(alvo,(frame%255,201,52,255),
                               (frame%450,180),7)
        self.medicoes["cache_fundo_temporal"]={
            "quadros":80,"reconstrucoes":fundos_redesenhados,
            "mudancas_de_cenario":4,"periodo_original":5,
        }

    def test_camera_estado_e_rgba_em_120_quadros(self):
        from pixelrush_cinema_v3172 import CameraCinematica
        import pixelrush_qa_camera_native_auto_v327742 as native
        original=CameraCinematica.aplicar
        frame=pygame.Surface((450,800),pygame.SRCALPHA,32)
        for y in range(800):
            pygame.draw.line(frame,((y*7)%256,(y*29)%256,
                (y*43)%256,(y*31)%256),(0,y),(449,y))
        a,b=CameraCinematica(),CameraCinematica()
        jogador=SimpleNamespace(no_chao=True,rect=pygame.Rect(100,540,34,66))
        t=[]
        native._REPORT["selecionado"]=False
        native.instalar()
        try:
            for i in range(120):
                jogador.no_chao=(i//17)%2==0
                jogador.rect.centery=540+(i%17)*7
                vel=7.5+(i%31)*.42
                momento=(i//40)%2==1
                ativo=i%29!=0
                t0=time.perf_counter_ns()
                esperado=original(a,frame,jogador,vel,momento,ativo)
                obtido=CameraCinematica.aplicar(b,frame,jogador,vel,momento,ativo)
                t.append((time.perf_counter_ns()-t0)/1e6)
                self.assertEqual(rgba(esperado),rgba(obtido),i)
                self.assertEqual(a.zoom,b.zoom)
                self.assertEqual(a.foco_y,b.foco_y)
        finally:
            native.restaurar_para_teste()
        self.medicoes["camera_120_quadros"]={
            "amostras":len(t),"p50_ms":percentil(t,.50),
            "p95_ms":percentil(t,.95),"pixel_exato":True}

    def test_camera_queda_native_nao_duplica_fisica_visual(self):
        from pixelrush_cinema_v3172 import CameraCinematica
        import pixelrush_qa_camera_native_auto_v327742 as native
        original=CameraCinematica.aplicar
        a,b=CameraCinematica(),CameraCinematica()
        source=textura(450,800,True)
        jogador=SimpleNamespace(no_chao=False,rect=pygame.Rect(40,575,40,58))
        native.instalar()
        antigo=native._NATIVE
        class NativoFalho:
            def processar(self,*args,**kwargs):
                raise RuntimeError("driver injetado indisponivel")
        try:
            # Preaquecimento com a camera CPU sem troca de classe.
            for _ in range(10):
                original(a,source,jogador,velocidade=13)
                original(b,source,jogador,velocidade=13)
            native._NATIVE=NativoFalho()
            native._REPORT["selecionado"]=True
            esperado=original(a,source,jogador,velocidade=13)
            saida=CameraCinematica.aplicar(b,source,jogador,velocidade=13)
            self.assertEqual(rgba(esperado),rgba(saida))
            self.assertEqual(a.zoom,b.zoom)
            self.assertEqual(a.foco_y,b.foco_y)
            self.assertFalse(native._REPORT["selecionado"])
            self.assertGreaterEqual(native._REPORT["fallbacks"],1)
        finally:
            native._NATIVE=antigo
            native.restaurar_para_teste()


if __name__ == "__main__":
    unittest.main(verbosity=2)
