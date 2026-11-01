#!/usr/bin/env python3
"""Empacotamento da PIXEL RUSH para PyCharm sem alterar codigo/recursos.

Organiza exclusivamente a distribuicao ZIP. O jogo mantem os mesmos
caminhos de modulos, recursos e configuracoes do commit Windows aprovado.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

BASE_SHA = "f5202e8599356ddb83beca7a61f81a314d09cda1"
VERSION = "3.277.25"
REVISAO_PACOTE = "r1"
PREFIXO = "PixelRush_v%s_PYCHARM/" % VERSION
ZIP_NOME = "PIXEL_RUSH_v%s_COMPLETO_PYCHARM_%s.zip" % (VERSION, REVISAO_PACOTE)
ARQUIVOS_EXTRAS_PERMITIDOS = {
    ".github/scripts/empacotar_pycharm_v327725.py",
    ".github/workflows/empacotar-pycharm-v327725.yml",
}

def git(*args):
    return subprocess.check_output(["git"] + list(args))

def eh_documentacao(nome):
    if "/" in nome:
        return False
    if nome in ("README.md", "LEIA_ME_PUBLICACAO.md"):
        return True
    return bool(re.match(r"^(NOTAS_|NOTAS_DA_VERSAO_|RELATORIO_|AUDITORIA_|SIMULACAO_).*\.(md|txt)$", nome, re.I))

def texto_guia():
    return """PIXEL RUSH v3.277.25 — PROJETO COMPLETO PARA PYCHARM / WINDOWS
PACOTE: r1 (somente organizacao do ZIP; codigo do jogo INALTERADO)
CODIGO DE ORIGEM: f5202e8599356ddb83beca7a61f81a314d09cda1

INICIO RAPIDO NO WINDOWS:
  1. Extraia o ZIP inteiro em uma pasta nova.
  2. Dê dois cliques em INSTALAR_E_JOGAR.bat, ou use JOGAR_WINDOWS.bat
     caso as dependencias ja estejam instaladas no Python.
  3. No PyCharm: abra esta pasta e execute JOGAR.py.
     Alternativa identificada como na primeira entrega:
     PixelRush_v3.277.25_LIMPA.py (so um encaminhador para JOGAR.py).
  4. Python 3.9+; no Windows houve QA com Python 3.9.13,
     pygame 2.6.1 e NumPy 1.26.4. requirements.txt instala pygame-ce.

ESTRUTURA:
  JOGAR.py, JOGAR_WINDOWS.bat, *.py  -> edicao LIMPA atual.
  assets/, assets_android/, assets_i18n_v3247/,
  world_art_v3106/, world_parallax_v3112/ -> recursos INALTERADOS.
  DOCUMENTACAO/    -> notas/relatorios apenas; nao sao usados pelo jogo.
  .github/         -> testes e workflows originais preservados.
  p4a-recipes/     -> compilacao Android, preservada.
  MANIFESTO_SHA256_ENTREGA.json -> inventario e SHA-256 de cada arquivo.
  VERSAO_ATUAL.txt -> numero da versao do JOGO (v3.277.25).

LIMPA x DEV:
  Esta e a edicao LIMPA v3.277.25 da linha de publicacao Android
  com compatibilidade Windows. A DEV v3.277.0 do ZIP de referencia
  continua SEPARADA; nenhuma DEV atualizada foi inventada ou ativada.
  Nao execute main.py para jogar: a entrada LIMPA e JOGAR.py.

SISTEMAS QUE PERMANECEM DESATIVADOS:
  A revisao nao altera nenhum flag ou configuracao. Lasers Jetpack,
  obstaculos direcionados e API online continuam bloqueados na
  edicao LIMPA, como no codigo de origem. Acoes desativadas anteriormente
  nao foram reativadas. Skins e biomas limitados permanecem como antes.
  Salvamentos do usuario nao foram incluidos, modificados ou migrados.

IMPORTANTE:
  Os arquivos Python, assets e configuracoes de jogo conservam
  byte a byte os arquivos Git do commit Windows aprovado.
  So houve organizacao de notas no ZIP e criacao de guia,
  iniciador opcional e manifesto de integridade.
  A validacao Windows anterior foi de 18 segundos de inicializacao;
  nao equivale a homologacao de todas as corridas nem Play Store.
"""

def bat_instalar():
    return (r"""@echo off
