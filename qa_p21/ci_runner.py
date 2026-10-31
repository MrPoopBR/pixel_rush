#!/usr/bin/env python3
"""P21 CI 1.1.0: orquestrador independente, somente leitura do jogo e do tracker.

Não executa código de produção. Apenas sintaxe AST (quando fontes oficiais existirem),
regressões do próprio QA, auditoria XLSX e smoke SDL dummy. Salva JSON fora das entradas.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import traceback
import unittest
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from p21_auditor_tracker import read_tracker, analisar

EXPECTED_GAME_VERSION = 'v3.285.4'

def sha256_file(path: Path):
    digest=hashlib.sha256()
    with path.open('rb') as fh:
        for piece in iter(lambda: fh.read(1024*1024),b''):
            digest.update(piece)
    return digest.hexdigest()

def guarded_input(path: Path, kind: str):
    path=path.absolute()
    if path.is_symlink():
        raise ValueError(f'{kind} não aceita link simbólico')
    if not path.exists():
        raise FileNotFoundError(f'{kind} não encontrado')
    if kind == 'tracker' and not path.is_file():
        raise ValueError('Tracker deve ser XLSX regular')
    if kind == 'fonte' and not path.is_dir():
        raise ValueError('Fonte deve ser diretório')
    return path

def check_tracker(path: Path | None):
    if path is None:
        return {'estado':'nao_executado','motivo':'Tracker não fornecido; auditoria não conta para CI real'}
    before=sha256_file(path)
    try:
        data=analisar(read_tracker(path))
        state='aprovado' if data['aprovado'] else 'falha'
        return {'estado':state, 'verificacoes':len(data['verificacoes']),
                'falhas':data['erros'], 'origem_sha256':before,
                'origem_intocada':sha256_file(path)==before}
    except Exception as exc:
        return {'estado':'falha','erro':type(exc).__name__,'detalhe':str(exc)[:240],
                'origem_intocada':sha256_file(path)==before}

def check_pygame():
    os.environ.setdefault('SDL_VIDEODRIVER','dummy')
    os.environ.setdefault('SDL_AUDIODRIVER','dummy')
    os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')
    try:
        import pygame
        if pygame.version.ver != '2.5.8':
            return {'estado':'falha','motivo':'pygame-ce 2.5.8 obrigatório','encontrado':pygame.version.ver}
        pygame.init()
        try:
            surface=pygame.display.set_mode((64,64))
            surface.fill((12,34,56))
            pygame.draw.rect(surface,(255,120,0),pygame.Rect(8,8,20,20))
            cor=surface.get_at((10,10))[:3]
            outside=surface.get_at((1,1))[:3]
            ok=(cor == (255,120,0) and outside == (12,34,56))
        finally:
            pygame.quit()
        return {'estado':'aprovado' if ok else 'falha','versao':pygame.version.ver,
                'driver':'dummy','pixels_verificados':ok}
    except Exception as exc:
        return {'estado':'falha','erro':type(exc).__name__,'detalhe':str(exc)[:240]}

def source_version(source):
    # Extração estática. Não importa nem executa código do jogo.
    for node in source.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id=='VERSAO' for t in targets):
                value=node.value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    return value.value
    return None

def check_game_sources(root: Path | None, version=EXPECTED_GAME_VERSION):
    if root is None:
        return {'estado':'nao_executado','motivo':'Fontes LIMPA/DEV v3.285.4 não fornecidas; teste do jogo bloqueado'}
    files=sorted(root.rglob('*.py'))
    if not files:
        return {'estado':'bloqueado','motivo':'Nenhum arquivo Python encontrado'}
    if len(files)>1500:
        return {'estado':'bloqueado','motivo':'Limite de 1500 arquivos atingido'}
    versions={'LIMPA':[],'DEV':[]}
    summaries=[]
    for path in files:
        if path.is_symlink() or not path.is_file():
            return {'estado':'bloqueado','motivo':'Fonte contém link simbólico', 'arquivo':path.name}
        rel=path.relative_to(root).as_posix()
        raw=path.read_bytes()
        if len(raw)>8*1024*1024:
            return {'estado':'bloqueado','motivo':'Fonte maior que 8 MiB', 'arquivo':rel}
        try:
            text=raw.decode('utf-8-sig')
            tree=ast.parse(text, filename=rel)
        except (SyntaxError, UnicodeError) as exc:
            return {'estado':'falha','motivo':'Erro de sintaxe/UTF-8', 'arquivo':rel,
                    'erro':type(exc).__name__, 'linha':getattr(exc,'lineno',None)}
        declared=source_version(tree)
        variant=('LIMPA' if 'LIMPA' in rel.upper() else 'DEV' if 'DEV' in rel.upper() else None)
        if variant and declared and declared.startswith(version):
            versions[variant].append(rel)
        summaries.append({'arquivo':rel,'sha256':hashlib.sha256(raw).hexdigest()})
    if not all(versions.values()):
        return {'estado':'bloqueado', 'motivo':f'Pares LIMPA/DEV {version} não confirmados por VERSAO',
                'candidatos_confirmados':versions, 'arquivos_parseados':len(summaries)}
    return {'estado':'aprovado_estatico','arquivos_parseados':len(summaries),
            'versao':version, 'fontes_confirmadas':versions,
            'manifesto_sha256':hashlib.sha256(json.dumps(summaries, sort_keys=True).encode()).hexdigest(),
            'nota':'AST apenas; não é execução, replay, CI de jogabilidade ou hardware'}

def run_regression_tests():
    suite=unittest.TestLoader().discover(str(HERE/'tests'), pattern='test_*.py',top_level_dir=str(HERE.parent))
    import io
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    return {'estado':'aprovado' if result.wasSuccessful() and result.testsRun>0 else 'falha',
            'executados':result.testsRun,'falhas':len(result.failures), 'erros':len(result.errors),
            'ignorados':len(result.skipped),'log':stream.getvalue()[-10000:]}

def execute(tracker=None,source_root=None):
    results={
      'schema':'pixelrush.p21.qa_ci.v1',
      'pipeline':'P21 CI Independente v1.1.0',
      'gerado_utc':datetime.now(timezone.utc).isoformat(),
      'ambiente':{'python':platform.python_version(),'sistema':platform.system(),
                  'arch':platform.machine(),'SDL_VIDEODRIVER':os.environ.get('SDL_VIDEODRIVER','dummy')},
      'escopo':'QA isolado, sem importação/execução de produção',
      'regressoes_qa':run_regression_tests(),
      'smoke_pygame':check_pygame(),
      'auditoria_tracker':check_tracker(tracker),
      'sintaxe_fontes':check_game_sources(source_root),
      'gates_oficiais':{'P21':'1/4 (25%), sem alteração','P23':'2/4 (50%), sem alteração'},
    }
    results['qa_local_aprovado']=(results['regressoes_qa']['estado']=='aprovado'
                                  and results['smoke_pygame']['estado']=='aprovado'
                                  and results['auditoria_tracker']['estado'] not in {'falha'}
                                  and results['sintaxe_fontes']['estado'] not in {'falha'})
    results['ci_github_executado']=(os.environ.get('GITHUB_ACTIONS')=='true')  # Não prova gate de jogo.
    return results

def avaliar_resultado(result, require_source=False, require_tracker=False):
    faltantes=[name for name,needed,state in [
        ('tracker',require_tracker,result['auditoria_tracker']['estado']),
        ('fontes',require_source,result['sintaxe_fontes']['estado'])]
        if needed and state not in ('aprovado','aprovado_estatico')]
    estado='APROVADO_QA_ISOLADO' if result['qa_local_aprovado'] and not faltantes else 'FALHA_OU_BLOQUEADO'
    return estado, faltantes

def main(argv=None):
    ap=argparse.ArgumentParser(description='P21: CI offline independente; não altera produção/pets')
    ap.add_argument('--tracker',type=Path)
    ap.add_argument('--source-root',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--require-source',action='store_true')
    ap.add_argument('--require-tracker',action='store_true')
    args=ap.parse_args(argv)
    inputs=[]
    try:
        tracker=guarded_input(args.tracker,'tracker') if args.tracker else None
        source=guarded_input(args.source_root,'fonte') if args.source_root else None
        inputs=[p for p in (tracker,source) if p]
        target=args.output.absolute()
        if target.exists():
            ap.error('Arquivo de evidência já existe; não sobrescrever')
        if any(p==target or p in target.parents for p in inputs):
            ap.error('Relatório de saída não pode ficar dentro de qualquer pasta de fonte')
        if tracker and target.parent==tracker.parent:
            ap.error('Relatório não pode ficar na pasta de origem do tracker')
        target.parent.mkdir(parents=True,exist_ok=True)
        result=execute(tracker,source)
        result['requisitos']={'tracker':args.require_tracker,'fontes':args.require_source}
        result['resultado_final'], result['faltantes']=avaliar_resultado(
            result, require_source=args.require_source, require_tracker=args.require_tracker)
        with target.open('x',encoding='utf-8') as out:
            json.dump(result,out,ensure_ascii=False,indent=2)
            out.write('\n')
        print(json.dumps({'resultado':result['resultado_final'],'evidencia':target.name,
                          'testes':result['regressoes_qa']['executados'],
                          'fontes':result['sintaxe_fontes']['estado'],
                          'tracker':result['auditoria_tracker']['estado']},ensure_ascii=False))
        return 0 if result['resultado_final']=='APROVADO_QA_ISOLADO' else 2
    except (OSError,ValueError) as exc:
        print(f'BLOQUEADO: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 2
if __name__=='__main__':
    raise SystemExit(main())