from __future__ import annotations
import copy
import json
from pathlib import Path
import unittest
from qa_p21.p21_auditor_tracker import analisar

FIXTURE=Path(__file__).resolve().parents[1]/'fixtures'/'tracker_estrutura_sintetica.json'

class TestTrackerP21(unittest.TestCase):
    def setUp(self):
        self.sheet=copy.deepcopy(json.loads(FIXTURE.read_text(encoding='utf-8')))

    def falha(self, fragmento):
        outcome=analisar(self.sheet)
        self.assertFalse(outcome['aprovado'])
        self.assertTrue(any(fragmento in x for x in outcome['erros']),outcome['erros'])

    def test_baseline(self): self.assertTrue(analisar(self.sheet)['aprovado'])
    def test_plano_duplicado(self):
        self.sheet['Backlog 30 planos'][1][0]='P30'; self.falha('30 IDs')
    def test_dependencia_inexistente(self):
        self.sheet['Backlog 30 planos'][1][5]='P99'; self.falha('Dependências')
    def test_autodependencia(self):
        self.sheet['Backlog 30 planos'][1][5]='P01'; self.falha('Dependências')
    def test_ciclo_dependencia(self):
        self.sheet['Backlog 30 planos'][20][5]='P19'
        self.sheet['Backlog 30 planos'][19][5]='P20'; self.falha('Grafo')
    def test_gate_fake(self):
        self.sheet['Progresso Gates Offline'][12][3]=4; self.falha('Contagens')
    def test_percentual_fake(self):
        self.sheet['Progresso Gates Offline'][11][6]=0.75; self.falha('Contagens')
    def test_homologacao_p23_falsa(self):
        for row in self.sheet['Gates QA Offline 32854']:
            if row and row[0]=='P23' and 'autênticos' in str(row[1]):
                row[2]='Aprovado offline'; break
        self.falha('P23 sem homologação')
    def test_subgate_historico_mal_classificado(self):
        self.sheet['Gates QA Offline 32854'][36][0]='P21'; self.falha('Subgate P23')
    def test_status_invalido(self):
        self.sheet['Backlog 30 planos'][1][6]='Aprovado sem prova'; self.falha('Estados permitidos')
    def test_p23_nao_avanca_sem_prova(self):
        self.sheet['Progresso Gates Offline'][12][6]=1; self.falha('P23 continua')
    def test_resumo_falso(self):
        self.sheet['Visão Geral'][3][1]=31; self.falha('Indicadores')
    def test_p21_nao_avanca_sem_prova(self):
        self.sheet['Progresso Gates Offline'][11][6]=0.5; self.falha('P21 continua')

if __name__=='__main__': unittest.main()