"""Pixel Rush v3.134: conexão efetiva do mundo modular com todos os passes.

As rotinas herdadas de pixelrush_world_v3130 consultam constantes do módulo
em que foram definidas (não os globals deste arquivo). Ligá-las aqui garante
que imagem, normal, material, flow, geometria, fxmask e foreground concordem.
Não toca em lógica da corrida, clima, física ou colisões.
"""
import os
import pixelrush_world_v3130 as engine
from pixelrush_biomes2_v3134 import ModularBiomeScene, MODULAR_BIOMES

CLASSICOS = os.environ.get('PIXELRUSH_CENARIOS_CLASSICOS') == '1'
# Mantém a opção histórica de cenário clássico sob opt-out explícito.
if not CLASSICOS:
    engine.MODULAR_BIOMES = MODULAR_BIOMES


class LivingWorld(engine.LivingWorld):
    def _get_modular(self):
        if CLASSICOS:
            return super()._get_modular()
        scene = self.modular.get(self.biome)
        if scene is None:
            scene = ModularBiomeScene(self.biome)
            self.modular.clear()  # somente um atlas modular residente no Android
            self.modular[self.biome] = scene
        scene.visual_quality = 0 if self.lightweight else 1
        return scene

    def register_landing(self, player_x, intensity=1.0):
        super().register_landing(player_x, intensity)
        if not CLASSICOS and self.biome in ('floresta','vulcao','cidade_futurista','ilhas_celestes'):
            self._get_modular().registrar_pouso(player_x, intensity)

    def update(self, speed, night=0, climate='limpo', phase=.5):
        super().update(speed, night=night, climate=climate, phase=phase)
        if not CLASSICOS and self.biome in self.modular:
            atlas=self.modular[self.biome]
            if getattr(atlas,'_pouso_restante',0)>0:
                atlas._pouso_restante-=1
