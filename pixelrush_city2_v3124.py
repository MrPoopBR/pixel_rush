"""Cidade v3.124: céu único compartilhado ao fundo, sem duplicação vertical."""
from pixelrush_city2_v3123 import CityPilotScene as CidadeAnterior
from pixelrush_city2_v3115 import DEFAULT_NORMAL, NEUTRAL_FLOW
import os
import pygame
# QA R23: candidato fechado ate completar A/B RGBA e desempenho.
_QA_SKIP_HIDDEN_TRAIN=os.environ.get('PIXELRUSH_QA_SKIP_HIDDEN_TRAIN','1')=='1'
# LAB R26: evitar enumeracao de far/mid inteiramente cobertos nos mapas
# opacos NORMAL/FLOW. R26 CI #42084960670: 260 RGBA exatos, p50
# quinto quadro -3.06% no Linux; opt-out '0'. Inerte sem QA786.
_QA_R26_SKIP_OCCLUDED_LAYERS=os.environ.get('PIXELRUSH_QA_R26_SKIP_OCCLUDED_LAYERS','1')=='1'
# Configurada no boot QA; nenhum getenv no quinto quadro.
_QA_DIRECT_NIGHT_MULT=os.environ.get('PIXELRUSH_QA_DIRECT_NIGHT_MULT','1')=='1'
# QA754: near_tiles e consumido somente por image/fxmask (luzes); em
# normal/geometry/flow/material gerador e suficiente sem alocar tuple.
_QA_NEAR_TUPLE_ON_DEMAND=os.environ.get('PIXELRUSH_QA_NEAR_PLAN_ON_DEMAND','1')=='1'
# QA755: normal/flow preenchem toda a Surface com alpha 255 no inicio
# da passagem. So dentro desse escopo o destino SRCALPHA equivale ao
# destino RGB para recortes de fontes com alpha 0. Demais canais intactos.
_QA_TECH_OPAQUE_BOUNDS=os.environ.get('PIXELRUSH_QA_TECH_OPAQUE_BOUNDS','1')=='1'

class CityPilotScene(CidadeAnterior):
    def _make_near_variant(self, idx):
        # Concreto em lugar da antiga faixa gramada no fundo da pista.
        import pygame
        v = super()._make_near_variant(idx)
        pygame.draw.rect(v.image, (109, 108, 110), (0, 225, 450, 6))
        pygame.draw.line(v.image, (174, 171, 162), (0, 225), (449, 225), 1)
        pygame.draw.rect(v.material, (105, 100, 98), (0, 225, 450, 6))
        # Juntas da calçada criadas uma só vez na construção do atlas.
        for jx in range(56 + (idx % 3) * 12, 445, 96):
            pygame.draw.line(v.image, (77, 79, 83), (jx, 226), (jx, 230), 1)
            pygame.draw.line(v.image, (158, 155, 151), (jx + 1, 226), (jx + 1, 230), 1)
            pygame.draw.line(v.material, (93, 91, 91), (jx, 226), (jx, 230), 1)
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
        # QA755: contexto somente quando fill do mapa técnico acabou de
        # estabelecer alfa 255 em CADA pixel. O marcador é local a esta
        # chamada, restaurado mesmo se SDL levantar exceção.
        anterior_opaque=getattr(self,'_qa_opaque_safe_target',None)
        seguro_opaque=bool(
            _QA_TECH_OPAQUE_BOUNDS and not foreground_only and
            map_kind in ('normal','flow') and
            (target.get_flags() & pygame.SRCALPHA) and
            target.get_alpha() in (None,255))
        self._qa_opaque_safe_target=target if seguro_opaque else None
        try:
            near_tiles=None
            for layer in self.layers:
                if layer.foreground!=foreground_only:
                    continue
                # near e reutilizado nas luzes; outros planos consumidos uma vez.
                # QA754: mapas tecnicos sem luzes nunca consultam near_tiles;
                # nao materializar tuple que seria descartada apos cada layer.
                usa_near=(layer.name=='near' and not foreground_only and
                          map_kind in ('image','fxmask'))
                # QA786 valida cobertura near, identidade de todos os atlases,
                # formato e ordem das camadas nesta chamada de render.
                # Se validado, nem materializar tiles far/mid; a near opaca
                # os substitui em sua totalidade, inclusive sprites tecnicos.
                oculto=(_QA_R26_SKIP_OCCLUDED_LAYERS and
                        not foreground_only and layer.name in ('far','mid') and
                        map_kind in ('normal','flow') and
                        getattr(self,'_qa_opaque_maps_pass',None)==map_kind)
                visible=(() if oculto else
                         (tuple(self._layer_tiles(travel,layer))
                         if (usa_near if _QA_NEAR_TUPLE_ON_DEMAND
                             else layer.name=='near')
                         else self._layer_tiles(travel,layer)))
                for x,variant,flip in visible:
                    self._render_chunk(target,variant,flip,int(x),frame,night,climate,phase,map_kind)
                if layer.name=='mid' and not foreground_only:
                    # Skip somente se QA786 confirmou near opaco sobre todos
                    # os pixels dos mapas NORMAL/FLOW no render atual.
                    if not (_QA_SKIP_HIDDEN_TRAIN and map_kind in ('normal','flow')
                            and getattr(self,'_qa_opaque_maps_pass',None)==map_kind):
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
                    self._qa_geometry_borrowed_surface=target
                else:
                    # QA750: a copy() criava 900 KiB por passe de geometria.
                    # A escala 1:1 grava os canais RGBA crus no buffer existente,
                    # sem o alpha-blend cumulativo que um blit produziria.
                    if (self._geometry_view is None or
                            self._geometry_view is target or
                            self._geometry_view is getattr(self,'_qa_geometry_borrowed_surface',None) or
                            self._geometry_view.get_size()!=target.get_size() or
                            self._geometry_view.get_bitsize()!=target.get_bitsize() or
                            self._geometry_view.get_masks()!=target.get_masks() or
                            bool(self._geometry_view.get_flags() & pygame.SRCALPHA)!=
                            bool(target.get_flags() & pygame.SRCALPHA)):
                        self._geometry_view=target.copy()
                        self._qa_geometry_borrowed_surface=None
                    else:
                        pygame.transform.scale(target,target.get_size(),self._geometry_view)
            self._last_state=(travel,frame,night,climate,phase)
        finally:
            self._qa_opaque_safe_target=anterior_opaque
