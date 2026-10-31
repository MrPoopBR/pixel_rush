"""Proteção de saves v3.252: transação de arquivo e backup de última versão válida.

Uma geração .bak por save; nunca usa RNG do jogo e não migra o esquema JSON.
Falha no arquivo principal permite leitura de .bak apenas se ele for válido.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile

LIMITE_LEITURA = 32 * 1024 * 1024


def _ler_objeto(caminho):
    caminho = Path(caminho)
    if caminho.is_symlink() or not caminho.is_file() or caminho.stat().st_size > LIMITE_LEITURA:
        raise ValueError('Arquivo ausente, link ou tamanho excessivo')
    with caminho.open('r', encoding='utf-8') as arq:
        dado = json.load(arq)
    if not isinstance(dado, dict):
        raise ValueError('Save precisa ser objeto JSON')
    return dado


def ler_save_protegido(caminho):
    """Retorna dados do principal ou do backup; não regrava o arquivo corrompido."""
    caminho = Path(caminho)
    try:
        return _ler_objeto(caminho)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        return _ler_objeto(Path(str(caminho) + '.bak'))


def _sync_dir(pasta):
    """Best effort: fsync do diretório em sistemas que suportam."""
    if os.name == 'nt' or not hasattr(os, 'O_DIRECTORY'):
        return
    try:
        fd = os.open(str(pasta), os.O_DIRECTORY | os.O_RDONLY)
        try: os.fsync(fd)
        finally: os.close(fd)
    except OSError:
        pass


def _transacao_bytes(destino, conteudo):
    destino = Path(destino)
    # Temporário NO MESMO diretório para os.replace permanecer atômico.
    fd, nome = tempfile.mkstemp(prefix='.' + destino.name + '.', suffix='.tmp', dir=str(destino.parent))
    try:
        with os.fdopen(fd, 'wb') as arq:
            arq.write(conteudo)
            arq.flush()
            os.fsync(arq.fileno())
        os.replace(nome, destino)
        _sync_dir(destino.parent)
    finally:
        try: os.unlink(nome)
        except FileNotFoundError: pass


def salvar_save_protegido(caminho, dados):
    """Backup de save *válido*, seguido da troca atômica do principal.

    Falha antes do replace mantém o principal anterior. Se o principal já está
    ilegível, o backup é mantido para não perder a última cópia recuperável.
    Retorna bool; o chamador legado lida silenciosamente com erros de IO.
    """
    caminho = Path(caminho)
    if caminho.is_symlink() or Path(str(caminho) + '.bak').is_symlink():
        raise OSError('Não sobrescreve save ou backup por link simbólico')
    # Validação/serialização COMPLETA antes de tocar no arquivo atual.
    if not isinstance(dados, dict):
        raise TypeError('Save precisa ser dicionário')
    conteudo = json.dumps(dados, indent=4, ensure_ascii=True, allow_nan=False).encode('utf-8')
    if caminho.exists():
        try:
            _ler_objeto(caminho)
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
            pass  # Não transformar arquivo inválido em novo backup.
        else:
            # Cópia fiel do JSON anterior (preserva saves antigos sem migração).
            _transacao_bytes(Path(str(caminho) + '.bak'), caminho.read_bytes())
    _transacao_bytes(caminho, conteudo)
    return True
