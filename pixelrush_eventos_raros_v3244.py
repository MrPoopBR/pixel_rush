# -*- coding: utf-8 -*-
"""Plano K v3.244 — somente três eventos adicionais ao diretor v3.243.

A classe v3.243 segue responsável, intacta, pelos quatro biomas originais,
pelos temporizadores, cancelamentos, impacto e proteção. Para os três biomas
novos, a inicialização obedece às mesmas regras de raridade e concorrência.
Um único sprite Pygame pré-renderizado por bioma; sem RNG global, passes ou
superfícies criadas por quadro. Nenhuma hitbox antiga é alterada.
"""
import pygame
from pixelrush_eventos_raros_v3243 import DiretorEventosRaros as DiretorBase, EVENTOS as EVENTOS_ORIGINAIS

NOVOS_EVENTOS = {
    'vulcao': ('ERUPCAO - SALTE!', (255, 135, 72), 'rochas_flamejantes'),
    'cidade_futurista': ('PANE: DRONES - AGACHE!', (95, 241, 252), 'drones_em_pane'),
    'ilhas_celestes': ('CRISTAIS - AGACHE!', (177, 166, 255), 'tempestade_cristalina'),
}
EVENTOS = {**EVENTOS_ORIGINAIS, **NOVOS_EVENTOS}


