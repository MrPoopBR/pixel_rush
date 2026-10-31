"""Plano I v3.220.0 — acabamento geometricamente ancorado em quatro biomas."""
from pixelrush_world_v3219 import LivingWorld as Anterior
from pixelrush_geometria_v3220 import instalar_modular


class LivingWorld(Anterior):
    def _get_modular(self):
        cena=super()._get_modular()
        instalar_modular(cena,leve=self.lightweight)
        return cena
