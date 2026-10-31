"""v3.277.6-PROD — origem dos atlas otimizados, preservando os wrappers.

O carregador é integrado ao ponto de criação original de v3.185.
Não substitui _get_modular: continuam executando todos os tratamentos visuais
registrados pelas versões 3.197, 3.200, 3.220 e correções posteriores.
A modificação do construtor ocorre uma vez, nesta edição PROD apenas.
"""
import pixelrush_world_v3185 as _motor_texturas
from pixelrush_atlas_prod_v32776 import carregar_cena
_motor_texturas.ModularBiomeScene = carregar_cena
from pixelrush_world_prod_v32775 import LivingWorld
