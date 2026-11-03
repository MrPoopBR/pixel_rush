# -*- coding: utf-8 -*-
"""QA v3.277.47 — antecipa SOMENTE leitura de atlas em menu, sem RNG/SDL.

A corrida sorteia o proximo bioma apenas no instante da transicao. Por isso
nao e correto escolher um bioma antecipadamente nem reservar tres mundos
na RAM. Esta etapa aquece as paginas dos atlas no SO, sem criar pygame.Surface,
e deixa a instancia de cena ser criada pelo loader PROD no momento original.
"""
import hashlib
import os
from pathlib import Path

MAX_ARQUIVO_BYTES=40*1024*1024
MAX_TOTAL_BYTES=125*1024*1024
BLOCO_BYTES=64*1024
ALVOS=('neve_lite','deserto_lite','neve','deserto')


def preaquecer_arquivos_fora_do_jogo(estado='CARREGANDO', alvos=ALVOS,
                                   max_total_bytes=MAX_TOTAL_BYTES,
                                   diretorio=None, hashes=None):
    """Leitura streaming de atlas existentes e SHA exato. Nada fica em cache Python.

    Nao executa pickle, nao constroi SDL e nao depende de qual sera o bioma
    aleatorio. Rejeita chamada quando JOGANDO. A leitura nao garante que o
    sistema operacional conserve as paginas de arquivo no seu page cache.
    """
    from pixelrush_atlas_prod_v32776 import _ATLAS, _HASHES
    resultado={'schema':'pixelrush.qa.atlas_io.v327747',
               'preparado':False,'arquivos':[],'bytes_lidos':0,
               'max_buffer_python_bytes':BLOCO_BYTES,
               'sorteio_usado':False,'superficies_criadas':0,
               'memoria_persistente_qa':0,'estado':str(estado)}
    if estado not in ('INICIO','CARREGANDO','PREPARACAO'):
        resultado['motivo']='estado_proibido'
        return resultado
    root=Path(diretorio) if diretorio is not None else _ATLAS
    hashes=dict(hashes) if hashes is not None else _HASHES
    seen=set()
    for nome in alvos:
        if nome in seen or nome not in hashes or nome not in ALVOS:
            continue
        seen.add(nome)
        arquivo=root/(nome+'.atlas')
        try:
            tam=arquivo.stat().st_size
            if tam<=0 or tam>MAX_ARQUIVO_BYTES:
                resultado['arquivos'].append({'nome':nome,'status':'fora_orcamento'})
                continue
            if resultado['bytes_lidos']+tam>max_total_bytes:
                resultado['arquivos'].append({'nome':nome,'status':'orcamento_total'})
                continue
            digest=hashlib.sha256()
            with arquivo.open('rb') as stream:
                while True:
                    dados=stream.read(BLOCO_BYTES)
                    if not dados:
                        break
                    digest.update(dados)
            resultado['bytes_lidos']+=tam
            valido=digest.hexdigest()==hashes[nome]
            resultado['arquivos'].append({'nome':nome,'status':'sha_ok' if valido else 'sha_invalido',
                                         'bytes':tam})
        except (OSError,ValueError):
            resultado['arquivos'].append({'nome':nome,'status':'indisponivel'})
    # Fechamento #23: incluir no page cache os tiles de acabamento
    # aprovados e assinados (3 biomas), sem descompactar pickle, carregar
    # SDL ou adiantar o sorteio do próximo cenário. Mesmo orçamento total.
    resultado['tiles_prod']=[]
    if diretorio is None and os.environ.get('PIXELRUSH_QA_TILES_IO_PREWARM','1')=='1':
        try:
            from pixelrush_tiles_prod_v32777 import _DIR as tiles_dir, _HASHES as tiles_sha
            for nome,esperado in tiles_sha.items():
                caminho=tiles_dir/(nome+'.tiles')
                try:
                    tamanho=caminho.stat().st_size
                    if (tamanho<=0 or tamanho>MAX_ARQUIVO_BYTES or
                            resultado['bytes_lidos']+tamanho>max_total_bytes):
                        resultado['tiles_prod'].append(
                            {'nome':nome,'status':'fora_orcamento'})
                        continue
                    sha=hashlib.sha256()
                    with caminho.open('rb') as stream:
                        for bloco in iter(lambda:stream.read(BLOCO_BYTES),b''):
                            sha.update(bloco)
                    resultado['bytes_lidos']+=tamanho
                    resultado['tiles_prod'].append(
                        {'nome':nome,'status':('sha_ok' if sha.hexdigest()==esperado
                                               else 'sha_invalido'),'bytes':tamanho})
                except (OSError,ValueError):
                    resultado['tiles_prod'].append(
                        {'nome':nome,'status':'indisponivel'})
        except (ImportError,AttributeError,RuntimeError):
            resultado['tiles_prod'].append(
                {'nome':'todos','status':'fallback_sem_tiles_prod'})
    resultado['preparado']=any(x['status']=='sha_ok' for x in (
        resultado['arquivos']+resultado['tiles_prod']))
    resultado['motivo']='io_verificado' if resultado['preparado'] else 'nenhum_atlas_verificado'
    return resultado


_ULTIMO={'executado':False,'motivo':'instalacao_nao_solicitada'}


def instalar_no_boot_qa():
    """Executa no instalador QA, antes de entrar no loop de jogo; sem APK."""
    global _ULTIMO
    if os.environ.get('PIXELRUSH_QA_ATLAS_IO_PREWARM','1')!='1':
        _ULTIMO={'executado':False,'motivo':'desativado_por_env'}
        return dict(_ULTIMO)
    try:
        # A produção já dispara hash+page-cache dos mesmos quatro .atlas
        # em pixelrush_preparacao_prod_v32778.instalar(). Não executar
        # a MESMA leitura duplicada no QA antes do menu. Aquecer apenas
        # tiles PROD adicionais, ainda sem SDL, saves ou sorteio.
        deduplicar=os.environ.get('PIXELRUSH_QA_ATLAS_IO_DEDUP','1')=='1'
        r=preaquecer_arquivos_fora_do_jogo(
            alvos=() if deduplicar else ALVOS)
        r['atlas_prod_preparados_pelo_carregador_original']=deduplicar
        _ULTIMO={'executado':True,'resultado':r}
    except (OSError,ImportError,RuntimeError,MemoryError) as exc:
        _ULTIMO={'executado':True,'motivo':'fallback_'+type(exc).__name__}
    return dict(_ULTIMO)


def diagnostico():
    return dict(_ULTIMO)