class DiretorEventosRaros(DiretorBase):
    """Extensão conservadora: eventos antigos são delegados à base sem mudanças."""

    def atualizar(self, metros, bioma, *, permitido, perigo_proximo=False):
        # A base já controla toda a vida útil, os cancelamentos e as tentativas
        # dos biomas originais. O ramo novo só autoriza o início dos novos biomas.
        if self.ativo or bioma not in NOVOS_EVENTOS:
            return super().atualizar(metros, bioma, permitido=permitido,
                                     perigo_proximo=perigo_proximo)
        metros = max(0, int(metros))
        if (not permitido or perigo_proximo or self.aparicoes >= self.MAX_POR_PARTIDA
                or bioma in self.biomas_usados or metros < self.tentativa):
            return
        if self._rng.random() >= 0.18:
            self.tentativa = metros + 300 + self._rng.randrange(250)
            return
        self.bioma = bioma
        self.fase = 'aviso'
        self.ticks = 0
        self.aparicoes += 1
        self.biomas_usados.add(bioma)
        self.tentativa = metros + 950 + self._rng.randrange(300)
        self.impacto_pendente = False
        self.impactou = False

    def perigo_rect(self):
        if self.bioma not in NOVOS_EVENTOS:
            return super().perigo_rect()
        if self.fase != 'perigo':
            return None
        x = round(self.x)
        if self.bioma == 'vulcao':
            return pygame.Rect(x + 13, 696, 52, 25)  # rochas rasteiras: pular
        if self.bioma == 'cidade_futurista':
            return pygame.Rect(x + 14, 666, 51, 31)  # drone elevado: agachar
        return pygame.Rect(x + 13, 667, 54, 31)  # cristais altos: agachar

    def _sprite(self, bioma):
        if bioma not in NOVOS_EVENTOS:
            return super()._sprite(bioma)
        if bioma in self._sprites:
            return self._sprites[bioma]
        s = pygame.Surface((80, 76), pygame.SRCALPHA)
        if bioma == 'vulcao':
            # Chão fissurado, erupção e duas rochas com brilho interno.
            pygame.draw.ellipse(s, (27, 15, 22, 165), (4, 67, 72, 8))
            pygame.draw.polygon(s, (70, 40, 46), [(9, 70), (20, 55), (46, 49), (71, 68)])
            pygame.draw.polygon(s, (248, 101, 38), [(13, 67), (26, 58), (44, 55), (65, 68), (45, 65)])
            for x,y,r in ((28, 52, 17),(53, 53, 13)):
                pygame.draw.circle(s, (20, 19, 30), (x,y), r+3)
                pygame.draw.circle(s, (89, 54, 53), (x,y), r)
                pygame.draw.polygon(s, (245, 116, 41), [(x-8,y+5),(x-5,y-8),(x+3,y-11),(x+11,y+2)])
                pygame.draw.line(s, (255, 221, 99), (x-5,y+3), (x+3,y-7), 3)
            for x,y in ((22,22),(38,14),(57,28)):
                pygame.draw.polygon(s, (254, 180, 75), [(x,y+9),(x-5,y+2),(x+1,y-7),(x+5,y+3)])
                pygame.draw.rect(s, (255, 233, 147), (x-1,y,2,4))
        elif bioma == 'cidade_futurista':
            # Silhueta de drone suspenso e pane: eletricidade e falhas de tela.
            pygame.draw.line(s, (32, 91, 110), (7, 47), (72, 47), 2)
            for x in (15, 64):
                pygame.draw.circle(s, (11, 28, 47), (x, 31), 13)
                pygame.draw.circle(s, (60, 217, 231), (x, 31), 10, 3)
                pygame.draw.line(s, (152, 249, 251), (x-7,31), (x+7,31), 2)
            pygame.draw.polygon(s, (16, 26, 49), [(21,26),(59,26),(68,37),(57,48),(23,48),(12,37)])
            pygame.draw.polygon(s, (77, 92, 127), [(23,28),(57,28),(62,36),(54,43),(26,43),(18,36)])
            pygame.draw.rect(s, (255, 103, 157), (30,33,20,6))
            for x,y in ((9,11),(39,6),(67,16)):
                pygame.draw.lines(s, (104, 249, 255), False,
                                  [(x,y),(x+6,y+5),(x+1,y+11),(x+9,y+18)], 2)
            pygame.draw.rect(s, (250, 98, 145), (22, 56,33,2))
            pygame.draw.rect(s, (86, 230, 250), (28, 61,25,2))
        else:
            # Tempestade celestial com três cristais suspensos e eletricidade.
            for x,y in ((10,6),(41,3),(68,12)):
                pygame.draw.lines(s, (183, 211, 255), False,
                                  [(x,y),(x+5,y+8),(x-2,y+19),(x+6,y+27)],2)
            for x,y,w,h in ((20,27,21,32),(46,24,22,34),(7,38,15,21)):
                pygame.draw.polygon(s, (31, 34, 70),
                                    [(x+w//2,y-3),(x+w+2,y+h//3),(x+w//2,y+h+3),(x-2,y+h//3)])
                pygame.draw.polygon(s, (120, 135, 230),
                                    [(x+w//2,y),(x+w,y+h//3),(x+w//2,y+h),(x,y+h//3)])
                pygame.draw.polygon(s, (218, 228, 255),
                                    [(x+w//2,y+3),(x+w//2,y+h-5),(x+3,y+h//3)])
                pygame.draw.line(s, (251, 253, 255), (x+w//2,y+2), (x+w//2,y+h-5),2)
            for x,y in ((13,25),(65,39),(39,68)):
                pygame.draw.line(s,(160, 247, 252),(x-3,y),(x+3,y),2)
                pygame.draw.line(s,(160, 247, 252),(x,y-3),(x,y+3),2)
        self._sprites[bioma] = s.convert_alpha()
        return self._sprites[bioma]

    def _aviso(self, bioma, leve):
        if bioma not in NOVOS_EVENTOS:
            return super()._aviso(bioma, leve)
        k = (bioma, bool(leve))
        if k in self._avisos:
            return self._avisos[k]
        mensagem, cor, _ = NOVOS_EVENTOS[bioma]
        w = 186 if leve else 246
        surf = pygame.Surface((w, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, (15, 22, 35, 224), (0,0,w,32), border_radius=5)
        pygame.draw.rect(surf, cor, (1,1,w-2,30), 2, border_radius=5)
        fonte = pygame.font.Font(None, 16 if leve else 19)
        frase = fonte.render(mensagem, True, (255, 247, 221))
        # Também no modo leve o texto inteiro permanece dentro do aviso.
        if frase.get_width() > w - 10:
            fonte = pygame.font.Font(None, 14)
            frase = fonte.render(mensagem, True, (255, 247, 221))
        surf.blit(frase, (5,6))
        self._avisos[k] = surf
        return surf

    def desenhar(self, destino, leve=False):
        if self.bioma not in NOVOS_EVENTOS:
            return super().desenhar(destino, leve)
        if not self.ativo:
            return
        if self.fase == 'aviso':
            destino.blit(self._aviso(self.bioma, leve), (119 if leve else 94, 320))
        elif self.fase == 'perigo':
            destino.blit(self._sprite(self.bioma), (round(self.x), 654))
