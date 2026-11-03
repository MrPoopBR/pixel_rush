# -*- coding: utf-8 -*-
"""QA 3.277.47 — atlas streaming e gates sem alterar simulacao."""
import os
import random
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from pixelrush_qa_atlas_io_v327747 import (BLOCO_BYTES,MAX_TOTAL_BYTES,
    preaquecer_arquivos_fora_do_jogo,diagnostico,instalar_no_boot_qa)


class AtlasIOQA747(unittest.TestCase):
    def test_boot_lendo_atlas_prod_sem_tocar_rng_ou_cenas(self):
        from pixelrush_atlas_prod_v32776 import _ATLAS,_HASHES
        import pygame
        antes=random.getstate()
        inicializado=pygame.display.get_init()
        out=preaquecer_arquivos_fora_do_jogo('CARREGANDO')
        self.assertTrue(out['preparado'],out)
        self.assertEqual(len([x for x in out['arquivos'] if x['status']=='sha_ok']),4)
        self.assertEqual(out['max_buffer_python_bytes'],64*1024)
        self.assertLessEqual(out['bytes_lidos'],MAX_TOTAL_BYTES)
        self.assertFalse(out['sorteio_usado'])
        self.assertEqual(out['superficies_criadas'],0)
        self.assertEqual(out['memoria_persistente_qa'],0)
        self.assertEqual(random.getstate(),antes)
        self.assertEqual(pygame.display.get_init(),inicializado)
        self.assertEqual(len(_HASHES),len(_HASHES.copy()))
        self.assertTrue(_ATLAS.is_dir())

    def test_quando_jogando_nao_le_atlas_nem_cria_ativos(self):
        out=preaquecer_arquivos_fora_do_jogo('JOGANDO')
        self.assertEqual(out['motivo'],'estado_proibido')
        self.assertFalse(out['preparado'])
        self.assertEqual(out['bytes_lidos'],0)

    def test_atlas_corrompido_nao_aprovado_e_limites(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            (p/'neve_lite.atlas').write_bytes(b'arquivo sem sha valido')
            out=preaquecer_arquivos_fora_do_jogo(
                'INICIO',('neve_lite',),diretorio=p,
                hashes={'neve_lite':hashlib.sha256(b'outro arquivo').hexdigest()})
            self.assertFalse(out['preparado'])
            self.assertEqual(out['arquivos'][0]['status'],'sha_invalido')
            valid=b'abc'
            (p/'neve_lite.atlas').write_bytes(valid)
            exp={'neve_lite':hashlib.sha256(valid).hexdigest()}
            too_small=preaquecer_arquivos_fora_do_jogo(
                'INICIO',('neve_lite',),diretorio=p,hashes=exp,max_total_bytes=2)
            self.assertFalse(too_small['preparado'])
            self.assertEqual(too_small['arquivos'][0]['status'],'orcamento_total')
            okay=preaquecer_arquivos_fora_do_jogo(
                'INICIO',('neve_lite','neve_lite'),diretorio=p,hashes=exp)
            self.assertTrue(okay['preparado'])
            self.assertEqual(len(okay['arquivos']),1)
            self.assertEqual(okay['bytes_lidos'],len(valid))

    def test_boot_env_desabilita_sem_modificar_render(self):
        prior=os.environ.get('PIXELRUSH_QA_ATLAS_IO_PREWARM')
        try:
            os.environ['PIXELRUSH_QA_ATLAS_IO_PREWARM']='0'
            state=instalar_no_boot_qa()
            self.assertFalse(state['executado'])
            self.assertEqual(diagnostico()['motivo'],'desativado_por_env')
        finally:
            if prior is None:os.environ.pop('PIXELRUSH_QA_ATLAS_IO_PREWARM',None)
            else:os.environ['PIXELRUSH_QA_ATLAS_IO_PREWARM']=prior


if __name__=='__main__':
    unittest.main(verbosity=2)
