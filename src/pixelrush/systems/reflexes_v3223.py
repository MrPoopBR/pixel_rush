# -*- coding: utf-8 -*-
"""Plano I v3.223: frases de reflexo no diretor existente, sem novo spawn.

Cada passo ocupa um encontro de perigo que ja seria gerado. Nenhum evento
DESCANSO/TRILHA/None vira perigo; espacamento e protecoes originais prevalecem.
Todas as distancias do diretor sao em METROS, nao em frames de renderizacao.
"""
from functools import lru_cache
import pygame
from pixelrush_moveis_v3222 import ObstaculoMovel, PERFIS, TIPOS, quadros

ACOES = frozenset(('SALTO', 'ESCOLHA', 'PASSAGEM'))
COMANDOS = ('REFLEXO_CURTO', 'REFLEXO_LONGO', 'REFLEXO_BAIXO')
CHOQUES = frozenset((('SALTO', 'PASSAGEM'), ('PASSAGEM', 'SALTO'),
                     ('ESCOLHA', 'PASSAGEM'), ('PASSAGEM', 'ESCOLHA')))
MAPA_GESTO = {'REFLEXO_CURTO': 'SALTO', 'REFLEXO_LONGO': 'SALTO',
              'REFLEXO_BAIXO': 'PASSAGEM'}
# Ordem da frase muda com bioma e setor; os tres gestos sao utilizados.
FRASES = (
    ('REFLEXO_CURTO', 'REFLEXO_BAIXO', 'REFLEXO_LONGO'),
    ('REFLEXO_LONGO', 'REFLEXO_CURTO', 'REFLEXO_BAIXO'),
    ('REFLEXO_BAIXO', 'REFLEXO_CURTO', 'REFLEXO_LONGO'),
    ('REFLEXO_CURTO', 'REFLEXO_LONGO', 'REFLEXO_BAIXO'),
)
BIOMAS = tuple(PERFIS)


