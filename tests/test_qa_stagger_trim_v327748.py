# -*- coding: utf-8 -*-
"""QA 3.277.48: RGBA do clima, RSS e agendamento fora do quinto quadro."""
import os
import random
import sys
import unittest
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from weakref import WeakSet

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame

from pixelrush_qa_cache_trim_v327748 import EscalonadorTrimQA

class FakeWorld:
    def __init__(self,bioma='cidade'):
        self.biome=bioma
        self.props_cache={(name,i):i for i,name in enumerate(('cidade','neve','deserto'))}
        self.cache=OrderedDict((name,pygame.Surface((30,30)))
                               for name in ('cidade','neve','deserto'))
        for nome in ('fx_cache','normal_cache','material_cache',
                     'flow_cache','geometry_cache'):
            setattr(self,nome,{x:x for x in ('cidade','neve','deserto')})
        self._qa_mirror_props={('cidade',0):1,('neve',0):2}
        self._qa_deform_buffers={('cidade',0):1,('neve',0):2}
        self._city_surfaces={('image',False):1,('normal',False):2}
        self.city2=SimpleNamespace(_scaled=OrderedDict((i,i) for i in range(14)))

class StaggerQA748(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_rgba_clima_original_versus_opt_mais_de_100_quadros(self):
        from pixelrush_world_v3130 import LivingWorld
        from pixelrush_qa_performance_integrated_v327742 import _weather_cached
        original=LivingWorld._weather
        base=pygame.Surface((450,800),pygame.SRCALPHA)
        output=base.copy()
        state=random.getstate()
        try:
            for biome in ('cidade','neve','deserto'):
                for clima in ('limpo','chuva','tempestade','chuva_acida',
                              'neve','nevasca','areia','tempestade_areia',
                              'cinzas','chuva_meteoros','vento',
                              'vento_folhas','polen','brisa_celeste'):
                    for frame in (0,1,8,35,94,211):
                        world=SimpleNamespace(biome=biome,climate=clima,frame=frame)
                        base.fill((16+frame%17,36,92,255))
                        output.blit(base,(0,0))
                        original(world,base)
                        _weather_cached(world,output)
                        self.assertEqual(pygame.image.tobytes(base,'RGBA'),
                                         pygame.image.tobytes(output,'RGBA'),
                                         (biome,clima,frame))
        finally:
            self.assertEqual(random.getstate(),state)

    def test_sem_pressao_ou_multiplas_varreduras(self):
        a=FakeWorld()
        fundo={'cidade':1,'neve':2}
        worker=EscalonadorTrimQA(limite_por_passo=3)
        self.assertFalse(worker.iniciar(WeakSet((a,)),fundo,550,560))
        self.assertTrue(worker.iniciar(WeakSet((a,)),fundo,900,560))
        self.assertFalse(worker.iniciar(WeakSet((a,)),fundo,900,560))
        while worker.ativo:
            worker.passo()
        self.assertEqual(set(a.cache),{'cidade'})
        self.assertEqual(set(fundo),{'cidade'})
        self.assertEqual(len(a.city2._scaled),14)
        self.assertTrue(worker.concluidos)
        self.assertGreater(worker.passos,1)

    def test_multinstancia_bioma_trocado_durante_varredura(self):
        a=FakeWorld('cidade')
        b=FakeWorld('neve')
        source={'cidade':1,'neve':2,'deserto':3}
        worker=EscalonadorTrimQA(limite_por_passo=2)
        self.assertTrue(worker.iniciar(WeakSet((a,b)),source,900,560))
        worker.passo()
        b.biome='deserto'
        for _ in range(300):
            worker.passo()
            if not worker.ativo:
                break
        self.assertFalse(worker.ativo)
        self.assertIn('deserto',b.cache)
        self.assertIn('cidade',a.cache)
        self.assertIn('deserto',source)
        self.assertEqual(len(a.city2._scaled),14)
        self.assertEqual(len(b.city2._scaled),8)

    def test_integracao_180_flip_nao_limpa_no_quinto(self):
        import pixelrush_qa_performance_integrated_v327742 as perf
        import pixelrush_world_v3130 as world_module
        fake=FakeWorld()
        previous_mem=perf._memory_mib
        prior=os.environ.get('PIXELRUSH_QA_STAGGER_TRIM')
        os.environ['PIXELRUSH_QA_STAGGER_TRIM']='1'
        perf.restaurar_para_teste()
        try:
            perf.instalar()
            perf._memory_mib=lambda:900.
            perf._WORLDS.add(fake)
            perf._LAST_STATUS['frames']=0
            with patch.object(world_module,'_SOURCE',{'cidade':1,'neve':2}):
                for _ in range(180):
                    pygame.display.flip()
                self.assertIn('neve',fake.cache)
                self.assertTrue(perf._TRIMMER.ativo)
                for _ in range(31):
                    pygame.display.flip()
                self.assertNotIn('neve',fake.cache)
                self.assertIn('cidade',fake.cache)
                self.assertIn(('image',False),fake._city_surfaces)
                self.assertNotIn(('normal',False),fake._city_surfaces)
                self.assertEqual(len(fake.city2._scaled),14)
                self.assertGreater(perf.diagnostico()['limpeza_parcelada_qa']['passos_ultima_varredura'],0)
                self.assertFalse(perf.diagnostico()['cache_trim_fallback'])
        finally:
            perf._memory_mib=previous_mem
            perf.restaurar_para_teste()
            if prior is None:os.environ.pop('PIXELRUSH_QA_STAGGER_TRIM',None)
            else:os.environ['PIXELRUSH_QA_STAGGER_TRIM']=prior

    def test_desativar_restabelece_caminho_original(self):
        import pixelrush_qa_performance_integrated_v327742 as perf
        fake=FakeWorld()
        prior=os.environ.get('PIXELRUSH_QA_STAGGER_TRIM')
        old_mem=perf._memory_mib
        os.environ['PIXELRUSH_QA_STAGGER_TRIM']='0'
        perf.restaurar_para_teste()
        try:
            perf.instalar()
            perf._memory_mib=lambda:900.
            perf._WORLDS.add(fake)
            perf._LAST_STATUS['frames']=0
            for _ in range(180):
                pygame.display.flip()
            self.assertIsNone(perf._TRIMMER)
            self.assertNotIn('neve',fake.cache)
            self.assertIn('cidade',fake.cache)
        finally:
            perf._memory_mib=old_mem
            perf.restaurar_para_teste()
            if prior is None:os.environ.pop('PIXELRUSH_QA_STAGGER_TRIM',None)
            else:os.environ['PIXELRUSH_QA_STAGGER_TRIM']=prior

if __name__=='__main__':
    unittest.main(verbosity=2)
