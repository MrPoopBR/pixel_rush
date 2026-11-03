# -*- coding: utf-8 -*-
"""QA761: pré-aquecimento parcelado de tiles no menu, invariantes de jogo."""
import hashlib
import os
from pathlib import Path
import random
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
from pixelrush_qa_tiles_menu_v327761 import PrecargaTilesMenuQA
from pixelrush_qa_precarregamento_visual_v327757 import PrecargaVisuaisQA

class TilesMenu761(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((450,800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_preleitura_progressiva_menu_sem_rng_sdl_ou_corrida(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz=Path(tmp)
            dados={'neve':b'N'*170001,'deserto':b'D'*92003,
                   'cidade_futurista':b'F'*303}
            for nome,valor in dados.items():
                (raiz/(nome+'.tiles')).write_bytes(valor)
            fake=types.ModuleType('pixelrush_tiles_prod_v32777')
            fake._DIR=raiz
            fake._HASHES={nome:hashlib.sha256(d).hexdigest()
                          for nome,d in dados.items()}
            acoes=[]
            def skin(nome):
                acoes.append(('skin',nome))
                random.random()
            def pet(nome):
                acoes.append(('pet',nome))
                random.random()
            before=random.getstate()
            with patch.dict(sys.modules,{'pixelrush_tiles_prod_v32777':fake}),\
                 patch.dict(os.environ,{'PIXELRUSH_QA_TILES_IO_MENU':'1',
                                        'PIXELRUSH_QA_TILES_IO_PREWARM':'1'}):
                item=PrecargaVisuaisQA(
                    'AZUL',frozenset(('AZUL','VERDE','ROSA')),
                    'BOLHA',skin,pet,aquecer_tiles=True)
                for _ in range(100):
                    self.assertFalse(item.passo('JOGANDO'))
                self.assertEqual(acoes,[])
                self.assertNotIn('tiles_io',item.diagnostico())
                anterior=0
                for quadro in range(48):
                    item.passo('INICIO')
                    diag=item.diagnostico()
                    if 'tiles_io' in diag:
                        atual=diag['tiles_io']['bytes_lidos']
                        self.assertLessEqual(atual-anterior,64*1024,
                                             msg='mais de um bloco por frame')
                        anterior=atual
                resultado=item.diagnostico()
            self.assertEqual([x[0] for x in acoes],
                             ['skin','skin','skin','pet'])
            self.assertEqual(resultado['tiles_io']['pendentes'],0)
            self.assertTrue(resultado['tiles_io']['finalizado'])
            self.assertEqual(resultado['tiles_io']['superficies_criadas'],0)
            self.assertFalse(resultado['tiles_io']['rng_usado'])
            self.assertEqual(resultado['tiles_io']['bytes_lidos'],
                             sum(map(len,dados.values())))
            self.assertEqual(
                {x['nome']:x['status'] for x in resultado['tiles_io']['arquivos']},
                {nome:'sha_ok' for nome in dados})
            self.assertEqual(random.getstate(),before)

    def test_mutacao_durante_sha_nao_aprova(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'neve.tiles'
            original=b'A'*(2*64*1024+9)
            path.write_bytes(original)
            hash_original=hashlib.sha256(original).hexdigest()
            p=PrecargaTilesMenuQA(
                [('neve',path,hash_original)],bloco_bytes=64*1024)
            self.assertTrue(p.passo())
            self.assertEqual(p.diagnostico()['bytes_lidos'],64*1024)
            path.write_bytes(b'Z'*len(original))
            st=path.stat()
            os.utime(path,ns=(st.st_atime_ns,st.st_mtime_ns+2000000000))
            self.assertTrue(p.passo())
            self.assertEqual(p.diagnostico()['arquivos'][0]['status'],
                             'alterado_durante_leitura')
            self.assertFalse(any(x['status']=='sha_ok'
                                 for x in p.diagnostico()['arquivos']))

    def test_limites_ausente_arquivo_e_sha_errado(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            invalid=root/'deserto.tiles'
            invalid.write_bytes(b'bytes-invalidos')
            missing=root/'neve.tiles'
            item=PrecargaTilesMenuQA(
                [('deserto',invalid,'f'*64),('neve',missing,'f'*64)],
                max_total_bytes=300,bloco_bytes=64*1024)
            while item.passo():
                pass
            r=item.diagnostico()
            self.assertTrue(r['finalizado'])
            self.assertEqual([x['status'] for x in r['arquivos']],
                             ['sha_invalido','indisponivel'])
            self.assertLessEqual(r['max_leitura_por_passo'],64*1024)
            limited=PrecargaTilesMenuQA(
                [('deserto',invalid,'f'*64)],max_total_bytes=1)
            limited.passo()
            self.assertEqual(limited.diagnostico()['arquivos'][0]['status'],
                             'orcamento_total')

    def test_tiles_prod_reais_sha_completos_em_ate_32_passos(self):
        # Gate real contra os binarios oficiais: nenhuma aproximação
        # por fixture para estes três hashes de producao.
        from pixelrush_tiles_prod_v32777 import _DIR, _HASHES
        self.assertEqual(set(_HASHES),{'neve','deserto','cidade_futurista'})
        esperados=sum((_DIR/(nome+'.tiles')).stat().st_size for nome in _HASHES)
        self.assertLessEqual(esperados,125*1024*1024)
        random_antes=random.getstate()
        leitor=PrecargaTilesMenuQA()
        passos=0
        while not leitor.finalizado and passos<32:
            anterior=leitor.diagnostico()['bytes_lidos']
            leitor.passo()
            atual=leitor.diagnostico()['bytes_lidos']
            self.assertLessEqual(atual-anterior,64*1024)
            passos+=1
        r=leitor.diagnostico()
        self.assertTrue(r['finalizado'],msg='tile oficial nao aquecido em 32 quadros de menu')
        self.assertEqual(r['bytes_lidos'],esperados)
        self.assertEqual(len(r['arquivos']),len(_HASHES))
        self.assertTrue(all(x['status']=='sha_ok' for x in r['arquivos']),r)
        self.assertEqual(random_antes,random.getstate())
        self.assertEqual(r['superficies_criadas'],0)
        print('QA_TILES_PROD_MENU_GATE',{'passos':passos,'bytes':esperados,
                                         'sha_ok':len(_HASHES)})

    def test_boot_qa_transfere_tiles_ao_menu_sem_rehash(self):
        import pixelrush_qa_atlas_io_v327747 as atlas
        with patch.dict(os.environ,{
            'PIXELRUSH_QA_ATLAS_IO_PREWARM':'1',
            'PIXELRUSH_QA_ATLAS_IO_DEDUP':'1',
            'PIXELRUSH_QA_TILES_IO_MENU':'1',
            'PIXELRUSH_QA_TILES_IO_PREWARM':'1'}):
            result=atlas.instalar_no_boot_qa()
        self.assertFalse(result['executado'])
        self.assertEqual(result['motivo'],'tiles_adiados_para_menu')
        self.assertTrue(result['atlas_prod_preparados_pelo_carregador_original'])

if __name__=='__main__':
    unittest.main(verbosity=2)
