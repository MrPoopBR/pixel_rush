"""Plano G v3.198.0 — profundidade de paralaxe 2.5D, apenas visual.

Nao altera terreno, camera jogavel, speed do player, dados de mapas nem
simulacao. Aceleracao aparente somente dos planos de fundo/médio existentes.
Sem novo atlas, sem shaders, sem renderizações duplicadas nem novos objetos.
"""
from types import MethodType

# Coeficiente relativo a velocidade visual atual (zero modificacoes na NEAR).
# Distante recua, medio se aproxima: a diferenca relativa FAR/MID cresce 40%.
ESCALAS = {'far': 0.75, 'mid': 1.12}


def instalar_modular(scene, leve=False):
    """Preserva todos os passes técnicos. Acopla no _draw_layer JÁ existente."""
    if getattr(scene, '_profundidade_3198', False):
        return scene
    scene._profundidade_3198 = True
    scene._profundidade_modo_leve_3198 = bool(leve)
    if leve:
        return scene
    anterior = scene._draw_layer
    scene._profundidade_draw_anterior_3198 = anterior

    def _draw_paralaxe(self, destino, plano, percurso, tipo):
        if tipo == 'image' and plano in ESCALAS:
            # Apenas localização na composição VISUAL; mapas de geometria,
            # normal/material/fluxo e efeito conservam seu percurso original.
            percurso = percurso * ESCALAS[plano]
        return self._profundidade_draw_anterior_3198(destino, plano, percurso, tipo)

    scene._draw_layer = MethodType(_draw_paralaxe, scene)
    return scene


def instalar_cidade(scene, leve=False):
    """Usa o mesmo gerador de chunks da Cidade e mantém sprites ancorados.

    Nao modifica Layer.speed nem transições do jogo: somente a seleção
    de pedaços de imagem no passe de fundo. Nenhuma alteração em layers.
    """
    if getattr(scene, '_profundidade_3198', False):
        return scene
    scene._profundidade_3198 = True
    scene._profundidade_modo_leve_3198 = bool(leve)
    if leve:
        return scene
    anterior = scene._layer_tiles
    scene._profundidade_tiles_anterior_3198 = anterior
    scene._profundidade_render_imagem_3198 = False

    def _tiles_profundidade(self, percurso, layer):
        if (self._profundidade_render_imagem_3198 and
                not layer.foreground and layer.name in ESCALAS):
            # Em vez de trocar layer.speed, mapeia somente a coordenada
            # de desenho. Os sprites dos chunks seguem seus próprios pais.
            percurso = percurso * ESCALAS[layer.name]
        return self._profundidade_tiles_anterior_3198(percurso, layer)

    original_render = scene.render_scene
    scene._profundidade_render_anterior_3198 = original_render

    def _render_profundidade(self, destino, percurso, frame, noite, clima,
                            fase, foreground_only=False, map_kind='image'):
        anterior_estado = self._profundidade_render_imagem_3198
        self._profundidade_render_imagem_3198 = (map_kind == 'image' and not foreground_only)
        try:
            return self._profundidade_render_anterior_3198(
                destino, percurso, frame, noite, clima, fase,
                foreground_only=foreground_only, map_kind=map_kind)
        finally:
            self._profundidade_render_imagem_3198 = anterior_estado

    scene._layer_tiles = MethodType(_tiles_profundidade, scene)
    scene.render_scene = MethodType(_render_profundidade, scene)
    return scene
