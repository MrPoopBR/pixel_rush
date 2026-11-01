"""Cidade 3.0 viva v3.123.0 — extensao segura da v3.122.0.

Integra eventos de fundo, cables Verlet-like, luz local, clima e micro-cenas.
Efeito exclusivamente cenografico: nao altera o loop fisico nem os obstaculos.
"""
from __future__ import annotations
from collections import OrderedDict
import pygame
from pixelrush_city2_v3122 import CityPilotScene as _City122
from pixelrush_city2_v3115 import DEFAULT_NORMAL, NEUTRAL_FLOW, WIDTH, SCENE_H
from pixelrush_citylife_v3123 import CityLifeDirector


class CityPilotScene(_City122):
    def __init__(self):
        super().__init__()
        self.life=CityLifeDirector()
        self.visual_quality=1
        self._night_veils=OrderedDict()

    def tick_life(self, frame, travel, climate):
        self.life.tick(frame, travel, climate)

    def react_to_player(self,intensity=1.0):
        self.life.react_to_player(intensity)

    def _night_veil(self, night):
        key=max(0,min(12,int(night*12+.5)))
        overlay=self._night_veils.get(key)
        if overlay is None:
            overlay=pygame.Surface((WIDTH,SCENE_H),pygame.SRCALPHA)
            overlay.fill((18,31,63,int(72*key/12)))
            self._night_veils[key]=overlay
        return overlay

    def render_scene(self,target,travel,frame,night,climate,phase,foreground_only=False,map_kind='image'):
        quality=self.visual_quality
        if not foreground_only:
            if map_kind=='image':
                self._draw_sky(target,travel,frame,night,phase,climate)
            elif map_kind=='normal':
                target.fill(DEFAULT_NORMAL)
            elif map_kind=='flow':
                target.fill(NEUTRAL_FLOW)
            else:
                target.fill((0,0,0,0))
        near_tiles=None
        for layer in self.layers:
            if layer.foreground!=foreground_only:
                continue
            visible=tuple(self._layer_tiles(travel,layer))
            for x,variant,flip in visible:
                self._render_chunk(target,variant,flip,int(x),frame,night,climate,phase,map_kind)
            if layer.name=='mid' and not foreground_only:
                self._draw_train(target,travel,frame,night,map_kind)
                if map_kind=='image':
                    # Todos os personagens/veiculos estao ATRAS dos edificios da frente.
                    self.life.draw_bridge_life(target,travel,night,frame,quality)
                    self.life.draw_suspended_cables(target,travel,frame,quality)
                    self.life.draw_pigeons(target,travel,frame,quality)
            if layer.name=='near' and not foreground_only:
                near_tiles=visible
        if map_kind=='image' and not foreground_only:
            # Noite tinge o bairro, mas as fontes de luz surgem depois.
            if night>.12:
                target.blit(self._night_veil(night),(0,0))
            if near_tiles:
                self.life.draw_windows_lights(target,near_tiles,night,frame,quality,'image')
            self.life.draw_atmosphere(target,travel,frame,night,climate,quality)
            self.life.draw_wet_reflections(target,travel,frame,night,climate)
        elif map_kind=='fxmask' and near_tiles:
            self.life.draw_windows_lights(target,near_tiles,night,frame,quality,'fxmask')
        if map_kind=='geometry' and not foreground_only:
            # Apenas geometria cenografica de base. Nao interfere nas hitboxes.
            self._geometry_view=target.copy()
        self._last_state=(travel,frame,night,climate,phase)
