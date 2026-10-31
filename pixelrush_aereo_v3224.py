# -*- coding: utf-8 -*-
"""Plano I v3.224: extensao dos mecanismos EXISTENTES de Jetpack e corredor laser.

Sem gerador paralelo, sem RNG privado, sem alterar a fisica, as caixas antigas,
contratos de save ou o temporizador de moedas. Atualizacao somente em tick fixo.
"""
from functools import lru_cache
import pygame


# O corredor antigo continua gerando 2/3 das barreiras sem modificacoes.
# Novos desenhos sao mais largos e so seguem o ultimo portal por passos curtos.
PADROES = ('degrau_acima', 'degrau_abaixo', 'onda', 'estavel')


def corredor_avancado(indice, ultimo_gap, altura, rng):
    """Devolve gap_y, gap_h, padrao para o MESMO array do corredor existente.

    Em dois portais sucessivos, a diferenca vertical nao excede 70 px. A
    aceleracao vertical do jogador no corredor e >=0.34 px/tick^2, limitada
    a 6.3 px/tick; 40+ ticks entre geracoes garantem a troca de faixa.
    """
    padrao = PADROES[((indice // 3) + rng.randrange(4)) % 4]
    movimento = {
        'degrau_acima': -64,
        'degrau_abaixo': 64,
        'onda': (-54 if (indice // 3) % 2 else 54),
        'estavel': 0,
    }[padrao]
    centro = altura - 335
    origem = int(ultimo_gap) if ultimo_gap is not None else centro
    novo = max(altura - 398, min(altura - 275, origem + movimento))
    altura_gap = rng.choice((152, 160, 168))
    return int(novo), int(altura_gap), padrao


# Mantem as mesmas moedas, o mesmo pool e a mesma cadencia de oito ticks.
# Introduz rotas de tres alturas sem novo objeto fisico e sem alterar o voo.
_TRILHA_ORIGINAL = (1, 1, 2, 2, 1, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2)
_TRILHA_ESCADA = (1, 1, 2, 2, 2, 1, 1, 0, 0, 0, 1, 1, 2, 2, 1, 1)
_TRILHA_ONDA = (1, 0, 0, 1, 1, 2, 2, 1, 1, 0, 0, 1, 2, 2, 1, 1)
_TRILHAS = (_TRILHA_ORIGINAL, _TRILHA_ESCADA, _TRILHA_ONDA)


def faixa_moeda_jetpack(indice):
    indice = max(0, int(indice))
    return _TRILHAS[(indice // 16) % len(_TRILHAS)][indice % 16]


@lru_cache(maxsize=2)
def _imagem_gate(aviso):
    """Quadros pre-renderizados uma vez. Um unico blit por gate."""
    sf = pygame.Surface((48, 42), pygame.SRCALPHA)
    base = (235, 169, 78) if aviso else (248, 67, 113)
    luz = (255, 242, 174) if aviso else (255, 231, 245)
    pygame.draw.rect(sf, (24, 30, 62, 234), (0, 0, 48, 42), border_radius=7)
    pygame.draw.rect(sf, base, (4, 5, 40, 32), 3, border_radius=5)
    pygame.draw.line(sf, base, (7, 21), (41, 21), 8)
    pygame.draw.line(sf, luz, (9, 19), (39, 19), 3)
    pygame.draw.circle(sf, luz, (9, 21), 3)
    pygame.draw.circle(sf, luz, (39, 21), 3)
    # Linhas de emissao, ranhuras e terminais luminosos pixelados.
    for xx in (6, 40):
        pygame.draw.rect(sf, (88, 219, 255), (xx, 8, 3, 6))
        pygame.draw.rect(sf, (88, 219, 255), (xx, 28, 3, 6))
    for xx in (16, 25, 34):
        pygame.draw.rect(sf, luz, (xx, 16, 3, 3))
        pygame.draw.rect(sf, (67, 106, 173), (xx, 25, 2, 3))
    return sf.convert_alpha()


@lru_cache(maxsize=1)
def _painel_aviso():
    painel = pygame.Surface((238, 27), pygame.SRCALPHA)
    painel.fill((14, 29, 53, 215))
    pygame.draw.rect(painel, (255, 190, 105), (0, 0, 238, 27), 2)
    rotulo = pygame.font.Font(None, 19).render('LASER AEREO  -  MUDE DE FAIXA', True, (255, 238, 178))
    painel.blit(rotulo, rotulo.get_rect(center=(119, 14)))
    return painel.convert_alpha()


class LaserJetpackAvancado:
    """Um gate por vez na fase de voo, isolado dos lasers terrestres.

    Protecoes: aparece so em voo estavel, nunca na subida/descida, nenhuma
    aparicao veloz, ao menos 35 ticks de reacao, apenas 1 faixa obstruida,
    sem perigo simultaneo, nenhum RNG extra ou sprite em grupos globais.
    """
    INTERVALO = 142
    ESPERA_INICIAL = 74
    REACAO_MIN_TICKS = 35

    def __init__(self, largura=450):
        self.largura = int(largura)
        self.reiniciar()

    def reiniciar(self):
        self.em_voo = False
        self.contador = 0
        self.espera = self.ESPERA_INICIAL
        self.x = -100.0
        self.y = 0
        self.aviso = 0
        self.ligado = False
        self.faixa = 1
        self.gerados = 0
        self.colisoes = 0

    @property
    def visivel(self):
        return self.x > -50 and self.ligado

    def atualizar(self, jogador, velocidade, permitido=True):
        if jogador.jetpack_fase != 'voando' or jogador.morrendo:
            # O gate nao persiste na aterrissagem ou entre powerups.
            self.em_voo = False
            self.ligado = False
            self.x = -100.0
            return
        if not self.em_voo:
            self.em_voo = True
            self.espera = self.ESPERA_INICIAL
            self.ligado = False
            self.x = -100.0
        # Auditoria v3.226.0: quando outro evento torna o laser proibido,
        # cancelar tambem o gate JA ativo (nao apenas bloquear novos spawns).
        if not permitido:
            self.ligado = False
            self.x = -100.0
            return
        self.contador += 1
        if self.ligado:
            self.x -= float(velocidade) + 2.0
            if self.aviso:
                self.aviso -= 1
            if self.x < -50:
                self.ligado = False
            return
        self.espera -= 1
        if self.espera > 0:
            return
        if not permitido or jogador.tempo_jetpack <= 118:
            return
        velocidade = max(0.0, float(velocidade))
        x_inicio = self.largura + 62
        tempo_reacao = (x_inicio - jogador.rect.right) / (velocidade + 2.0)
        if tempo_reacao < self.REACAO_MIN_TICKS:
            return
        # O heroi ja deve estar centralizado na faixa antes da aparicao.
        faixa = int(jogador.jetpack_nivel)
        if abs(jogador.rect.bottom - jogador.obter_bottom_jetpack(faixa)) > 12:
            return
        self.faixa = faixa
        self.y = jogador.obter_y_moeda_jetpack(faixa)
        self.x = float(x_inicio)
        self.aviso = min(31, max(1, int(tempo_reacao) - 12))
        self.ligado = True
        self.gerados += 1
        self.espera = self.INTERVALO

    def hitbox(self):
        return pygame.Rect(int(self.x) + 6, int(self.y) - 13, 36, 26)

    def colide(self, hitbox_jogador):
        return bool(self.ligado and self.aviso == 0 and
                    self.hitbox().colliderect(hitbox_jogador))

    def consumir(self):
        self.ligado = False
        self.x = -100.0
        self.colisoes += 1

    def desenhar(self, superficie, leve=False):
        if not self.ligado:
            return
        superficie.blit(_imagem_gate(self.aviso > 0), (int(self.x), int(self.y) - 21))
        if self.aviso > 0:
            superficie.blit(_painel_aviso(), ((self.largura - 238)//2, 222))
        if not leve and self.aviso > 0:
            # Flecha informativa: apenas duas linhas, sem calculos trigonometricos.
            x = int(self.x) + 24
            y = int(self.y) - 29
            pygame.draw.line(superficie, (255, 220, 123), (x - 7, y), (x + 7, y), 2)
            pygame.draw.line(superficie, (255, 220, 123), (x, y - 4), (x, y + 3), 2)
