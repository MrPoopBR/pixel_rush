# -*- coding: utf-8 -*-
"""QA761: aquecimento incremental dos tiles PROD SOMENTE durante menus.

O carregamento de producao continua sendo a fonte de verdade, com seu
SHA, descompactacao e fallback originais. Esta classe so le paginas de
arquivo e verifica SHA em blocos pequenos; nao faz pickle, SDL, sorteio,
thread, Pygame Surface nem altera estado de jogo.
"""
from collections import deque
import hashlib
from pathlib import Path

MAX_ARQUIVO_BYTES = 40 * 1024 * 1024
MAX_TOTAL_BYTES = 125 * 1024 * 1024
BLOCO_BYTES = 64 * 1024


class PrecargaTilesMenuQA:
    def __init__(self, arquivos=None, max_total_bytes=MAX_TOTAL_BYTES,
                 bloco_bytes=BLOCO_BYTES):
        if arquivos is None:
            from pixelrush_tiles_prod_v32777 import _DIR, _HASHES
            arquivos = tuple((nome, _DIR / (nome + '.tiles'), sha)
                             for nome, sha in _HASHES.items())
        self._fila = deque((str(nome), Path(caminho), str(sha))
                           for nome, caminho, sha in arquivos)
        self._atual = None
        self._teto = max(0, min(MAX_TOTAL_BYTES, int(max_total_bytes)))
        self._bloco = max(1, min(BLOCO_BYTES, int(bloco_bytes)))
        self._usados = 0
        self._resultados = []
        self._passos = 0
        self._finalizado = False

    @property
    def finalizado(self):
        return self._finalizado

    def _registrar(self, nome, estado, tamanho=0):
        self._resultados.append({'nome': nome, 'status': estado,
                                 'bytes': int(tamanho)})
        self._atual = None

    def passo(self):
        """No maximo 64 KiB de leitura e uma unica operacao de arquivo.

        Chamador autoriza somente menus. Nao se conserva descritor entre
        frames; quando sai do menu nao ha I/O nem arquivo aberto na corrida.
        """
        if self._finalizado:
            return False
        self._passos += 1
        if self._atual is None:
            if not self._fila:
                self._finalizado = True
                return False
            nome, caminho, sha = self._fila.popleft()
            try:
                st = caminho.stat()
                tamanho = st.st_size
                if tamanho <= 0 or tamanho > MAX_ARQUIVO_BYTES:
                    self._registrar(nome, 'fora_orcamento')
                    return True
                if self._usados + tamanho > self._teto:
                    self._registrar(nome, 'orcamento_total')
                    return True
                self._atual = (nome, caminho, sha, tamanho,
                               st.st_mtime_ns, 0, hashlib.sha256())
            except (OSError, ValueError, TypeError):
                self._registrar(nome, 'indisponivel')
                return True

        nome, caminho, sha, tamanho, modificado, offset, digest = self._atual
        try:
            anterior = caminho.stat()
            if (anterior.st_size, anterior.st_mtime_ns) != (tamanho, modificado):
                self._registrar(nome, 'alterado_durante_leitura')
                return True
            with caminho.open('rb') as arquivo:
                arquivo.seek(offset)
                dados = arquivo.read(min(self._bloco, tamanho - offset))
            posterior = caminho.stat()
            if ((posterior.st_size, posterior.st_mtime_ns) !=
                    (tamanho, modificado) or not dados):
                self._registrar(nome, 'alterado_durante_leitura')
                return True
            digest.update(dados)
            offset += len(dados)
            self._usados += len(dados)
            if offset == tamanho:
                self._registrar(nome, 'sha_ok' if digest.hexdigest() == sha
                                else 'sha_invalido', tamanho)
            else:
                self._atual = (nome, caminho, sha, tamanho,
                               modificado, offset, digest)
        except (OSError, ValueError, TypeError, MemoryError):
            self._registrar(nome, 'indisponivel')
        return True

    def diagnostico(self):
        return {
            'schema':'pixelrush.qa.tiles.menu.v327761',
            'finalizado':self._finalizado,
            'pendentes':len(self._fila) + int(self._atual is not None),
            'bytes_lidos':self._usados,
            'max_leitura_por_passo':self._bloco,
            'passos':self._passos,
            'superficies_criadas':0,
            'rng_usado':False,
            'arquivos':tuple(dict(x) for x in self._resultados),
            'atual':self._atual[0] if self._atual else None,
        }
