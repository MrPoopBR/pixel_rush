"""v3.177.0 — tratamento de materiais das variantes já existentes da Cidade."""
from pixelrush_city2_v3175 import aplicar_composicao_cidade
from pixelrush_luz_materiais_v3177 import iluminar_material


def aplicar_luz_cidade(scene):
    aplicar_composicao_cidade(scene)
    if getattr(scene,'_iluminacao_3177',False):
        return scene
    for layer in scene.layers:
        if layer.foreground or layer.name not in ('far','mid','near'):
            continue
        vistos=set()
        for variant in layer.variants:
            if id(variant.image) in vistos:
                continue
            vistos.add(id(variant.image))
            iluminar_material(variant.image,'cidade',layer.name)
    scene._iluminacao_3177=True
    return scene
