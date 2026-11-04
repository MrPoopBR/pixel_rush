# -*- coding: utf-8 -*-
"""Perfil off-line de passes reais do World Cidade — QA v3.277.76.

Instrumenta somente na execução isolada dos testes; nenhuma mudança
no runtime do jogo, física, saves ou pipeline aprovado. Paridade RGBA.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import json
import statistics
import time
import unittest
from collections import defaultdict
from pathlib import Path
from functools import wraps
import pygame

PATH=Path(__file__).resolve().parents[1]/"qa-r11-city-hotspots-v327776.json"

def bytes_rgba(s):
    return pygame.image.tobytes(s,"RGBA")

class CidadeHotspotsQA776(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))
        from pixelrush_qa_city_bootstrap_v327759 import instalar
        instalar()

    @classmethod
    def tearDownClass(cls):
        from pixelrush_qa_city_bootstrap_v327759 import restaurar_para_teste
        restaurar_para_teste()
        pygame.quit()

    def test_passes_reais_e_rgba(self):
        from pixelrush_world_v3130 import LivingWorld
        from pixelrush_city2_v3125 import CityPilotScene
        from pixelrush_citylife_v3123 import CityLifeDirector
        from pixelrush_renderfx_v3125 import WorldDebris
        world=LivingWorld("cidade")
        world.lightweight=True
        original={}
        medidas=defaultdict(list)
        contagens=defaultdict(int)
        chamadas=(
          (LivingWorld,"_city_surface","city_surface"),
          (CityPilotScene,"render_scene","city_total"),
          (CityPilotScene,"_render_chunk","chunk"),
          (CityPilotScene,"_scaled_surface","scale_cache"),
          (CityPilotScene,"_draw_sprite","sprites_city"),
          (CityPilotScene,"_draw_train","train"),
          (CityLifeDirector,"draw_bridge_life","vehicles_people"),
          (CityLifeDirector,"draw_suspended_cables","cables"),
          (CityLifeDirector,"draw_pigeons","pigeons"),
          (CityLifeDirector,"draw_windows_lights","windows"),
          (CityLifeDirector,"draw_atmosphere","atmosphere"),
          (CityLifeDirector,"draw_wet_reflections","reflections"),
          (WorldDebris,"draw","debris"),
        )
        def wrapped(func,name):
            @wraps(func)
            def call(*args,**kwargs):
                ts=time.perf_counter_ns()
                try:return func(*args,**kwargs)
                finally:
                    medidas[name].append((time.perf_counter_ns()-ts)/1e6)
                    contagens[name]+=1
            return call
        try:
            # Aquecimento de caches antes da medicao.
            for k in range(4):
                world.update(6.5,0.0,"limpo",0.45)
                t=pygame.Surface((450,800)).convert()
                t.fill((13,31,71))
                world.draw(t)
            # RGBA com bytes ocultos preservados mesmo com wrappers.
            for flags in (0,pygame.SRCALPHA):
                destino=pygame.Surface((450,800),flags,32)
                destino.fill((40,60,80,0) if flags else (40,60,80))
                a=destino.copy()
                world.draw(a)
                for cls,method,name in chamadas:
                    key=(cls,method)
                    original[key]=getattr(cls,method)
                    setattr(cls,method,wrapped(original[key],name))
                try:
                    b=destino.copy()
                    world.draw(b)
                    self.assertEqual(bytes_rgba(a),bytes_rgba(b),
                                     ("desenho_rgba",flags))
                finally:
                    for (cls,method),func in reversed(list(original.items())):
                        setattr(cls,method,func)
                    original.clear()
            # Medição sem forçar redraw extra ou mudar período do jogo.
            for cls,method,name in chamadas:
                key=(cls,method)
                original[key]=getattr(cls,method)
                setattr(cls,method,wrapped(original[key],name))
            frames=[]
            for i in range(42):
                night=(0.,.36,.88)[(i//14)%3]
                climate=("limpo","chuva","tempestade")[(i//14)%3]
                for _ in range(5):
                    world.update(6.3,night,climate,.36)
                target=pygame.Surface((450,800)).convert()
                target.fill((15,36,59))
                start=time.perf_counter_ns()
                world.draw(target)
                frames.append((time.perf_counter_ns()-start)/1e6)
            result={"schema":"pixelrush.qa.r11.city.hotspots.v327776",
                "base":"LivingWorld cidade real v3125, leve, 5 updates/1 draw",
                "hardware_a54":False, "numero_frames":len(frames),
                "world_draw_p50_ms":round(statistics.median(frames),4),
                "frames":{"media_ms":round(statistics.mean(frames),4),
                          "p95_ms":round(sorted(frames)[int(.95*(len(frames)-1))],4)},
                "passes":{}}
            for name,times in medidas.items():
                result["passes"][name]={
                   "chamadas":contagens[name],
                   "ms_soma":round(sum(times),4),
                   "ms_por_chamada_p50":round(statistics.median(times),5),
                   "ms_por_chamada_p95":round(sorted(times)[int(.95*(len(times)-1))],5),
                   "media_por_world_draw_ms":round(sum(times)/len(frames),4)}
            PATH.write_text(json.dumps(result,indent=2),encoding="utf8")
            print("QA776 HOTSPOTS",json.dumps(result,sort_keys=True))
            self.assertEqual(len(frames),42)
            self.assertGreater(contagens["chunk"],0)
            self.assertGreater(contagens["city_total"],0)
        finally:
            for (cls,method),func in reversed(list(original.items())):
                setattr(cls,method,func)

if __name__=="__main__":unittest.main(verbosity=2)
