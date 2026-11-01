"""Regressoes reais: Windows + CPython 3.9 + pygame 2.6.1.

Somente verifica inicializacao, checksum SHA e carregador assíncrono;
nao modifica dados do jogo nem executa saves.
"""
import hashlib
import io
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from pixelrush_hash_compat_v327725 import sha256_stream

RAIZ = Path(__file__).resolve().parents[2]
assert sys.version_info[:2] == (3, 9), sys.version
assert sys.platform == "win32", sys.platform
assert pygame.version.ver == "2.6.1", pygame.version.ver
pygame.init()
pygame.display.set_mode((450, 800))

# Python 3.9 nao implementa hashlib.file_digest; use os mesmos bytes SHA-256.
assert not hasattr(hashlib, "file_digest")
tamanho = 2 * 1024 * 1024 + 17
dados = b"PIXEL_RUSH_Windows_39" * (tamanho // len(b"PIXEL_RUSH_Windows_39") + 1)
dados = dados[:tamanho]
objeto = io.BytesIO(dados)
assert sha256_stream(objeto) == hashlib.sha256(dados).hexdigest()
assert objeto.tell() == len(dados)
objeto = io.BytesIO(b"PREFIX" + dados)
objeto.seek(6)
assert sha256_stream(objeto) == hashlib.sha256(dados).hexdigest()
assert objeto.tell() == len(dados) + 6

# Usa arquivos de release reais, nao apenas bytes artificiais.
amostras = [
    (RAIZ / "assets" / "buffers_prod_v32779", "manifest.json", "neve.pbuf"),
    (RAIZ / "assets" / "atlas_prod_v32776", "manifesto.json", "deserto.atlas"),
]
for pasta, manifesto, nome in amostras:
    esperado = json.loads((pasta / manifesto).read_text(encoding="utf8"))
    if "assets" in esperado:
        # Um manifesto pode armazenar hash por chave simples.
        colecao = esperado["assets"]
    else:
        colecao = esperado
    chave = nome.rsplit(".", 1)[0]
    info = colecao[chave]
    esperado_hash = info["sha256"] if isinstance(info, dict) else info
    with (pasta / nome).open("rb") as arquivo:
        assert sha256_stream(arquivo) == esperado_hash, nome

# O gerenciador deve funcionar em Windows sem chamar CDLL(None).
import pixelrush_buffers_prod_v327710 as buffers
gerenciador = buffers._Manager()
assert gerenciador._trim is None, "malloc_trim nao existe no Windows"
gerenciador.update(False, "cidade")
limite = time.monotonic() + 20
while time.monotonic() < limite and "neve" not in gerenciador.stats["loaded"]:
    time.sleep(.1)
assert "neve" in gerenciador.stats["loaded"], (
    "Prefetch deve validar o SHA-256 e carregar estado real com Python 3.9",
    gerenciador.stats,
)
pygame.quit()
print("APROVADO: Windows Py3.9 pygame2.6.1, SHA real, prefetch e CDLL protegido")
