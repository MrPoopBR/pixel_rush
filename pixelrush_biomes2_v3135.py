"""Pixel Rush v3.135 — arte viva ancorada aos chunks, sem novas colisões.

Aproveita o motor modular v3.134, sem executar IAs, FFT, sombreamento pesado
ou criar superfícies no loop. Props de fundo predesenhados (e não obstáculos)
compõem pequenas cenas reativas à passagem, luz e clima. Normal e material são
refinados *sob demanda* no cache técnico já existente, para o shader ModernGL.
"""
import math
import pygame
import numpy as np
from pixelrush_biomes2_v3134 import ModularBiomeScene as Anterior, MODULAR_BIOMES, EXTRA_BIOMES

TEMAS = {
    'floresta': ('BORDA DO BOSQUE', 'CLAREIRA DOS PASSAROS', 'RUINAS E RIO', 'ARVOREDO'),
    'vulcao': ('CRATERAS', 'COLUNAS DE BASALTO', 'CAMPOS DE FUMACA', 'RIO DE LAVA'),
    'cidade_futurista': ('TORRES NEON', 'AEROVIA', 'DISTRITO INDUSTRIAL', 'CENTRO HOLOGRAFICO'),
    'ilhas_celestes': ('JARDINS SUSPENSOS', 'PONTES DE NUVENS', 'TEMPLOS', 'QUEDAS DE AGUA'),
}