class DiretorReflexos:
    """Decorador externo: pede ao mesmo diretor original um comando por encontro.

    Na primeira acao elegivel apos 1250m, inicia uma frase de tres perigos.
    A cada passo existe >=32m desde o anterior; se a frase demorar >330m,
    aborta. A pausa pos-frase de 540m evita repeticao em loop. Nenhuma
    chamada a random: compatibilidade deterministica com as fitas de replay.
    """
    INICIO = 1250
    INTERVALO_MIN_METROS = 32
    LIMITE_FRASE_METROS = 330
    PAUSA_METROS = 540

    def __init__(self, diretor):
        self.diretor = diretor
        self.reiniciar(contar_base=False)

    def reiniciar(self, contar_base=True):
        if contar_base:
            self.diretor.reiniciar()
        self.bioma = None
        self.ultimo_emitido = None
        self.protecoes = 0
        self.etapa = 0
        self.inicio_frase = 0
        self.ultimo_metro = -10**9
        self.liberado_em = self.INICIO
        self.total_passos = 0
        self.frases_completas = 0
        self.frases_canceladas = 0

    def _emitir(self, comando):
        self.ultimo_emitido = comando
        return comando

    def proxima(self, metros, cenario='cidade'):
        base = self.diretor.proxima(metros, cenario)
        if cenario != self.bioma:
            # Nao transportar partes de uma frase entre biomas.
            if self.etapa:
                self.frases_canceladas += 1
            self.bioma = cenario
            self.ultimo_emitido = None
            self.etapa = 0
            self.liberado_em = max(self.INICIO, int(metros) + 65)
        if cenario not in PERFIS or metros < self.INICIO:
            return self._emitir(base)
        if self.etapa and (metros - self.inicio_frase > self.LIMITE_FRASE_METROS):
            self.etapa = 0
            self.frases_canceladas += 1
            self.liberado_em = int(metros) + self.PAUSA_METROS // 2
        # Janelas vazias e pausas permanecem intocadas, inclusive durante frase.
        if base not in ACOES or metros < self.liberado_em:
            return self._emitir(base)
        if self.etapa and metros - self.ultimo_metro < self.INTERVALO_MIN_METROS:
            return self._emitir(base)
        if not self.etapa:
            self.inicio_frase = int(metros)
        indice_bioma = BIOMAS.index(cenario)
        frase = FRASES[(indice_bioma + self.inicio_frase // 1800) % len(FRASES)]
        escolhido = frase[self.etapa]
        # A camada interna de justiça desconhece a transformação de gestos
        # feita AQUI; portanto aplica a MESMA tabela de choques do auditor.
        anterior = MAPA_GESTO.get(self.ultimo_emitido, self.ultimo_emitido)
        atual = MAPA_GESTO[escolhido]
        if (anterior, atual) in CHOQUES:
            self.protecoes += 1
            return self._emitir('DESCANSO')
        self.ultimo_metro = int(metros)
        self.etapa += 1
        self.total_passos += 1
        if self.etapa == 3:
            self.etapa = 0
            self.frases_completas += 1
            self.liberado_em = int(metros) + self.PAUSA_METROS
        return self._emitir(escolhido)


# Sprites curtos/longos reutilizam somente atlas existentes: variacao sem
# arquivos adicionais e sem deformar a pixel art aprovada na v3.222.
CURTOS = {}
LONGOS = {}
for bioma, perfis in PERFIS.items():
    aptos = [nome for nome, rota, _ in perfis if rota == 'chao']
    if bioma == 'cidade':
        CURTOS[bioma], LONGOS[bioma] = 'moto_rua', 'carro_urbano'
    elif bioma == 'neve':
        CURTOS[bioma], LONGOS[bioma] = 'treno_neve', 'bola_neve_gigante'
    elif bioma == 'deserto':
        CURTOS[bioma], LONGOS[bioma] = 'barril_deserto', 'rocha_arenito'
    elif bioma == 'floresta':
        CURTOS[bioma], LONGOS[bioma] = 'raiz_viajante', 'tronco_rolando'
    elif bioma == 'vulcao':
        CURTOS[bioma], LONGOS[bioma] = 'bloco_basalto', 'rocha_magma'
    elif bioma == 'cidade_futurista':
        CURTOS[bioma], LONGOS[bioma] = 'moto_ionica', 'carro_magnetico'
    else:
        CURTOS[bioma], LONGOS[bioma] = aptos[0], aptos[0]


@lru_cache(maxsize=7)
def _quadros_longos(tipo):
    """Dois veiculos/objetos conectados, rasterizados UMA vez por bioma."""
    frames = []
    for base in quadros(tipo):
        superficie = pygame.Surface((162, 62), pygame.SRCALPHA)
        superficie.blit(base, (0, 0))
        superficie.blit(base, (80, 0))
        frames.append(superficie.convert_alpha())
    return tuple(frames)


class ObstaculoReflexo(ObstaculoMovel):
    """Apenas encontros NOVOS recebem caixas proprias de curta/longa distancia.

    Deriva do obstaculo movel oficial: nao troca grupos, update ou colisao.
    """
    def __init__(self, x_pos, bioma, longo=False):
        tipo = LONGOS[bioma] if longo else CURTOS[bioma]
        super().__init__(x_pos, tipo)
        self._reflexo_comando = 'REFLEXO_LONGO' if longo else 'REFLEXO_CURTO'
        # Energia/deslocamento extra iguais nos dois comprimentos: gestos
        # distinguem-se pela largura, nao por picos inesperados de velocidade.
        self.bonus = min(self.bonus, 0.8)
        self.rota = 'chao'
        self._frames = _quadros_longos(tipo) if longo else quadros(tipo)
        self.image = self._frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = int(x_pos)
        self.rect.bottom = 730
        self._x = float(self.rect.x)
        self._base_y = self.rect.y
        # Evita caixa retangular invisivel no meio da dupla.
        if longo:
            self._hitboxes_precisas_v342 = (pygame.Rect(9, 15, 61, 37),
                                             pygame.Rect(90, 15, 61, 37))
        else:
            self._hitboxes_precisas_v342 = (pygame.Rect(13, 15, 55, 37),)


def criar_reflexo(comando, bioma, x_base, ObstaculoVoador, altura_virtual):
    """Um so perigo por encontro; a rota baixa usa o inimigo suspenso antigo."""
    if comando == 'REFLEXO_BAIXO':
        obs = ObstaculoVoador(x_base, bioma)
        obs.rect.y = altura_virtual - 157
        obs._reflexo_comando = comando
        return obs
    if comando not in COMANDOS or bioma not in CURTOS:
        raise ValueError('Comando/bioma de reflexo nao reconhecido')
    # Mesmo ponto de entrada do gerador; reflexos nao criam outro temporizador.
    return ObstaculoReflexo(x_base, bioma, longo=comando == 'REFLEXO_LONGO')


def janela_teorica(comando, largura, velocidade, extra=0.8):
    """QA auxiliar para estimar a travessia da caixa, nao controla gameplay."""
    return max(0.0, float(largura) / max(0.1, float(velocidade) + float(extra)))
