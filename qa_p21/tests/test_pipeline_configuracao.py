from __future__ import annotations
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
YML=ROOT/'.github/workflows/p21-qa-independente.yml'

class TestManifestoPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow=YML.read_text(encoding='utf-8')
    def test_arquivo_existe(self): self.assertTrue(YML.is_file())
    def test_push_somente_na_branch_qa(self):
        # Compatibilidade da suite v1.1.0 com a execução automática isolada v1.3.0.
        self.assertIn('workflow_dispatch:',self.workflow)
        self.assertIn('  push:\n    branches:\n      - qa/p21-ci-isolado-v3.285.4', self.workflow)
        self.assertNotIn('  pull_request:', self.workflow)
        self.assertNotIn('  schedule:', self.workflow)
    def test_permissoes_minimas(self):
        self.assertIn('permissions:\n  contents: read',self.workflow)
        self.assertIn('persist-credentials: false',self.workflow)
    def test_actions_node24(self):
        for fragment in ('actions/checkout@v7','actions/setup-python@v7','actions/upload-artifact@v7'):
            self.assertIn(fragment,self.workflow)
    def test_matriz_isolada(self):
        for fragment in ('ubuntu-24.04','windows-2022',"python-version: '3.13.5'",'SDL_VIDEODRIVER: dummy'):
            self.assertIn(fragment,self.workflow)
    def test_sem_tokens_de_assinatura(self):
        for fragment in ('PIXELRUSH_KEYSTORE', 'GITHUB_TOKEN:', 'secrets.', 'git push'):
            self.assertNotIn(fragment,self.workflow)
    def test_saida_artifact_evidencia(self):
        self.assertIn('artifacts/',self.workflow)
        self.assertIn('retention-days: 14',self.workflow)

if __name__=='__main__': unittest.main()