setlocal
cd /d "%~dp0"
title PIXEL RUSH v3.277.25 - Instalar e jogar
if not exist ".venv\Scripts\python.exe" (
  echo Criando ambiente Python isolado...
  where py >nul 2>nul
  if not errorlevel 1 py -3.9 -m venv .venv >nul 2>nul
  if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv >nul 2>nul
  if not exist ".venv\Scripts\python.exe" python -m venv .venv >nul 2>nul
)
if not exist ".venv\Scripts\python.exe" (
  echo ERRO: Python 3.9+ nao encontrado.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo ERRO ao instalar as dependencias. Confira a internet.
  pause
  exit /b 1
)
echo Abrindo PIXEL RUSH LIMPA v3.277.25...
".venv\Scripts\python.exe" JOGAR.py
if errorlevel 1 (
  echo O jogo encontrou um erro. Veja as mensagens acima.
  pause
  exit /b 1
)
endlocal
""").replace("\n", "\r\n")

def alias_limpa():
    return """# -*- coding: utf-8 -*-
\"\"\"Alias LIMPA para PyCharm: mesma entrada JOGAR.py, nenhum jogo alternativo.\"\"\"
from pathlib import Path
import runpy
if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "JOGAR.py"), run_name="__main__")
"""

def organizar():
    base = Path.cwd()
    alterados = set(git("diff", "--name-only", BASE_SHA, "HEAD").decode().splitlines())
    if not alterados.issubset(ARQUIVOS_EXTRAS_PERMITIDOS):
        raise RuntimeError("Codigo ou recursos diferentes da v3.277.25: " +
                           ", ".join(sorted(alterados - ARQUIVOS_EXTRAS_PERMITIDOS)))
    nomes = [s.decode("utf-8") for s in git("ls-files", "-z").split(b"\0") if s]
    assert nomes and "JOGAR.py" in nomes and "buildozer.spec" in nomes
    assert "PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py" in nomes
    assert "pixelrush_tutorial_guia_prod_v327724.py" in nomes
    caminhos = {}
    for nome in sorted(nomes):
        arquivo = base / nome
        if not arquivo.is_file():
            raise RuntimeError("Arquivo rastreado ausente: " + nome)
        destino = ("DOCUMENTACAO/" + nome if eh_documentacao(nome) else nome)
        if destino in caminhos:
            raise RuntimeError("Destino duplicado: " + destino)
        caminhos[destino] = (nome, arquivo.read_bytes())

    extras = {
        "LEIA_ME_PRIMEIRO.txt": texto_guia().encode("utf-8"),
        "INSTALAR_E_JOGAR.bat": bat_instalar().encode("utf-8"),
        "PixelRush_v3.277.25_LIMPA.py": alias_limpa().encode("utf-8"),
    }
    if set(extras).intersection(caminhos):
        raise RuntimeError("Extras colidem com codigo original")
    for dest, data in extras.items():
        caminhos[dest] = ("gerado apenas no ZIP", data)
    manifesto = {
        "versao_jogo": "v" + VERSION,
        "revisao_entrega": REVISAO_PACOTE,
        "commit_codigo_invariavel": BASE_SHA,
        "origem_referencia": "PixelRush_v3.277.0_COMPLETO_LIMPA_DEV.zip",
        "dev_ativada": False,
        "arquivos": {
            dest: {"sha256": hashlib.sha256(data).hexdigest(),
                   "bytes": len(data), "origem": origem}
            for dest, (origem, data) in sorted(caminhos.items())
        },
    }
    caminhos["MANIFESTO_SHA256_ENTREGA.json"] = (
        "gerado apenas no ZIP",
        (json.dumps(manifesto, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    destino = base / "dist" / ZIP_NOME
    destino.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destino, "w", allowZip64=True) as arq:
        for relative, (origin, data) in sorted(caminhos.items()):
            info = zipfile.ZipInfo(PREFIXO + relative, date_time=(2026, 11, 1, 12, 0, 0))
            info.compress_type = (
                zipfile.ZIP_STORED if Path(relative).suffix.lower() in (
                    ".png", ".ogg", ".mp3", ".zip", ".jpg", ".jpeg") else zipfile.ZIP_DEFLATED
            )
            info.external_attr = (0o644 << 16)
            arq.writestr(info, data, compresslevel=6)
    with zipfile.ZipFile(destino) as arq:
        assert arq.testzip() is None
        assert len(arq.namelist()) == len(caminhos)
        for relative, (_, data) in caminhos.items():
            actual = arq.read(PREFIXO + relative)
            if hashlib.sha256(actual).digest() != hashlib.sha256(data).digest():
                raise AssertionError("ZIP divergiu do original: " + relative)
    print("APROVADO: ZIP completo e integro:", destino)
    print("ARQUIVOS:", len(caminhos), "| git:", len(nomes))
    print("CODIGO/FLAGS DE JOGO: byte a byte identicos ao commit", BASE_SHA)
    print("SHA256 ZIP:", hashlib.sha256(destino.read_bytes()).hexdigest())
    print("BYTES ZIP:", destino.stat().st_size)

if __name__ == "__main__":
    organizar()
