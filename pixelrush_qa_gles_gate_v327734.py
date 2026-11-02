# -*- coding: utf-8 -*-
"""QA v3.277.34: gate conservador de migracao de camera para OpenGL ES.

Nao cria contexto GL, nao altera a Surface SDL, nao faz upload/readback e
nunca ativa GPU sem equivalencia visual e benchmark no aparelho real.
Somente informacao diagnostica obtida do display SDL JA INICIALIZADO.
"""
def diagnosticar():
    try:
        import pygame
        inicializado = bool(pygame.display.get_init())
        tela = pygame.display.get_surface() if inicializado else None
        flags = int(tela.get_flags()) if tela is not None else None
        gl_nativo = bool(flags is not None and flags & pygame.OPENGL)
        try:
            driver = pygame.display.get_driver() if inicializado else None
        except pygame.error:
            driver = None
        # O projeto usa set_mode() sem pygame.OPENGL e display.flip().
        # SDL_GetWindowSurface nao pode coexistir com o renderer 3D na
        # MESMA janela. Mesmo numa janela GL, a equivalencia nao foi provada.
        return {
            'schema': 'pixelrush.qa.gles_gate.v1',
            'tipo_janela': 'opengl' if gl_nativo else (
                'surface_sdl' if tela is not None else 'sem_janela'),
            'sdl_driver': driver,
            'ativa_gpu': False,
            'integracao_aprovada': False,
            'fallback_cpu_preservado': True,
            'motivos': [
                'SDL2 proibe misturar WindowSurface e renderer/GL na mesma janela',
                'interpolacao linear GLES2/GLES3 divergiu de smoothscale pygame-ce',
                'sem benchmark na GPU real do Android e emuladores',
                'migracao precisa apresentar na GPU sem readback para evitar novo custo',
            ],
        }
    except (ImportError, RuntimeError):
        return {
            'schema': 'pixelrush.qa.gles_gate.v1',
            'integracao_aprovada': False, 'ativa_gpu': False,
            'fallback_cpu_preservado': True, 'tipo_janela': 'indisponivel',
            'motivos': ['SDL nao disponivel para diagnostico'],
        }
