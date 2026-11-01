# -*- coding: utf-8 -*-
"""Pixel Rush 3.222 — obstáculos móveis por bioma.

Usa EXCLUSIVAMENTE o grupo/spawn/colisão antigos. Quadros feitos fora do jogo,
carregados sob demanda; sem pygame.transform.rotate ou desenhos por tick.
O ritmo é o passo fixo já existente (update chamado uma vez por tick).
"""
from functools import lru_cache
from pathlib import Path
import pygame

LARGURA, ALTURA = 82, 62
FRAMES = 6
RAIZ = Path(__file__).resolve().parent / 'assets' / 'moveis_v3222'
# Nome interno, rota (chao ou alto) e velocidade relativa extra, em pixels/tick.
# Salto horizontal longo significa a peça maior, NÃO modifica física do jogador.
PERFIS = {
    'cidade': (
        ('carro_urbano', 'chao', .8), ('moto_rua', 'chao', 1.6),
        ('van_urbana', 'chao', .7)),
    'neve': (
        ('bola_neve_gigante', 'chao', 1.2), ('bloco_gelo', 'chao', .7),
        ('treno_neve', 'chao', 1.5)),
    'deserto': (
        ('rocha_arenito', 'chao', 1.0), ('barril_deserto', 'chao', 1.5),
        ('vagonete_mina', 'chao', .9)),
    'floresta': (
        ('tronco_rolando', 'chao', 1.2), ('galho_alto', 'alto', 1.1),
        ('raiz_viajante', 'chao', .7)),
    'vulcao': (
        ('rocha_magma', 'chao', 1.1), ('fragmento_lava', 'alto', 1.4),
        ('bloco_basalto', 'chao', .8)),
    'cidade_futurista': (
        ('carro_magnetico', 'alto', 1.2), ('moto_ionica', 'alto', 1.7),
        ('drone_transporte', 'alto', 1.0)),
    'ilhas_celestes': (
        ('cristal_levitante', 'alto', .9), ('fragmento_mineral', 'chao', 1.1),
        ('tronco_suspenso', 'alto', 1.2)),
}
TIPOS = {nome: (bioma, rota, bonus) for bioma, perfis in PERFIS.items()
         for nome, rota, bonus in perfis}
# Primeiras sequências seguras: 1 perigo móvel no lugar de 1 perigo antigo;
# não combina chão + teto nesta etapa. A sequência do diretor permanece a dona do spawn.
# v3.236.0 — alinhamento exclusivamente visual de quatro atlas terrestres.
# Margem inferior transparente constante nos seis quadros, medida em Pygame.
# Não altera rect, hitboxes, spawn, velocidade, timers ou lógica de colisão.
DESLOCAMENTO_VISUAL_SOLO = {
    'treno_neve': 10, 'barril_deserto': 12,
    'tronco_rolando': 9, 'raiz_viajante': 11,
}

ROTAS = {'SALTO': 'chao', 'PASSAGEM': 'alto', 'ESCOLHA': None}
DISTANCIA_MINIMA = 850
PROBABILIDADE = .27


def escolher(bioma, sequencia, metros, aleatorio):
    """RNG global fornecido pelo chamador: compatível com replay e gravação."""
    if metros < DISTANCIA_MINIMA or sequencia not in ROTAS or bioma not in PERFIS:
        return None
    exigida = ROTAS[sequencia]
    opcoes = [nome for nome, rota, _ in PERFIS[bioma] if exigida is None or rota == exigida]
    if not opcoes:
        return None  # PASSAGEM clássica continua intacta nos biomas sem perigos altos.
    if aleatorio.random() >= PROBABILIDADE:
        return None
    return aleatorio.choice(opcoes)


@lru_cache(maxsize=9)
def quadros(tipo):
    """LRU: nove atlases em memória (menos de 1,4 MiB de RGBA)."""
    if tipo not in TIPOS:
        raise ValueError('Obstáculo móvel desconhecido: '+str(tipo))
    atlas = pygame.image.load(str(RAIZ / (tipo + '.png'))).convert_alpha()
    if atlas.get_size() != (LARGURA * FRAMES, ALTURA):
        raise ValueError('Atlas com dimensões incorretas: '+tipo)
    frames = tuple(atlas.subsurface((i * LARGURA, 0, LARGURA, ALTURA)).copy()
                   for i in range(FRAMES))
    # Visual pré-preparado no carregamento do atlas, jamais no loop da corrida.
    deslocamento = DESLOCAMENTO_VISUAL_SOLO.get(tipo, 0)
    if deslocamento:
        for frame in frames:
            frame.scroll(dy=deslocamento)
            frame.fill((0, 0, 0, 0), (0, 0, LARGURA, deslocamento))
    return frames


class ObstaculoMovel(pygame.sprite.Sprite):
    """Novo perigo com caixa própria, integrado ao grupo de obstáculos clássico."""
    def __init__(self, x_pos, tipo):
        super().__init__()
        bioma, rota, bonus = TIPOS[tipo]
        self.cenario = bioma
        self.tipo_movel = tipo
        self.rota = rota
        self.bonus = bonus
        self.qtd_cactos = 0
        self._frames = quadros(tipo)
        self.image = self._frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = int(x_pos)
        self.rect.bottom = (692 if rota == 'alto' else 730)
        self._x = float(self.rect.x)
        self._base_y = self.rect.y
        self._tick = 0
        # Apenas novos obstáculos têm hitbox própria; nenhum tipo antigo é editado.
        if tipo in ('moto_rua','moto_ionica'):
            self._hitboxes_precisas_v342 = (pygame.Rect(12, 22, 56, 27),)
        elif tipo in ('bola_neve_gigante','rocha_arenito','rocha_magma','fragmento_lava',
                      'cristal_levitante','fragmento_mineral','bloco_basalto'):
            self._hitboxes_precisas_v342 = (pygame.Rect(18, 10, 47, 45),)
        elif tipo in ('galho_alto','tronco_suspenso'):
            self._hitboxes_precisas_v342 = (pygame.Rect(8, 20, 66, 28),)
        else:
            self._hitboxes_precisas_v342 = (pygame.Rect(9, 15, 65, 37),)

    def update(self, velocidade_jogo):
        self._tick += 1
        # Velocidade relativa de aproximação: não altera vel_jogo do restante.
        self._x -= max(0.0, float(velocidade_jogo)) + self.bonus
        self.rect.x = int(self._x)  # conserva subpixels entre ticks.
        if self.rota == 'alto':
            self.rect.y = self._base_y + (0, -1, -2, -1, 0, 1)[(self._tick // 4) % 6]
        self.image = self._frames[(self._tick // 4) % FRAMES]
        if self.rect.right < -30:
            self.kill()

    def tempo_reacao_ticks(self, jogador_direita, velocidade_jogo):
        return max(0.0, (self.rect.left - jogador_direita) /
                   max(.1, max(0.0, float(velocidade_jogo)) + self.bonus))
