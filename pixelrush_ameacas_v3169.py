from pixelrush_ameacas_v3168 import *

# Compatibilidade explícita de perigos/ameaças por bioma para auditoria e spawn.
COMPAT_GROUND = {
    'deserto': ('CACTO',),
    'neve': ('espinho_gelo', 'N3', 'N4'),
    'cidade': ('C1', 'C3', 'C4'),
    'vulcao': ('V1', 'V3', 'V4'),
    'floresta': ('F1', 'F3', 'F4'),
    'cidade_futurista': ('CF1', 'CF3', 'CF4'),
    'ilhas_celestes': ('IC1', 'IC3', 'IC4'),
}
