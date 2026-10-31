"""Plano G v3.201.0 — otimizacao do passe atmosferico sem alterar a imagem."""
from pixelrush_world_v3200 import LivingWorld as Anterior
from pixelrush_world_v3198 import LivingWorld as AntesDaAtmosfera
from pixelrush_render_otimizado_v3201 import aplicar_otimizado


class LivingWorld(Anterior):
    def _city_surface(self, kind='image', foreground_only=False):
        # Recupera a mesma cena composta herdada pela v3.199 antes da luz:
        # pula APENAS o blit atmosferico de 24 bits (v3.199), substituido pelo
        # MESMO BLEND_RGB_ADD com a superficie ja convertida no cache v3.201.
        resultado = AntesDaAtmosfera._city_surface(self, kind, foreground_only)
        if kind == 'image' and not foreground_only and not self.lightweight:
            aplicar_otimizado(resultado, self.biome, self.night, self.phase, self.climate)
        return resultado
