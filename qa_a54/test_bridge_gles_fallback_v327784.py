# -*- coding: utf-8 -*-
"""Fullscreen GLES mais lento que pygame-ce retorna SDL sem janela 450x800."""
import os,pygame
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ['PIXELRUSH_QA_ANDROID']='1'
os.environ['PIXELRUSH_QA_GL_DESKTOP_LAB']='1'
os.environ['PIXELRUSH_QA_GLES_FULLSCREEN_PROBE']='1'
os.environ['PIXELRUSH_QA_GLES3_CONTEXT']='1'
os.environ['PIXELRUSH_QA_GPU_ZOOM']='1'
os.environ['PIXELRUSH_QA_GLES_BRIDGE']='1'
os.environ['PIXELRUSH_QA_GLES_PBO']='0'
import pixelrush_qa_gles_bridge_v327749 as bridge
pygame.init()
bridge.instalar()
try:
    screen=pygame.display.set_mode((450,800),pygame.FULLSCREEN|pygame.SCALED)
    result=bridge.diagnostico()
    print('QA784 fallback fisico',result,'logico',screen.get_size(),
          'fisico',pygame.display.get_window_size())
    assert bridge._BRIDGE.modo=='fallback'
    assert screen.get_size()==(450,800)
    assert pygame.display.get_window_size()!=(450,800)
    assert result['preflight_fisico']['pixels_rgba_exatos'] is True
    assert result['preflight_fisico']['casos_rgba']==8
    assert result['preflight_fisico']['diferencas']==0
    assert result['preflight_fisico']['selecionado'] is False
    screen.fill((15,120,188))
    pygame.display.flip()
    assert bridge.diagnostico()['frames_fallback']>=1
finally:
    bridge.restaurar_para_teste()
    pygame.quit()
