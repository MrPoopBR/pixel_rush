#!/usr/bin/env python3
"""Adaptador para GitHub Actions: argumentos nunca são interpretados por shell."""
from __future__ import annotations
import os
from pathlib import Path
import sys
from qa_p21.ci_runner import main

def safe_relative(raw: str):
    if not raw: return None
    repo=Path.cwd().resolve()
    user_path=Path(raw)
    if user_path.is_absolute() or '..' in user_path.parts:
        raise ValueError('Forneça apenas caminho relativo dentro do repositório')
    candidate=repo/user_path
    if not candidate.resolve().is_relative_to(repo):
        raise ValueError('Caminho não pode sair do repositório')
    return str(candidate)

def entrypoint():
    args=['--output','artifacts/P21_QA_RESULTADO.json']
    try:
        tr=safe_relative(os.getenv('P21_TRACKER_PATH',''))
        src=safe_relative(os.getenv('P21_SOURCE_ROOT',''))
    except ValueError as exc:
        print('ERRO: ',exc,file=sys.stderr);return 2
    if tr: args+=['--tracker',tr]
    if src: args+=['--source-root',src]
    if os.getenv('P21_REQUIRE_SOURCE','false').lower()=='true': args.append('--require-source')
    if os.getenv('P21_REQUIRE_TRACKER','false').lower()=='true': args.append('--require-tracker')
    return main(args)
if __name__=='__main__': raise SystemExit(entrypoint())