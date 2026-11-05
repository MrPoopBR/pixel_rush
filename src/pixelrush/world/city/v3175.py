"""v3.175.0 — tratamento de profundidade da Cidade, sem novos prédios.

Reutiliza a instância da cidade já criada pelo jogo, evitando gerar os
atlases/sprites uma segunda vez e sem tocar nos mapas de colisão/efeitos.
"""
from pixelrush_city2_v3125 import CityPilotScene as Anterior
from pixelrush_composicao_v3175 import compor_plano


def aplicar_composicao_cidade(scene):
    if getattr(scene, '_composicao_3175', False):
        return scene
    for layer in scene.layers:
        if layer.name not in ('far', 'mid') or layer.foreground:
            continue
        seen = set()
        for variant in layer.variants:
            if id(variant.image) in seen:
                continue
            seen.add(id(variant.image))
            compor_plano(variant.image, 'cidade', layer.name)
    scene._composicao_3175 = True
    return scene


class CityPilotScene(Anterior):
    """Utilizada somente no QA para comparar variantes independentes."""
    def __init__(self):
        super().__init__()
        aplicar_composicao_cidade(self)
