"""Compatibilidade de atlas/binarios em CPython 3.9+ e NumPy 1.x/2.x.

A verificacao criptografica SHA-256 permanece obrigatoria nos chamadores.
"""
import hashlib
import pickle


def sha256_stream(arquivo):
    """Hash do stream a partir da posicao atual, com blocos no Python 3.9."""
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


class NumPyCompatUnpickler(pickle.Unpickler):
    """Ler snapshots NumPy 2 no NumPy 1 sem transformar nenhum dado.

    Aplica o alias legado apenas quando o modulo numpy._core esta ausente.
    Os demais globais do pickle mantem a resolucao padrao original.
    """

    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except ModuleNotFoundError:
            if module == 'numpy._core' or module.startswith('numpy._core.'):
                antigo = 'numpy.core' + module[len('numpy._core'):]
                return super().find_class(antigo, name)
            raise


def load_verified_pickle(arquivo):
    """Desserializar somente arquivos locais previamente verificados por SHA."""
    return NumPyCompatUnpickler(arquivo).load()
