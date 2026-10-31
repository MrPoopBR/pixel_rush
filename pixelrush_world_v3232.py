"""Integra a correção visual localizada FLO-001 no mundo existente."""
from pixelrush_bruma_v3232 import instalar
from pixelrush_world_v3220 import LivingWorld as _LivingWorldAnterior
instalar()

class LivingWorld(_LivingWorldAnterior):
    """Mesma atualização, física e render; bruma alfa corrigida na Floresta."""
    pass
