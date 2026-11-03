"""Cidade v3.124: céu único compartilhado ao fundo, sem duplicação vertical."""
from pixelrush_city2_v3123 import CityPilotScene as CidadeAnterior
from pixelrush_city2_v3115 import DEFAULT_NORMAL, NEUTRAL_FLOW
import os
import pygame
# Configurada no boot QA; nenhum getenv no quinto quadro.
_QA_DIRECT_NIGHT_MULT=os.environ.get('PIXELRUSH_QA_DIRECT_NIGHT_MULT','1')=='1'

class CityPilotScene(CidadeAnterior):
    def _make_near_variant(self, idx):
        # Concreto em lugar da antiga faixa gramada no fundo da pista.
        import pygame
        v = super()._make_near_variant(idx)
        pygame.draw.rect(v.image, (109, 108, 110), (0, 225, 450, 6))
        pygame.draw.line(v.image, (174, 171, 162), (0, 225), (449, 225), 1)
        pygame.draw.rect(v.material, (105, 100, 98), (0, 225, 450, 6))
        return v

    def render_scene(self, target, travel, frame, night, climate, phase,
                     foreground_only=False, map_kind='image'):
        quality=self.visual_quality
        # O céu é desenhado uma única vez pelo ParallaxBackground e fica
        # visível pelas transparências das camadas da Cidade (TOP..GROUND).
        if not foreground_only:
            if map_kind == 'normal':
                target.fill(DEFAULT_NORMAL)
            elif map_kind == 'flow':
                target.fill(NEUTRAL_FLOW)
            else:
                target.fill((0, 0, 0, 0))
        near_tiles=None
        for layer in self.layers:
            if layer.foreground!=foreground_only:
                continue
            # near e reutilizado nas luzes; outros planos consumidos uma vez.
            visible=(tuple(self._layer_tiles(travel,layer))
                     if layer.name == 'near' else self._layer_tiles(travel,layer))
            for x,variant,flip in visible:
                self._render_chunk(target,variant,flip,int(x),frame,night,climate,phase,map_kind)
            if layer.name=='mid' and not foreground_only:
                self._draw_train(target,travel,frame,night,map_kind)
                if map_kind=='image':
                    self.life.draw_bridge_life(target,travel,night,frame,quality)
                    self.life.draw_suspended_cables(target,travel,frame,quality)
                    self.life.draw_pigeons(target,travel,frame,quality)
            if layer.name=='near' and not foreground_only:
                near_tiles=visible
        if map_kind=='image' and not foreground_only:
            # Escurece apenas os prédios, sem escurecer o céu de novo.
            if night>.12:
                key = min(12, max(0, int(night*12 + .5)))
                # QA751: um fill especial (em C/SDL) multiplica diretamente
                # os canais do destino, com os MESMOS fatores e arredondamento
                # de blit RGBA_MULT de uma Surface uniforme 450x500. Evita
                # criar/manter ate 13 Surfaces RGBA (~11 MiB) e um blit inteiro.
                # Testes direcionados pygame-ce 2.5.8: RGB/RGBA byte-identicos.
                cor=(255-key*8,255-key*7,255-key*4,255)
                if _QA_DIRECT_NIGHT_MULT:
                    target.fill(cor,special_flags=pygame.BLEND_RGBA_MULT)
                else:
                    veil = self._night_veils.get(key)
                    if veil is None:
                        veil=pygame.Surface(target.get_size(),pygame.SRCALPHA)
                        veil.fill(cor)
                        self._night_veils[key]=veil
                    target.blit(veil,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
            if near_tiles:
                self.life.draw_windows_lights(target,near_tiles,night,frame,quality,'image')
            self.life.draw_atmosphere(target,travel,frame,night,climate,quality)
            self.life.draw_wet_reflections(target,travel,frame,night,climate)
        elif map_kind=='fxmask' and near_tiles:
            self.life.draw_windows_lights(target,near_tiles,night,frame,quality,'fxmask')
        if map_kind=='geometry' and not foreground_only:
            # QA752: somente Surface persistente PROPRIA do World; evita
            # um copy/scale completo ao guardar geometry_view. Destinos
            # efemeros continuam fazendo o snapshot original.
            if getattr(self,'_qa_geometry_borrow_target',None) is target:
                self._geometry_view=target
            else:
                # QA750: a copy() criava 900 KiB por passe de geometria.
                # A escala 1:1 grava os canais RGBA crus no buffer existente,
                # sem o alpha-blend cumulativo que um blit produziria.
                if (self._geometry_view is None or
                        self._geometry_view.get_size()!=target.get_size() or
                        self._geometry_view.get_bitsize()!=target.get_bitsize() or
                        self._geometry_view.get_masks()!=target.get_masks() or
                        bool(self._geometry_view.get_flags() & pygame.SRCALPHA)!=
                        bool(target.get_flags() & pygame.SRCALPHA)):
                    self._geometry_view=target.copy()
                else:
                    pygame.transform.scale(target,target.get_size(),self._geometry_view)
        self._last_state=(travel,frame,night,climate,phase)
