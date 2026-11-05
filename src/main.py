# -*- coding: utf-8 -*-
"""Entrada desktop alternativa: python src/main.py ou python -m src.main.

A entrada Android continua no main.py existente; sem reimplementacao do jogo.
"""
if __package__:
    from .pixelrush.game import iniciar_desktop
else:
    from pixelrush.game import iniciar_desktop


if __name__ == "__main__":
    iniciar_desktop()
