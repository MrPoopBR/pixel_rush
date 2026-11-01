"""Compatibilidade SHA-256 para Python 3.9+ sem alterar a validacao dos assets.

hashlib.file_digest entrou no Python 3.11; a alternativa processa o arquivo
em blocos, mantendo a posicao final do stream e o mesmo SHA-256.
"""
import hashlib


def sha256_stream(arquivo):
    acelerado = getattr(hashlib, 'file_digest', None)
    if acelerado is not None:
        return acelerado(arquivo, 'sha256').hexdigest()
    resumo = hashlib.sha256()
    while True:
        bloco = arquivo.read(1024 * 1024)
        if not bloco:
            break
        resumo.update(bloco)
    return resumo.hexdigest()
