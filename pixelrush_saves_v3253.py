"""v3.253 — histórico de até três backups válidos e diagnóstico local read-only.

Não modifica estrutura do save, não lê diretórios remotos e não usa RNG.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from pixelrush_saves_v3252 import _ler_objeto, _transacao_bytes, LIMITE_LEITURA

GERACOES = 3  # .bak, .bak.1 e .bak.2


def _candidatos(caminho):
    base = Path(caminho)
    return [base, Path(str(base) + '.bak')] + [Path(str(base) + '.bak.' + str(i)) for i in range(1, GERACOES)]


def ler_save_protegido(caminho):
    """Escolhe primeiro principal válido, depois backups do mais recente ao mais antigo."""
    ultimo = None
    for arquivo in _candidatos(caminho):
        try:
            return _ler_objeto(arquivo)
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
            ultimo = exc
    raise ValueError('Nenhum save JSON válido encontrado') from ultimo


def salvar_save_protegido(caminho, dados):
    """Roda apenas backups válidos ao salvar um principal válido.

    Se o principal estiver quebrado, preserva toda a cadeia de recuperação.
    Escrita segue a rotina transacional v3.252 (fsync + replace).
    """
    base = Path(caminho)
    arquivos = _candidatos(base)
    if any(p.is_symlink() for p in arquivos):
        raise OSError('Links simbólicos não são aceitos para saves ou backups')
    if not isinstance(dados, dict):
        raise TypeError('Save precisa ser dicionário')
    conteudo = json.dumps(dados, indent=4, ensure_ascii=True, allow_nan=False).encode('utf-8')
    if len(conteudo) > LIMITE_LEITURA:
        raise ValueError('Save excede limite de segurança de 32 MiB')
    # Completar a validação antes de tocar em qualquer arquivo.
    try:
        _ler_objeto(base)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        pass
    else:
        # Copia da geração mais antiga para a mais antiga seguinte. Não
        # propagamos fontes corrompidas para não apagar versões recuperáveis.
        for i in range(len(arquivos) - 1, 1, -1):
            origem, destino = arquivos[i - 1], arquivos[i]
            try:
                _ler_objeto(origem)
            except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
                continue
            _transacao_bytes(destino, origem.read_bytes())
        _transacao_bytes(arquivos[1], base.read_bytes())
    _transacao_bytes(base, conteudo)
    return True


def auditar_save(caminho):
    """Auditoria sem escrita; resumos, hashes e indicadores, nunca dados pessoais."""
    relatorio = {'schema':'pixelrush.save_audit.v2','geracoes':GERACOES,'arquivos':[],
                 'selecionado':None,'recuperavel':False,'avisos':[]}
    hashes = {}
    for index, caminho_arq in enumerate(_candidatos(caminho)):
        item = {'papel':'principal' if index == 0 else f'backup_{index}',
                'arquivo':Path(caminho_arq).name,'estado':'ausente'}
        caminho_arq = Path(caminho_arq)
        try:
            if caminho_arq.is_symlink():
                item['estado']='link_recusado'
            elif caminho_arq.exists():
                dados=_ler_objeto(caminho_arq)
                raw=caminho_arq.read_bytes()
                hash_=hashlib.sha256(raw).hexdigest()
                item.update(estado='valido',bytes=len(raw),sha256=hash_,
                            chaves=len(dados),campos_basicos={
                              k: type(dados[k]).__name__ for k in ('moedas_totais','recorde','upgrades') if k in dados})
                if hash_ in hashes:
                    item['duplicado_de']=hashes[hash_]
                    relatorio['avisos'].append('Cópias idênticas: ' + item['arquivo'])
                else:
                    hashes[hash_]=item['arquivo']
                if relatorio['selecionado'] is None:
                    relatorio['selecionado']=item['papel']
                    relatorio['recuperavel']=True
            else:
                item['estado']='ausente'
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
            item['estado']='invalido';item['erro']=type(exc).__name__
        relatorio['arquivos'].append(item)
    if relatorio['arquivos'][0]['estado']!='valido':
        relatorio['avisos'].append('Principal indisponível ou inválido; verificar recuperação em backup')
    if not relatorio['recuperavel']:
        relatorio['avisos'].append('Nenhum save válido recuperável')
    return relatorio
