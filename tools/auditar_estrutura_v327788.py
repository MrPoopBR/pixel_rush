#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inventario somente leitura: modularizacao QA788, imports e arquivo historico.
Sem pygame, sem glob por frame, sem modificar saves ou assets.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROOT_QA={
    "pixelrush_qa_city_scaled_budget_v327785.py":
        "src/pixelrush/performance/city/cache_budget.py",
    "pixelrush_qa_city_opaque_overdraw_v327786.py":
        "src/pixelrush/performance/city/opaque_overdraw.py",
    "pixelrush_qa_city_technical_cover_v327787.py":
        "src/pixelrush/performance/city/technical_maps.py",
}
def hash_git(data):
    header=("blob "+str(len(data))+"\\0").encode().replace(b'\\0',b'\\x00')
    return hashlib.sha1(header+data).hexdigest()
def diagnostico():
    py=sorted(p.name for p in ROOT.glob("*.py"))
    manifest=json.loads(
        (ROOT/"docs/historico/MANIFESTO_MOVIMENTOS_v327788.json").read_text("utf8"))
    errors=[]
    archived=0
    for entry in manifest["arquivos"]:
        old,new=ROOT/entry["antigo"],ROOT/entry["novo"]
        if old.exists():errors.append("nota antiga ainda na raiz: "+entry["antigo"])
        if not new.is_file():errors.append("documento arquivado ausente: "+entry["novo"])
        elif hash_git(new.read_bytes())!=entry["sha"]:
            errors.append("documento historico alterado: "+entry["novo"])
        else:archived+=1
    for old,new in ROOT_QA.items():
        o,n=ROOT/old,ROOT/new
        if not o.is_file() or not n.is_file():
            errors.append("modulo de compatibilidade faltando: "+old)
        elif "import_module(" not in o.read_text("utf8"):
            errors.append("arquivo antigo nao eh adaptador: "+old)
    return {"versao":"3.277.88-QA","python_na_raiz":len(py),
            "arquivos_arquivados_integridade_ok":archived,
            "arquivos_manifesto":len(manifest["arquivos"]),
            "modulos_qa_migrados":len(ROOT_QA),
            "main_android_preservado":(ROOT/"main.py").is_file(),
            "motor_original_preservado":(ROOT/"PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py").is_file(),
            "erros":errors}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--check",action="store_true")
    args=a.parse_args()
    info=diagnostico()
    print(json.dumps(info,indent=2,ensure_ascii=False))
    if args.check and info["erros"]:
        return 1
    return 0

if __name__=="__main__":
    sys.exit(main())
