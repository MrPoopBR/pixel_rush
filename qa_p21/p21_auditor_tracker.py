#!/usr/bin/env python3
"""PIXEL RUSH P21: auditoria independente (somente leitura) do tracker XLSX.

Não importa nem executa código da PIXEL RUSH. Não modifica o XLSX.
Suporta Python 3.10+ sem dependências. Não representa homologação do jogo/CI.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET
import zipfile

S = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
PR = '{http://schemas.openxmlformats.org/package/2006/relationships}'
VALID_STATUSES = {'Planejado', 'Em execução', 'Concluído'}
GATE_STATUSES = {'Aprovado offline', 'Em investigação', 'Evidência anterior',
                 'Pendente investigação', 'Pendente revisão', 'Pendente hardware'}
EM_INVESTIGACAO = {'Em investigação', 'Evidência anterior', 'Pendente investigação'}
PATTERN_ID = re.compile(r'P(?:0[1-9]|[12][0-9]|30)$')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def col_index(address):
    m = re.match(r'([A-Z]+)', address)
    if not m:
        raise ValueError('Referência inválida')
    n = 0
    for ch in m[1]:
        n = n * 26 + (ord(ch) - 64)
    return n-1


def parse_cell(c, shared):
    t = c.get('t')
    if t == 'inlineStr':
        return ''.join(x.text or '' for x in c.iter(S+'t'))
    v = c.find(S+'v')
    if v is None:
        return None
    text = v.text or ''
    if t == 's':
        return shared[int(text)]
    if t in ('str', 'e'):
        return text
    if t == 'b':
        return text == '1'
    try:
        n = float(text)
        return int(n) if n.is_integer() else n
    except ValueError:
        return text


def read_tracker(path: Path) -> dict[str, list[list]]:
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError('CRC inválido no XLSX')
        wb_root = ET.fromstring(z.read('xl/workbook.xml'))
        rel_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rels = {r.get('Id'):r.get('Target') for r in rel_root}
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            shared = [''.join(t.text or '' for t in si.iter(S+'t')) for si in root.findall(S+'si')]
        out = {}
        for s in wb_root.findall('.//'+S+'sheet'):
            rel = rels[s.get(R+'id')]
            part = rel.lstrip('/') if rel.startswith('/') else 'xl/' + rel
            root = ET.fromstring(z.read(part))
            rows = {}
            width = 0
            for row in root.findall('.//'+S+'sheetData/'+S+'row'):
                number = int(row.get('r'))
                values = {}
                for cell in row.findall(S+'c'):
                    ci = col_index(cell.get('r'))
                    values[ci] = parse_cell(cell, shared)
                    width = max(width, ci+1)
                rows[number] = values
            height = max(rows, default=0)
            out[s.get('name')] = [[rows.get(r, {}).get(c) for c in range(width)] for r in range(1, height+1)]
        return out


def at(matrix, row, col):
    return matrix[row-1][col-1] if len(matrix) >= row and len(matrix[row-1]) >= col else None


def analisar(sheets):
    errors, checks, notes = [], [], []
    def check(label, ok, detail=''):
        checks.append({'verificacao':label, 'resultado':'OK' if ok else 'FALHA', 'detalhe':detail})
        if not ok:
            errors.append(f'{label}: {detail}')
    required = ['Visão Geral', 'Backlog 30 planos', 'Fases e ordem',
                'Progresso Gates Offline', 'Gates QA Offline 32854']
    missing = [x for x in required if x not in sheets]
    check('Abas obrigatórias', not missing, ', '.join(missing))
    if missing:
        return {'aprovado':False, 'erros':errors, 'verificacoes':checks, 'observacoes':notes}

    backlog = [x for x in sheets['Backlog 30 planos'][1:] if x and x[0] is not None]
    ids = [str(x[0]) for x in backlog]
    plan = {str(x[0]):x for x in backlog}
    check('30 IDs únicos e consecutivos', len(ids)==30 and len(set(ids))==30 and set(ids)=={f'P{i:02}' for i in range(1,31)}, f'IDs={len(ids)}, únicos={len(set(ids))}')
    origem = Counter(x[4] for x in backlog)
    check('18 originais + 12 novos', origem['original']==18 and origem['novo']==12, str(dict(origem)))
    status = Counter(x[6] for x in backlog)
    check('Estados permitidos e distribuição', set(status)<=VALID_STATUSES and status['Em execução']==10 and status['Planejado']==20 and status['Concluído']==0, str(dict(status)))
    check('Prioridades válidas', all(x[3] in {'P0','P1','P2','P3'} for x in backlog), '')
    check('Fases válidas', all(x[2] in {'A','B','C','D','E','F'} for x in backlog), '')
    check('Percentuais no intervalo', all(isinstance(x[7],(int,float)) and 0 <= x[7] <= 1 for x in backlog), '')
    geral = sheets['Visão Geral']
    expected = {'Planos totais':len(backlog), 'Planos originais':origem['original'], 'Novos planos':origem['novo'],
                'Em execução':status['Em execução'], 'Concluídos':status['Concluído'], 'Planejados':status['Planejado']}
    got = {str(row[0]):row[1] for row in geral if len(row)>1 and row[0] in expected}
    check('Indicadores do resumo coerentes', got==expected, f'esperado={expected}, encontrado={got}' if got!=expected else '')
    invalid_deps = []
    deps = {}
    for x in backlog:
        pid = str(x[0]); found = [s.strip() for s in str(x[5] or '').split(',') if s.strip()]
        deps[pid] = found
        invalid_deps += [f'{pid}->{dep}' for dep in found if dep not in plan or dep==pid]
    check('Dependências existentes e sem autorreferência', not invalid_deps, ', '.join(invalid_deps))
    visited, visiting, cycles = set(),set(),[]
    def visit(pid):
        if pid in visiting:
            cycles.append(pid)
            return
        if pid in visited:
            return
        visiting.add(pid)
        for dep in deps.get(pid, []):
            if dep in plan: visit(dep)
        visiting.remove(pid)
        visited.add(pid)
    for pid in ids: visit(pid)
    check('Grafo de dependências sem ciclos', not cycles, ', '.join(cycles))

    gate_sheet = sheets['Gates QA Offline 32854']
    # A linha 37 é subgate histórico extra NÃO incluído na fórmula do placar oficial.
    official = [x for x in gate_sheet[3:36] if x and x[0] is not None]
    unrecognized = [(str(x[0]),str(x[2])) for x in official if str(x[2]) not in GATE_STATUSES]
    check('Classificação de 33 gates oficiais válida', len(official)==33 and not unrecognized, str(unrecognized))
    progress = [x for x in sheets['Progresso Gates Offline'][4:14] if x and x[0] is not None]
    check('Dez planos monitorados, sem repetição', len(progress)==10 and len(set(x[0] for x in progress))==10, str(len(progress)))
    mismatches=[]
    for row in progress:
        pid = row[0]
        related=[x for x in official if x[0]==pid]
        counts=(len(related), sum(x[2]=='Aprovado offline' for x in related),
                sum(x[2] in EM_INVESTIGACAO for x in related),
                sum(x[2] not in EM_INVESTIGACAO and x[2]!='Aprovado offline' for x in related))
        reported = tuple(row[2:6])
        if counts != reported:
            mismatches.append(f'{pid}: apurado={counts}, tracker={reported}')
        if len(related) and (not isinstance(row[6],(int,float)) or abs(row[6]-counts[1]/counts[0])>1e-9):
            mismatches.append(f'{pid}: % diferente')
        if pid in plan:
            if abs(float(plan[pid][7])-float(row[6]))>1e-9 or plan[pid][6]!=row[7]:
                mismatches.append(f'{pid}: backlog não coincide com placar')
    check('Contagens e percentuais dos gates conferem', not mismatches, '; '.join(mismatches))
    # Sem prova física/autêntica, estes gates não devem ser classificados como aprovados.
    high_risk = []
    for g in official:
        gate_name = str(g[1]).lower()
        if g[0]=='P23' and any(s in gate_name for s in ['autênticos', 'queda real']):
            if g[2]=='Aprovado offline': high_risk.append(str(g[1]))
    check('P23 sem homologação de saves autênticos/energia', not high_risk, ','.join(high_risk))
    p23=next((x for x in progress if x[0]=='P23'), None)
    check('P23 continua em 2/4 gates', p23 is not None and list(p23[2:7])==[4,2,1,1,0.5], str(p23[2:7] if p23 else 'não encontrado'))
    p21=next((x for x in progress if x[0]=='P21'), None)
    check('P21 continua em 1/4 gates', p21 is not None and list(p21[2:7])==[4,1,2,1,0.25], str(p21[2:7] if p21 else 'não encontrado'))
    excluded = gate_sheet[36] if len(gate_sheet)>36 else []
    check('Subgate P23 adicional separado do placar', len(excluded)>2 and excluded[0]=='P23' and excluded[2]=='Aprovado offline', str(excluded[:3]))
    notes += ['Esta auditoria verifica consistência documental do tracker, não executa o jogo.',
              'Não certifica CI, gravação/replay, desempenho ou hardware.',
              'Saves históricos autênticos não disponíveis; P23 não avançou.']
    return {'aprovado':not errors, 'erros':errors, 'verificacoes':checks, 'observacoes':notes,
            'planos':{'total':len(ids), 'originais':origem['original'], 'novos':origem['novo'],
                       'em_execucao':status['Em execução'], 'planejados':status['Planejado'],
                       'concluidos':status['Concluído']},
            'gates':{'P21':{'aprovados':1,'total':4}, 'P23':{'aprovados':2,'total':4}}}


class TesteAuditor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = read_tracker(Path(__file__).resolve().parent / 'tracker_amostra.xlsx') if (Path(__file__).resolve().parent/'tracker_amostra.xlsx').exists() else None

    def setUp(self):
        if self.base is None:
            self.skipTest('Informe --tracker para testes integrados; sem fixture interna')
        self.x = copy.deepcopy(self.base)

    def assertFalha(self, termo):
        res=analisar(self.x)
        self.assertFalse(res['aprovado'])
        self.assertTrue(any(termo in e for e in res['erros']), res['erros'])

    def test_baseline_valido(self):
        self.assertTrue(analisar(self.x)['aprovado'])
    def test_duplicacao_de_plano(self):
        self.x['Backlog 30 planos'][1][0]='P30'; self.assertFalha('30 IDs')
    def test_dependencia_inexistente(self):
        self.x['Backlog 30 planos'][1][5]='P99'; self.assertFalha('Dependências')
    def test_autodependencia(self):
        self.x['Backlog 30 planos'][1][5]='P01'; self.assertFalha('Dependências')
    def test_ciclo(self):
        self.x['Backlog 30 planos'][20][5]='P19'; self.x['Backlog 30 planos'][19][5]='P20'; self.assertFalha('Grafo')
    def test_contagem_gate(self):
        self.x['Progresso Gates Offline'][12][3]=4; self.assertFalha('Contagens')
    def test_percentual_incoerente(self):
        self.x['Progresso Gates Offline'][11][6]=0.75; self.assertFalha('Contagens')
    def test_gate_autentico_falsamente_aprovado(self):
        for row in self.x['Gates QA Offline 32854']:
            if row and row[0]=='P23' and 'autênticos' in str(row[1]):
                row[2]='Aprovado offline'; break
        self.assertFalha('P23 sem homologação')
    def test_artefato_externo_incluido_indevidamente(self):
        self.x['Gates QA Offline 32854'][36][0]='P21'; self.assertFalha('Subgate P23')
    def test_status_invalido(self):
        self.x['Backlog 30 planos'][1][6]='Aprovado sem prova'; self.assertFalha('Estados permitidos')
    def test_p23_falseamento_de_progresso(self):
        self.x['Progresso Gates Offline'][12][6]=1; self.assertFalha('P23 continua')
    def test_resumo_incoerente(self):
        self.x['Visão Geral'][3][1]=31; self.assertFalha('Indicadores')


def main():
    ap=argparse.ArgumentParser(description='P21: conferir tracker sem modificá-lo')
    ap.add_argument('--tracker',required=True, type=Path)
    ap.add_argument('--saida',type=Path, help='JSON em nova pasta, nunca no diretório do XLSX')
    ap.add_argument('--testar', action='store_true', help='Testes de mutação sem arquivos originais')
    args=ap.parse_args()
    if args.saida and args.saida.resolve().parent == args.tracker.resolve().parent:
        ap.error('A saída deve ficar em pasta separada do tracker de origem')
    if args.saida and args.saida.exists():
        ap.error('Não sobrescreve relatórios existentes')
    before=sha256(args.tracker)
    sheets=read_tracker(args.tracker)
    result=analisar(sheets)
    result.update({'ferramenta':'P21 Auditor Tracker v1.0.0','origem_nome':args.tracker.name,
                   'origem_sha256':before,'emissao_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
                   'abas_encontradas':len(sheets)})
    if args.testar:
        TesteAuditor.base=sheets
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(TesteAuditor)
        # Subclasse TesteAuditor setUpClass é ignorado para preservar a referência em memória.
        TesteAuditor.setUpClass=classmethod(lambda cls: None)
        replay=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(suite)
        result['testes_mutacao']={'executados':replay.testsRun,'falhas':len(replay.failures)+len(replay.errors),
                                   'aprovados':replay.wasSuccessful()}
        if not replay.wasSuccessful(): result['aprovado']=False
    after=sha256(args.tracker)
    result['origem_intocada']=before==after
    if not result['origem_intocada']: result['aprovado']=False
    if args.saida:
        args.saida.parent.mkdir(parents=True,exist_ok=True)
        args.saida.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('verificacoes','observacoes')},ensure_ascii=False,indent=2))
    return 0 if result['aprovado'] else 1

if __name__=='__main__': sys.exit(main())