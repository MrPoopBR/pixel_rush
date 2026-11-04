# -*- coding: utf-8 -*-
"""QA776: prototipo SOMENTE BENCHMARK, nao muda o mundo do jogo.

Fonte REAL da Cidade v3125, compor SRCALPHA de 450x500 em RGB16/RGB24/RGB32
e provar bytes exatos ao omitir linhas com alfa zero. O gate de ganho
pode falhar sem mudar flags, gameplay ou aparencia do APK.
"""
import os,json,statistics,time,unittest
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'qa-r11-world-bands-v327776.json'

def rgba(s):return pygame.image.tobytes(s,'RGBA')
def bands(source):
    arr=pygame.surfarray.pixels_alpha(source)
    try:
        used=np.any(arr!=0,axis=0)
    finally:
        del arr
    rows=[];start=None
    for y,present in enumerate(used):
        if present and start is None:
            start=y
        if not present and start is not None:
            rows.append((start,y-start));start=None
    if start is not None:
        rows.append((start,len(used)-start))
    return rows,sum(n for _,n in rows)/source.get_height()

def clipped(dest,source,areas):
    for y,height in areas:
        dest.blit(source,(0,230+y),(0,y,450,height))

class WorldBandsR11QA776(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init();pygame.display.set_mode((450,800))
        from pixelrush_qa_city_bootstrap_v327759 import instalar
        instalar()
    @classmethod
    def tearDownClass(cls):
        from pixelrush_qa_city_bootstrap_v327759 import restaurar_para_teste
        restaurar_para_teste();pygame.quit()

    def test_cidade_real_composicao_rgba_e_bench(self):
        from pixelrush_world_v3130 import LivingWorld
        world=LivingWorld('cidade')
        results=[]
        for i,(night,climate,phase) in enumerate(((0.,'limpo',.35),(.65,'chuva',.62),(1.,'limpo',.18))):
            world.update(6.0,night,climate,phase)
            source=world._city_surface('image')
            self.assertEqual(source.get_size(),(450,500))
            self.assertTrue(source.get_flags() & pygame.SRCALPHA)
            areas,occupancy=bands(source)
            for bpp in (16,24,32):
                base=pygame.Surface((450,800),0,bpp)
                base.fill((24+i*29,57,103))
                before=base.copy();after=base.copy()
                before.blit(source,(0,230))
                clipped(after,source,areas)
                self.assertEqual(rgba(before),rgba(after),(i,bpp,areas))
                old=[];new=[];bounded=[]
                bbox=source.get_bounding_rect(min_alpha=1)
                test_bbox=base.copy()
                test_bbox.blit(source,(bbox.x,230+bbox.y),bbox)
                self.assertEqual(rgba(before),rgba(test_bbox),(i,bpp,'bbox'))
                for j in range(140):
                    t=time.perf_counter_ns()
                    before.blit(source,(0,230))
                    old.append(time.perf_counter_ns()-t)
                    t=time.perf_counter_ns()
                    clipped(after,source,areas)
                    new.append(time.perf_counter_ns()-t)
                    t=time.perf_counter_ns()
                    box=source.get_bounding_rect(min_alpha=1)
                    test_bbox.blit(source,(box.x,230+box.y),box)
                    bounded.append(time.perf_counter_ns()-t)
                self.assertEqual(rgba(before),rgba(after),(i,bpp,'repeated'))
                med_old=statistics.median(old)
                med_new=statistics.median(new)
                med_bounded=statistics.median(bounded)
                results.append({'caso':i,'bpp':bpp,'occupancy_rows':round(occupancy,3),
                                'bands':len(areas),'old_ms':round(med_old/1e6,4),
                                'new_ms':round(med_new/1e6,4),
                                'speedup':round(med_old/med_new,3),
                                'bbox_auto_ms':round(med_bounded/1e6,4),
                                'bbox_auto_speedup':round(med_old/med_bounded,3),
                                'RGBA_exato':True})
        REPORT.write_text(json.dumps({'schema':'pixelrush.qa.r11.world_bands.v327776',
            'integrado':False,'hardware_A54':False,'amostras':results},indent=2))
        print('R11 world bands',json.dumps(results))
        self.assertEqual(len(results),9)

if __name__=='__main__':unittest.main(verbosity=2)
