# -*- coding: utf-8 -*-
"""Funções extraídas sem reescrever algoritmos da v3.277.89-QA.
Nomes de funções permanecem importados no motor nos pontos originais.
"""

import pygame

def hitbox_disparo_laser(laser):
    # O brilho vermelho da borda não deve matar sem contato com o feixe central.
    return pygame.Rect(laser.rect.left, laser.rect.top + 5,
                       laser.rect.width, max(1, laser.rect.height - 10))

