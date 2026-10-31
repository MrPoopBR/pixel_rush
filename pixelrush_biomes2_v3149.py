"""v3.149 — passe final premium da Floresta Densa.

Foco:
- profundidade fina adicional;
- redução de recortes retos percebidos durante a corrida;
- mais variedade discreta na vegetação média e próxima;
- sem alterar jogabilidade nem outros biomas.
"""
import math
import random
import pygame
from pixelrush_biomes2_v3148 import ModularBiomeScene as Previous
from pixelrush_biomes2_v3126 import LW


class ModularBiomeScene(Previous):
    _FOREST_PERIOD = LW * 4

    def _edge_canopy(self, s, side, seed, height_shift=0):
        rng = random.Random(seed)
        dark=(56,102,84); mid=(76,128,103); light=(106,158,126)
        if side == 'left':
            cx = rng.randint(8, 18); half = rng.randint(14, 20)
        else:
            cx = LW - rng.randint(8, 18); half = rng.randint(14, 20)
        top = 152 + height_shift + rng.randint(-3, 3)
        pts=[
            (max(0,cx-half), 214),
            (max(0,cx-half+4), top+18),
            (max(0,cx-half+8), top+10),
            (max(0,cx-half+12), top+7),
            (cx-4, top+3), (cx, top), (cx+4, top+3),
            (min(LW-1,cx+half-10), top+8),
            (min(LW-1,cx+half-5), top+12),
            (min(LW-1,cx+half), 214),
        ]
        pygame.draw.polygon(s, dark, pts)
        pygame.draw.line(s, mid, (max(0,cx-half+8), top+12), (cx-2, top+5), 1)
        pygame.draw.line(s, light, (cx, top+5), (min(LW-1,cx+8), top+7), 1)
        for _ in range(4):
            x = min(LW-2, max(1, cx + rng.randint(-half+5, half-5)))
            y = min(212, max(top+4, top + rng.randint(5, 16)))
            pygame.draw.line(s, light if rng.random()>.45 else mid, (x, y), (min(LW-1, x+2), y), 1)

    def _mid_depth_polish(self, s, index):
        # Bosquetes laterais para quebrar cortes verticais percebidos em corrida.
        self._edge_canopy(s, 'left', 14900 + index*3, height_shift=(index % 3)-1)
        self._edge_canopy(s, 'right', 14901 + index*3, height_shift=((index+1) % 3)-1)

        # Troncos/arbustos distantes discretos no meio para ampliar profundidade.
        rng = random.Random(14950 + index * 17)
        dark=(90,136,116); mid=(111,155,133); light=(139,181,158)
        for cx in (34, 72, 114, 152, 192):
            if (cx + index) % 2 == 0:
                top = 188 + rng.randint(-5, 4)
                half = 7 + rng.randint(0, 4)
                pts=[
                    (cx-half, 214), (cx-half+2, top+11), (cx-half+5, top+6),
                    (cx-2, top+2), (cx+1, top), (cx+5, top+2),
                    (cx+half-3, top+6), (cx+half, 214)
                ]
                pygame.draw.polygon(s, dark, pts)
                pygame.draw.line(s, mid, (cx-half+3, top+8), (cx, top+4), 1)
                if cx % 3:
                    pygame.draw.line(s, light, (cx, top+5), (cx+4, top+6), 1)

        # Microfolhagens baixas entre os arbustos principais, discretas.
        grass_dark=(61,112,73); grass_mid=(102,156,96); grass_hi=(164,208,132)
        for base in (18, 48, 86, 126, 167, 203):
            for j in range(3):
                x = min(LW-3, max(2, base + j*3 + ((index+j) % 3) - 1))
                y = 216 + (j % 2)
                pygame.draw.line(s, grass_dark, (x, y), (x+1, y-4-j), 1)
                if j != 1:
                    pygame.draw.line(s, grass_mid, (x+1, y-1), (x+2, y-3-j), 1)
            if (base + index) % 4 == 0:
                pygame.draw.rect(s, grass_hi, (base+1, 211, 1, 1))

    def _far_depth_polish(self, s, index):
        # Atmosfera baixa muito sutil para separar melhor horizonte e camada média.
        veil = pygame.Surface((LW, 22), pygame.SRCALPHA)
        for y in range(22):
            a = max(0, 22 - y)
            veil.fill((132, 171, 156, 3 + a // 3), (0, y, LW, 1))
        s.blit(veil, (0, 193))

        # Silhuetas extras pequenas e irregulares para evitar repetição do fundo.
        dark=(88,132,119); light=(118,160,145)
        rng = random.Random(14980 + index * 11)
        for cx in (12, 48, 83, 121, 158, 196, 218):
            if (cx//12 + index) % 2 == 0:
                top = 183 + rng.randint(-4, 3)
                half = 5 + rng.randint(0, 3)
                pts=[(max(0,cx-half),214),(cx-half+2, top+8),(cx-1, top+2),(cx+2, top),(cx+half-1, top+5),(min(LW-1,cx+half),214)]
                pygame.draw.polygon(s, dark, pts)
                pygame.draw.line(s, light, (max(0,cx-2), top+4), (min(LW-1,cx+2), top+3), 1)

    def _near_ground_polish(self, s, index):
        # Pequenos tufos e trepadeiras rasteiras para enriquecer o primeiro plano.
        rng = random.Random(15030 + index * 29)
        dark=(39,83,61); mid=(74,131,82); hi=(140,191,111)
        positions=(9, 28, 61, 102, 141, 179, 209)
        for n, base in enumerate(positions):
            if (n + index) % 2 == 0:
                h = 4 + (n % 3)
                pygame.draw.line(s, dark, (base, 223), (base+1, 223-h), 1)
                pygame.draw.line(s, mid, (base+1, 223), (base+2, 223-h+1), 1)
                if n % 3 == 0:
                    pygame.draw.line(s, hi, (base+2, 222), (base+3, 223-h+1), 1)
        # folhas pequenas dispersas no chão alto (sem entrar na pista)
        leaf_cols=((116,174,98),(171,212,124),(82,136,80))
        for x in (16, 44, 73, 118, 153, 188, 214):
            yy = 222 - (x % 2)
            c = leaf_cols[(x // 7 + index) % len(leaf_cols)]
            pygame.draw.line(s, c, (x, yy), (min(LW-1,x+2), yy-1), 1)

    def _forest_chunk(self, layer, index):
        s = super()._forest_chunk(layer, index)
        if layer == 'far':
            self._far_depth_polish(s, index)
        elif layer == 'mid':
            self._mid_depth_polish(s, index)
        elif layer == 'near':
            self._near_ground_polish(s, index)
        return s
