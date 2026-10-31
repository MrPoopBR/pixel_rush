"""Pixel Rush v3.161.0 — microacabamento de Ilhas Celestiais.

Somente arte pré-renderizada (uma vez ao construir as superfícies de chunks).
Não modifica clima, partículas dinâmicas, física, colisões ou biomas externos.
"""
from pixelrush_biomes2_v3160 import ModularBiomeScene as Previous
import pygame


# Âncoras extraídas das geometrias existentes na v3.158.0; não são spawns.
_FAR_ISLANDS = {
    'acropole_marmore': ((12, 116, 74, 42), (134, 127, 60, 35)),
    'jardins_bioluminescentes': ((16, 122, 70, 40), (126, 112, 78, 48)),
    'residencial_suspenso': ((18, 120, 68, 40), (129, 127, 65, 37)),
    'santuario_cristal': ((14, 123, 74, 42), (132, 115, 70, 45)),
    'pontes_celestes': ((12, 128, 62, 38), (127, 120, 74, 41)),
    'docas_aereas': ((16, 124, 68, 39), (128, 116, 76, 45)),
}
_MID_ISLANDS = {
    'acropole_marmore': ((14, 148, 82, 53), (126, 140, 78, 49)),
    'jardins_bioluminescentes': ((18, 147, 75, 50), (122, 138, 84, 55)),
    'residencial_suspenso': ((16, 150, 79, 49), (128, 145, 74, 45)),
    'santuario_cristal': ((14, 150, 77, 50), (120, 142, 86, 57)),
    'pontes_celestes': ((16, 147, 72, 46), (116, 142, 92, 53)),
    'docas_aereas': ((15, 149, 76, 48), (127, 141, 82, 52)),
}


class ModularBiomeScene(Previous):
    def _district_name(self, index):
        """Não permitir que nomes celestiais vazem para a Cidade Futurista.

        A colisão entre dois métodos homônimos já estava na base v3.160.0;
        restabelece os nomes da arquitetura futurista da v3.157.0.
        """
        if self.biome == 'cidade_futurista':
            return ('corporativo', 'residencial', 'transito',
                    'holografico', 'industrial', 'jardins')[index % 6]
        return super()._district_name(index)

    def _premium_pass_celestial_layers(self):
        """Aproveita o acabamento anterior; acrescenta apenas detalhes ancorados."""
        super()._premium_pass_celestial_layers()
        if self.biome != 'ilhas_celestes':
            return
        for layer in ('far', 'mid'):
            for index, surface in enumerate(self._layers[layer]):
                district = self._district_name(index if layer == 'far' else index + 2)
                geometry = _FAR_ISLANDS[district] if layer == 'far' else _MID_ISLANDS[district]
                pal = self._district_palette(district)
                for island_index, (x, y, width, height) in enumerate(geometry):
                    self._edge_and_rock_detail(surface, x, y, width, height, pal,
                                               phase=(index + island_index) % 3,
                                               distant=layer == 'far')
        for index, surface in enumerate(self._layers['near']):
            pal = self._district_palette(self._district_name(index + 4))
            self._bridge_marble_detail(surface, pal, index)

    @staticmethod
    def _safe_pixel(surface, x, y):
        return (0 <= x < surface.get_width() and 0 <= y < surface.get_height()
                and surface.get_at((x, y)).a != 0)

    def _edge_and_rock_detail(self, s, x, y, w, h, pal, phase, distant):
        # Marcas de borda apenas sobre o platô existente, não no céu.
        # O baixo contraste impede que o desenho pareça uma barreira sobre o templo.
        edge = pal['grass_dark'] if distant else pal['grass']
        rock_hi = pal['side'] if distant else pal['marble']
        mineral = pal['accent']
        for offset in range(12 + phase, w - 12, 13):
            xx = x + offset
            yy = y + 7
            if self._safe_pixel(s, xx, yy):
                pygame.draw.line(s, edge, (xx, yy), (xx + 3, yy), 1)

        # Estratos e facetas presos diretamente à massa rochosa; nunca em x/y aleatório.
        for frac, skew in ((0.29, 1), (0.62, -1)):
            xx = x + int(w * frac)
            yy = y + int(h * (0.35 if frac < .5 else .52))
            # Guarde local do traço inteiramente em pixels já ocupados.
            if all(self._safe_pixel(s, xx + dx, yy + dy)
                   for dx, dy in ((0, 0), (2, skew), (4, skew))):
                pygame.draw.line(s, rock_hi, (xx, yy), (xx + 2, yy + skew), 1)
                pygame.draw.line(s, mineral, (xx + 3, yy + skew), (xx + 4, yy + skew), 1)

        # Reflexo localizado ao longo da face do penhasco, sem aumentar partículas.
        xx = x + w // 2 - 2
        yy = y + h // 2
        if all(self._safe_pixel(s, xx, yy + k) for k in range(4)):
            pygame.draw.line(s, pal['side'], (xx, yy), (xx, yy + 3), 1)

    @staticmethod
    def _bridge_marble_detail(s, pal, index):
        # Pino de apoio nos suportes que JÁ existem; sem mexer no corredor da pista.
        supports = (14, 46, 81, 116, 154, 191, 214)
        for x in supports:
            pygame.draw.line(s, pal['marble'], (x + 1, 235), (x + 3, 235), 1)
            pygame.draw.rect(s, pal['gold'], (x + 2, 239, 1, 1))
        # Frisos curtos de mármore, alinhados aos 26 px das placas existentes.
        for x in range(9 + (index % 3) * 2, 211, 26):
            pygame.draw.line(s, pal['marble_hi'], (x, 233), (x + 5, 233), 1)
            pygame.draw.line(s, pal['joint'], (x + 2, 234), (x + 4, 234), 1)
