# -*- coding: utf-8 -*-
"""QA 3.277.46: preparacao de cena modular EXCLUSIVAMENTE fora da corrida.

O jogo PROD ja usa atlas verificados SHA-256 (v32776) e conserva no maximo
uma cena modular. Este modulo NAO reconstrói atlas, NAO duplica texturas,
NAO inicia threads SDL e NAO escolhe o proximo bioma aleatorio.

A chamada tem de ocorrer em menu/carregamento, quando o proximo bioma ja e
conhecido. A corrida aleatoria atual nao possui essa janela: o pre-aquecimento
automatico permanece DESATIVADO ate haver um ponto seguro no fluxo de jogo.
"""
import gc
from pathlib import Path

from pixelrush_qa_audit_offline_v327744 import rss_mib

ESTADOS_SEGUROS=frozenset(('INICIO','CARREGANDO','PREPARACAO'))
ALVOS=frozenset(('neve','deserto'))


def preparar_fora_da_corrida(world, proximo_bioma, estado,
                            teto_rss_mib=384.0, max_aumento_mib=32.0):
    """Conserva apenas uma cena preexistente do loader PROD, sem renderizar.

    Rejeita gameplay, mundo modular ativo, slot ocupado, atlas nao verificado,
    falta de memoria e aumenta de RSS acima do limite. Nunca remove o bioma
    que esta sendo usado. Apenas insercao em world.modular, que e o cache
    nativo de uma cena utilizado por world._get_modular().
    """
    from pixelrush_world_prod_v32777 import LivingWorld
    from pixelrush_atlas_prod_v32776 import _ATLAS, _HASHES, carregar_cena
    from pixelrush_hash_compat_v327725 import sha256_stream

    def resultado(estado_saida, **extra):
        return {'estado':estado_saida,'bioma':proximo_bioma,
                'ativo_na_corrida':False,'atlas_reutilizado':False,**extra}

    if not isinstance(world,LivingWorld):
        return resultado('mundo_nao_produtivo')
    if estado not in ESTADOS_SEGUROS:
        return resultado('estado_proibido')
    if world.biome!='cidade' or proximo_bioma not in ALVOS:
        return resultado('fora_do_escopo')
    if proximo_bioma in world.modular:
        return resultado('ja_preparado',atlas_reutilizado=True)
    if world.modular:
        # Nao manter dois modulares simultaneos nem destruir um cache vivo.
        return resultado('slot_ocupado')
    antes=rss_mib()
    if antes is None or antes+max_aumento_mib>teto_rss_mib:
        return resultado('orcamento_insuficiente',rss_antes_mib=antes)
    if max_aumento_mib<=0:
        return resultado('orcamento_insuficiente',rss_antes_mib=antes)
    nome=proximo_bioma+('_lite' if world.lightweight else '')
    esperado=_HASHES.get(nome)
    path=_ATLAS/(nome+'.atlas')
    if not esperado or not path.is_file():
        return resultado('atlas_ausente')
    try:
        with path.open('rb') as arquivo:
            if sha256_stream(arquivo)!=esperado:
                return resultado('atlas_invalido')
    except (OSError,ValueError):
        return resultado('atlas_ilegivel')

    # Nao usa construtor procedural paralelo nem altera world.biome/travel.
    # O atlas e validado outra vez pelo carregador original (fallback seguro).
    cena=carregar_cena(proximo_bioma,lightweight=world.lightweight)
    depois=rss_mib()
    if depois is None or depois>teto_rss_mib or depois-antes>max_aumento_mib:
        del cena
        gc.collect()  # Apenas fora da corrida, nunca no frame de jogo.
        return resultado('preparo_descartado_por_rss',rss_antes_mib=antes,
                         rss_depois_mib=depois)
    # Mesmo slot utilizado pelo renderer PROD; sem cache adicional persistente.
    world.modular[proximo_bioma]=cena
    return resultado('preparado',atlas_reutilizado=True,rss_antes_mib=antes,
                     rss_depois_mib=depois,
                     delta_rss_mib=round(max(0.,depois-antes),3),
                     cenas_retidas=len(world.modular))


def diagnostico():
    """Informa que esta API nao se auto-instala nem altera o sorteio."""
    return {'preparacao_automatica_na_corrida':False,
            'modulos_ativos_novos':False,
            'janela_segura':sorted(ESTADOS_SEGUROS),
            'max_cenas_adicionais':1,
            'usa_atlas_prod_existente':True}
