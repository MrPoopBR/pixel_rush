"""Pixel Rush v3.186.0 — intermediarios visuais dos 15 perigos ativos.

NAO altera _fase, ticks, atualizacao, trajetoria, rect, hitboxes ou colisao.
Seis quadros por perigo (3 fases originais + 3 intermediarios internos).
O geiser conserva a fase de dano exatamente como herdada do motor.
Apenas RGB dentro do alfa ja existente recebe transicoes; desenhos, alfa,
contorno, sprites e dimensoes do jogo anterior sao preservados.
"""
import pygame
import numpy as np
from pixelrush_ameacas_v3127 import risco_colisao_ativo
from pixelrush_ameacas_v3174 import (
    AMEACAS, POR_BIOMA, escorpiao_frame,
    imagem_ameaca as _imagem_base, AmeacaBioma as _ClasseAnterior,
)

ATIVOS = frozenset(k for k, v in AMEACAS.items()
                   if v[4] not in ('parado', 'parado_alto'))
AEREOS = frozenset(('C2', 'N2', 'V2', 'F2', 'CF2', 'IC2'))
RODANTES = frozenset(('C1', 'N1', 'D1', 'D2', 'V1', 'F1', 'CF1', 'IC1'))
_CACHE_INTERMEDIARIOS = {}


def quadro_intermediario(codigo, fase):
    """Retorna imagem imutavel em cache, sem qualquer transformacao por tick."""
    fase = int(fase) % 3
    if codigo not in ATIVOS:
        return _imagem_base(codigo, fase)
    chave = (codigo, fase)
    pronto = _CACHE_INTERMEDIARIOS.get(chave)
    if pronto is not None:
        return pronto
    origem = _imagem_base(codigo, fase)
    proximo = _imagem_base(codigo, (fase + 1) % 3)
    atual = pygame.surfarray.array3d(origem)
    alfa = pygame.surfarray.array_alpha(origem)
    futuro = pygame.surfarray.array3d(proximo)
    alfa_futuro = pygame.surfarray.array_alpha(proximo)
    largura, altura = origem.get_size()
    xs = np.arange(largura, dtype=np.int32)[:, None]
    ys = np.arange(altura, dtype=np.int32)[None, :]
    brilho = (atual[:, :, 0].astype(np.int32) * 3
              + atual[:, :, 1].astype(np.int32) * 5
              + atual[:, :, 2].astype(np.int32) * 2) // 10
    # A fase original fornece EXATAMENTE a mesma mascara alfa e o mesmo contorno.
    # Nunca misturar vapor com fresta: a fase de alerta do geiser e intocavel.
    miolo = (alfa == 255) & (alfa_futuro >= 220) & (brilho >= 72) & (brilho < 235)
    if codigo in AEREOS:
        # Ilusao de transicao entre batidas de asa, sem mover o contorno.
        zona = (ys < altura * 0.71) & ((xs < largura * .35) | (xs > largura * .67))
        peso = 48  # 48/128 para amostrar a cor do movimento seguinte.
    elif codigo in RODANTES:
        # Movimento secundario de patas, nadadeiras e superficie da carapaca.
        zona = ((ys > altura * (.30 if codigo in ('F1', 'IC1') else .51))
                & (ys < altura * .89))
        peso = 36
    else:
        # Geiser: somente brilho INTERNO do vapor/brasas, sem mudar avisos.
        zona = (xs > largura * .24) & (xs < largura * .78)
        peso = 0
    permitido = miolo & zona
    saida = origem.copy()
    matriz = pygame.surfarray.pixels3d(saida)
    if peso:
        novo = ((atual.astype(np.uint16) * (128 - peso)
                 + futuro.astype(np.uint16) * peso) // 128).astype(np.uint8)
        matriz[permitido] = novo[permitido]
    # Pontos ritmicos de brilho, exclusivamente em pixels SOLIDOS do material.
    # Pequena modulacao reforca movimento sem efeitos, sombras ou partículas novas.
    foco = (alfa == 255) & (brilho >= 68) & (brilho < 247)
    padrao = ((xs * 3 + ys * 5 + fase * 7) % 17) < 2
    if codigo == 'V4':
        # A coluna so recebe detalhe se ela ja existia na fase atual.
        foco &= (ys > altura * .15) & (xs > largura * .30) & (xs < largura * .70)
        ganho = np.array([6, 8, 10], dtype=np.int16)
    elif codigo in ('CF1', 'CF2', 'IC1', 'IC2'):
        foco &= zona
        ganho = np.array([3, 10, 11], dtype=np.int16)
    elif codigo in ('V1', 'V2'):
        foco &= zona
        ganho = np.array([11, 5, 1], dtype=np.int16)
    else:
        foco &= zona
        ganho = np.array([7, 7, 4], dtype=np.int16)
    seletor = foco & padrao
    if np.any(seletor):
        matriz[seletor] = np.minimum(255, matriz[seletor].astype(np.int16) + ganho).astype(np.uint8)
    del matriz
    # Contrato de seguranca visual: NENHUMA mudanca na mascara/hitbox.
    assert pygame.surfarray.array_alpha(saida).tobytes() == alfa.tobytes()
    assert saida.get_size() == origem.get_size()
    _CACHE_INTERMEDIARIOS[chave] = saida
    return saida


# Compatibilidade para ferramentas e outros imports antigos.
imagem_ameaca = _imagem_base


class AmeacaBioma(_ClasseAnterior):
    """A classe anterior continua integralmente responsavel pela simulacao."""
    def update(self, velocidade_jogo):
        super().update(velocidade_jogo)
        if self.codigo not in ATIVOS:
            return
        # Nao muda o periodo das fases originais; apenas substitui a
        # IMAGEM desenhada na segunda metade de uma fase preexistente.
        # A ativacao do geiser permanece exclusivamente no super().update.
        if self.codigo == 'V4':
            intermediario = (self.ticks % 10) >= 5
        else:
            intermediario = (self.ticks % 9) >= 5
        if intermediario:
            self.image = quadro_intermediario(self.codigo, self._fase)
        else:
            self.image = _imagem_base(self.codigo, self._fase)
