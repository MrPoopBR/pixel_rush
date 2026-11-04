# -*- coding: utf-8 -*-
"""Experimento QA776 (nao integrado): comparar source rect vs views SDL.

ROI e pixels identicos da vinheta GameFeel real; o experimento NAO altera
nenhuma classe runtime. Resultados gate para decidir integracao v777.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
os.environ["PIXELRUSH_QA_ANDROID"]="1"
import json, random, statistics,time,unittest
from pathlib import Path
import pygame
from pixelrush_gamefeel_v3129 import GameFeel
import pixelrush_qa_r11_vinheta_v327776 as qa
OUT=Path(__file__).resolve().parents[1]/"qa-vinheta-views-bench-v327776.json"

def bytes_rgba(s):return pygame.image.tobytes(s,"RGBA")

class ViewsCandidata776(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
    @classmethod
    def tearDownClass(cls):pygame.quit()
    def test_real_views_rgba_e_tempo(self):
        v=GameFeel()._vinheta
        views=tuple((v.subsurface(r),r.topleft) for r in qa._BORDAS)
        rng=random.Random(327776)
        tempos=[]
        for bpp,flags in ((16,0),(24,0),(32,0),(32,pygame.SRCALPHA)):
            a=pygame.Surface((450,800),flags,bpp)
            a.fill((55,101,143,0) if flags else (55,101,143))
            for _ in range(85):
                x,y=rng.randrange(450),rng.randrange(800)
                color=(rng.randrange(256),rng.randrange(256),rng.randrange(256))
                pygame.draw.rect(a,(*color,rng.randrange(256)) if flags else color,(x,y,13,29))
            b=a.copy()
            def before():
                for r in qa._BORDAS:
                    a.blit(v,r.topleft,r)
            def after():
                for surf,pos in views:
                    b.blit(surf,pos)
            before();after()
            self.assertEqual(bytes_rgba(a),bytes_rgba(b),("rgba_first",bpp,flags))
            aa,bb=[],[]
            for _ in range(750):
                t=time.perf_counter_ns();before();aa.append(time.perf_counter_ns()-t)
                t=time.perf_counter_ns();after();bb.append(time.perf_counter_ns()-t)
            self.assertEqual(bytes_rgba(a),bytes_rgba(b),("rgba_750",bpp,flags))
            median_old=statistics.median(aa)
            median_new=statistics.median(bb)
            tempos.append({"bpp":bpp,"srcalpha":bool(flags),
                "old_ns":round(median_old,1),
                "views_ns":round(median_new,1),
                "ganho":round(median_old/median_new,4),
                "rgba_igual":True})
        OUT.write_text(json.dumps({"schema":"pixelrush.qa.r11.views.experiment.v327776",
            "integrado":False,"android_medido":False,"resultados":tempos},indent=2),encoding="utf8")
        print("QA776 VIEWS EXPERIMENTO",json.dumps(tempos))
        self.assertEqual(len(tempos),4)

if __name__=="__main__":unittest.main(verbosity=2)