def _arte_ator(bioma, fase):
    """Quadros discretos; gerados uma vez na primeira visita ao bioma."""
    s = pygame.Surface((42, 25), pygame.SRCALPHA)
    if bioma == 'floresta':
        dx = (-2, 0, 2, 0)[fase % 4]
        # Ave de silhueta reconhecível, com 2 asas e bico claro.
        pygame.draw.polygon(s, (40, 68, 72), ((2, 14), (12, 7+dx), (21, 14), (16, 19)))
        pygame.draw.polygon(s, (78, 111, 115), ((21, 14), (35, 6-dx), (39, 17), (28, 19)))
        pygame.draw.ellipse(s, (133, 162, 145), (16, 12, 15, 10))
        pygame.draw.circle(s, (232, 223, 178), (28, 13), 2)
        pygame.draw.polygon(s, (226, 172, 91), ((30, 15), (41, 17), (30, 19)))
    elif bioma == 'vulcao':
        pygame.draw.ellipse(s, (61, 56, 63), (2, 18, 39, 6))
        # Pluma que cresce acima da cratera e volta sem emitir partícula.
        dy = (2, 0, -2, 0)[fase % 4]
        for x, y, r in ((12, 15+dy, 7), (24, 11+dy, 8), (29, 6+dy, 6)):
            pygame.draw.circle(s, (111, 99, 105), (x, y), r)
            pygame.draw.circle(s, (159, 139, 136), (x-2, y-2), max(2,r//2))
        pygame.draw.line(s, (255, 166, 82), (8, 21), (34, 21), 2)
    elif bioma == 'cidade_futurista':
        # Veículo ao fundo: não tem hitbox, não invade a faixa de corrida.
        pygame.draw.polygon(s, (46, 54, 89), ((1, 14), (8, 6), (27, 5), (38, 12), (40, 19), (4, 20)))
        pygame.draw.rect(s, (84, 154, 202), (10, 8, 20, 6))
        pygame.draw.line(s, (107, 236, 242), (4, 18), (39, 18), 2)
        for x in (10, 32):
            pygame.draw.rect(s, (102, 229, 252) if fase % 2 else (232, 125, 215), (x, 20, 5, 2))
    else:
        # Pequenino planador de fundo: asa oscilante, não um inimigo.
        dy = (-3, 0, 3, 0)[fase % 4]
        pygame.draw.polygon(s, (131, 179, 199), ((3, 11+dy), (20, 9), (21, 17), (10, 21)))
        pygame.draw.polygon(s, (187, 224, 229), ((21, 16), (37, 11-dy), (34, 20), (22, 20)))
        pygame.draw.ellipse(s, (108, 147, 177), (16, 11, 13, 9))
        pygame.draw.circle(s, (244, 244, 205), (28, 13), 2)
    return pygame.transform.scale(s, (84, 50))


class ModularBiomeScene(Anterior):
    def __init__(self, biome):
        super().__init__(biome)
        self._atores = ()
        if biome in EXTRA_BIOMES:
            self._atores = tuple(_arte_ator(biome, fase) for fase in range(4))

    def _tile_map(self, layer, idx, kind):
        if self.biome not in EXTRA_BIOMES or kind not in ('normal', 'material'):
            return super()._tile_map(layer, idx, kind)
        key = (layer, idx, kind)
        # Usa o MESMO cache LRU do motor. Nunca duplica mapa nem cria por frame.
        if key in self._map_cache:
            self._map_cache.move_to_end(key)
            return self._map_cache[key]
        mapa = super()._tile_map(layer, idx, kind)
        original = self._layers[layer][idx]
        rgb = pygame.surfarray.array3d(original).astype(np.float32)
        alpha = pygame.surfarray.array_alpha(original) > 90
        dst = pygame.surfarray.pixels3d(mapa)
        if kind == 'normal':
            lum = (rgb[:,:,0] * .26 + rgb[:,:,1] * .64 + rgb[:,:,2] * .10) / 255.0
            # Relevo discreto, sem arredondar os pixels da pixel art no albedo.
            gx, gy = np.gradient(lum)
            nx, ny = -gx*.85, -gy*.85
            nz = np.ones_like(nx)
            norm = np.sqrt(nx*nx+ny*ny+nz*nz)
            dst[:,:,0] = np.where(alpha, np.clip(128 + nx/norm * 127, 0, 255), 0).astype('uint8')
            dst[:,:,1] = np.where(alpha, np.clip(128 + ny/norm * 127, 0, 255), 0).astype('uint8')
            dst[:,:,2] = np.where(alpha, np.clip(128 + nz/norm * 127, 0, 255), 0).astype('uint8')
        else:
            # R=roughness, G=oclusão local, B=refletividade na convenção
            # GLSL existente. Metal/água/cristais mais especulares; folhagem opaca.
            palette = {
                'floresta': (.87,.81,.12),
                'vulcao': (.79,.74,.22),
                'cidade_futurista': (.58,.82,.49),
                'ilhas_celestes': (.68,.86,.36),
            }
            rough, ao, spec = palette[self.biome]
            brilho = (rgb[:,:,0] + rgb[:,:,1] + rgb[:,:,2]) / (3*255)
            ajuste = np.clip(brilho-.48,-.35,.35)
            dst[:,:,0] = np.where(alpha, np.clip((rough-.18*ajuste)*255, 0, 255), 0).astype('uint8')
            dst[:,:,1] = np.where(alpha, np.clip((ao+.12*ajuste)*255, 0, 255), 0).astype('uint8')
            dst[:,:,2] = np.where(alpha, np.clip((spec+.28*ajuste)*255, 0, 255), 0).astype('uint8')
        del dst
        return mapa

    def _ator_x(self, travel, seed, passo=535):
        # Posição em mundo, deslocamento da MESMA camada média (.25 * .5).
        pos = seed*passo + 120
        off = travel*.25*.5
        return int((pos - off) % (450+130))-85

    def _microeventos(self, surface, travel, frame, climate, night):
        if not self._atores:
            return
        # Dois atores distantes e previsíveis, sempre ATRÁS dos perigos reais.
        acelerado = climate in ('vento_folhas','tempestade_vento','vento_neon','cinzas','chuva_meteoros')
        for i in (0,1):
            x = self._ator_x(travel, i+1, 575 if i else 525)
            # Elimina qualquer ator fora da viewport, sem criar sprite nem RNG.
            if x < -84 or x > 450:
                continue
            pulso = math.sin((frame+i*23)*.072)
            ybase = {'floresta':112,'vulcao':203,'cidade_futurista':117,'ilhas_celestes':109}[self.biome]
            yy = int(ybase + pulso*(5 if acelerado else 2))
            if self.biome == 'floresta' and 82 <= x <= 164:
                # Bando reage ao corredor aproximando-se (visual, não IA).
                yy -= int((164-x)*.26)
            elif self.biome == 'cidade_futurista':
                x += int((frame*1.1)%(65 if acelerado else 95))
            elif self.biome == 'ilhas_celestes' and acelerado:
                yy += int(math.sin(frame*.11+i)*7)
            fase = (frame//(5 if acelerado else 10) + i) % 4
            if self.biome == 'vulcao':
                # Chaminé ancorada no solo distante, sem fumaça flutuante.
                pygame.draw.polygon(surface, (64, 55, 64),
                                    ((x+6, 230), (x+12, 221), (x+36, 216),
                                     (x+67, 222), (x+77, 230)))
                pygame.draw.line(surface, (224, 112, 69), (x+25, 224), (x+57, 224), 2)
            surface.blit(self._atores[fase], (x,yy))
        # Pequenas reações de cena: somente decoração já presa ao cenário.
        if self.biome == 'cidade_futurista' and night>.35:
            x = self._ator_x(travel, 3, 410)
            if 0<x<450:
                pygame.draw.line(surface, (130, 218, 231), (x, 223), (x+18, 223), 1)
        elif self.biome == 'floresta' and climate in ('vento_folhas','polen'):
            x = self._ator_x(travel, 2, 410)
            if 0<x<450:
                pygame.draw.arc(surface, (163, 194, 114), (x, 226, 31, 13), .15, 2.4, 1)

    def render_scene(self, target, travel, frame, night, climate, phase,
                     foreground_only=False, map_kind='image'):
        result = super().render_scene(target, travel, frame, night, climate, phase,
                                      foreground_only=foreground_only, map_kind=map_kind)
        if not foreground_only and map_kind == 'image' and self.biome in EXTRA_BIOMES:
            self._microeventos(target, travel, frame, climate, night)
        return result
