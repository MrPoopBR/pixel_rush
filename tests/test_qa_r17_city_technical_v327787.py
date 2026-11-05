# -*- coding: utf-8 -*-
"""QA787 LAB: hashes completos 260 RGBA, controle 785+786 e ganho tecnico."""
import json,os,subprocess,sys,tempfile,statistics,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame

class CityTechnicalQA787(unittest.TestCase):
    def test_gate_fora_do_frame_e_restauracao(self):
        pygame.init();pygame.display.set_mode((450,800))
        from pixelrush_qa_city_bootstrap_v327759 import instalar as boot,restaurar_para_teste as unboot
        from pixelrush_qa_city_scaled_budget_v327785 import instalar as budget,restaurar_para_teste as unbudget
        from pixelrush_qa_city_opaque_overdraw_v327786 import instalar as opaque,restaurar_para_teste as unopaque
        from pixelrush_qa_city_technical_cover_v327787 import instalar,restaurar_para_teste,diagnostico
        from pixelrush_city2_v3125 import CityPilotScene
        boot();budget()
        try:
            with patch.dict(os.environ,{'PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW':'1'}):
                opaque()
            original=(CityPilotScene.__init__,CityPilotScene.render_scene,CityPilotScene._render_chunk)
            with patch.dict(os.environ,{'PIXELRUSH_QA_CITY_TECH_COVER':'1'}):
                instalar()
            s=CityPilotScene()
            self.assertEqual(s._scaled_limit,20)
            self.assertEqual(set(s._qa_tech_cutoffs),{'geometry','material'})
            self.assertTrue(0<s._qa_tech_cutoffs['geometry']<500)
            self.assertTrue(0<s._qa_tech_cutoffs['material']<500)
            self.assertGreater(len(s._qa_tech_fx_bounds),0)
            self.assertGreater(diagnostico()['safe_scenes'],0)
            # Render completo com alfa oculto e estado arbitrario de entrada.
            for name in ('geometry','material','fxmask'):
                before=pygame.Surface((450,500),pygame.SRCALPHA,32)
                before.fill((113,37,191,0))
                after=before.copy()
                original[1](s,before,201.,47,.87,'tempestade',.37,False,name)
                s.render_scene(after,201.,47,.87,'tempestade',.37,False,name)
                self.assertEqual(pygame.image.tobytes(before,'RGBA'),
                                 pygame.image.tobytes(after,'RGBA'),name)
            # Trocar atlas near invalida gate geometry, sem alterar sprites.
            near=next(l for l in s.layers if l.name=='near')
            variant=near.variants[0]
            old=variant.geometry
            variant.geometry=old.copy()
            try:
                self.assertIsNotNone(s._qa_tech_sources.get('geometry'))
                a=pygame.Surface((450,500),pygame.SRCALPHA,32)
                b=a.copy()
                original[1](s,a,99.,12,.36,'limpo',.37,False,'geometry')
                s.render_scene(b,99.,12,.36,'limpo',.37,False,'geometry')
                self.assertEqual(pygame.image.tobytes(a,'RGBA'),
                                 pygame.image.tobytes(b,'RGBA'))
            finally:
                variant.geometry=old
            # Fora do render_scene nao ha aceleracao: preserva RGB oculto.
            v=next(l for l in s.layers if l.name=='far').variants[0]
            a=pygame.Surface((450,500),pygame.SRCALPHA,32)
            a.fill((123,41,98,0))
            b=a.copy()
            original[2](s,a,v,False,-125,42,.5,'chuva',.37,'fxmask',False)
            s._render_chunk(b,v,False,-125,42,.5,'chuva',.37,'fxmask',False)
            self.assertEqual(pygame.image.tobytes(a,'RGBA'),pygame.image.tobytes(b,'RGBA'))
            restaurar_para_teste()
            self.assertEqual((CityPilotScene.__init__,CityPilotScene.render_scene,
                              CityPilotScene._render_chunk),original)
        finally:
            restaurar_para_teste();unopaque();unbudget();unboot();pygame.quit()

    def test_mundo_130_quadros_260_rgba_e_ganho_repetido(self):
        with tempfile.TemporaryDirectory() as tmp:
            for light in (0,1):
                results={0:[],1:[]}
                for rep in range(2):
                    # Intercalar a ordem para reduzir efeito de temperatura/CPU.
                    for opt in ((0,1) if rep==0 else (1,0)):
                        dest=Path(tmp)/f'city_{light}_{rep}_{opt}.json'
                        env=os.environ.copy()
                        env.update(SDL_AUDIODRIVER='dummy',SDL_VIDEODRIVER='dummy',
                                   PYTHONPATH=str(ROOT))
                        subprocess.run([sys.executable,
                            str(ROOT/'qa_a54/benchmark_city_technical_v327787.py'),
                            '--limit','20','--opaque','1','--tech',str(opt),
                            '--light',str(light),'--output',str(dest)],
                            env=env,cwd=ROOT,stdout=subprocess.DEVNULL,
                            timeout=95,check=True)
                        results[opt].append(json.loads(dest.read_text('utf8')))
                for r in range(2):
                    a,b=results[0][r],results[1][r]
                    self.assertEqual(a['quadros_rgba'],260)
                    self.assertEqual(a['hashes_rgba'],b['hashes_rgba'],
                        ('RGBA do mundo nao-identico',light,r))
                    self.assertEqual(a['periodo_redesenho_preservado'],5)
                    self.assertEqual(b['periodo_redesenho_preservado'],5)
                    self.assertEqual(a['cache_maximo_observado'],b['cache_maximo_observado'])
                    self.assertEqual(a['opaque_stats']['chunks_hidden'],
                                     b['opaque_stats']['chunks_hidden'])
                    self.assertGreater(b['tech_stats']['clip_geo_mat'],90)
                    self.assertGreater(b['tech_stats']['clip_fxmask'],30)
                p50=lambda arr,key:statistics.median([x['timings'][key]['p50_ms']
                                                   for x in arr])
                base=p50(results[0],'fifth_total')
                candidate=p50(results[1],'fifth_total')
                self.assertLess(candidate,base*.97,
                    ('Sem ganho >=3% no quinto completo',light,base,candidate))
                tech_base=sum(p50(results[0],key) for key in
                              ('geometry','material','fxmask'))
                tech_after=sum(p50(results[1],key) for key in
                               ('geometry','material','fxmask'))
                self.assertLess(tech_after,tech_base*.9,
                    ('Sem ganho >=10% no conjunto tecnico',light,tech_base,tech_after))
                mem=statistics.median(x['memoria_rss_pico_kib']
                                      for x in results[1])-statistics.median(
                                      x['memoria_rss_pico_kib'] for x in results[0])
                self.assertLess(mem,3*1024)
                print('QA787',dict(light=light,RGBA=260,chunk_tech=b['tech_stats'],
                    fifth_base_ms=round(base,4),
                    fifth_qa_ms=round(candidate,4),
                    gain_pct=round(100*(1-candidate/base),2),
                    technical_base_ms=round(tech_base,4),
                    technical_qa_ms=round(tech_after,4),
                    technical_gain_pct=round(100*(1-tech_after/tech_base),2),
                    rss_delta_kib=mem),flush=True)

if __name__=='__main__':
    unittest.main(verbosity=2)
