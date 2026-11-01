# -*- coding: utf-8 -*-
"""QA v3.277.29: eliminacao de limpeza redundante do compositor 2.5D.

Cada render_scene nao-foreground ja limpa integralmente o buffer antes de desenhar
o primeiro pixel. A antiga _city_surface fazia OUTRO fill de 450 x 500 pixels
imediatamente antes. A eliminacao nao pula camadas nem altera sua ordem.
Foregound permanece com o caminho original, sem risco a mapas com transparencia.
Compatibilidade testada com SDL dummy pixel a pixel, multiplos canais e cenas.
"""
import pygame

_INSTALADO = False
_ORIGINAL = None


def instalar():
    global _INSTALADO, _ORIGINAL
    if _INSTALADO:
        return
    from pixelrush_world_v3130 import LivingWorld
    _ORIGINAL = LivingWorld._city_surface

    def _city_surface_qa(self, kind='image', foreground_only=False):
        if foreground_only:
            return _ORIGINAL(self, kind, foreground_only)
        chave = (kind, False)
        surf = self._city_surfaces.get(chave)
        if surf is None:
            from pixelrush_world_v3130 import WIDTH, GROUND, TOP
            surf = pygame.Surface((WIDTH, GROUND - TOP), pygame.SRCALPHA)
            self._city_surfaces[chave] = surf
        # render_scene executa fill completo para cada kind, inclusive image.
        from pixelrush_world_v3130 import MODULAR_BIOMES
        cena = self._get_modular() if self.biome in MODULAR_BIOMES else self.city2
        cena.render_scene(surf, self.travel, self.frame, self.night,
                          self.climate, self.phase, foreground_only=False,
                          map_kind=kind)
        return surf

    LivingWorld._city_surface = _city_surface_qa
    _INSTALADO = True


def restaurar_para_teste():
    """Somente em regressao offline, nunca executado no APK."""
    global _INSTALADO
    if _INSTALADO:
        from pixelrush_world_v3130 import LivingWorld
        LivingWorld._city_surface = _ORIGINAL
        _INSTALADO = False
