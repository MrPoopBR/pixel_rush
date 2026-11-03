# -*- coding: utf-8 -*-
"""QA 3.277.47 — arbitragem estrita de CPU/GPU sem trocar a janela SDL.

O presenter GLES2, o shader de paridade exata GLES3 e os PBOs ja existem no
laboratorio. Contudo pygame.display.set_mode sem OPENGL usa WindowSurface:
nao e permitido trocar de backend sem criar um adaptador de input, HUD e
apresentacao compatível. Este gate recusa automaticamente o caminho inseguro
e prepara o contrato para a homologacao final sem fabricar resultados GPU.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class CapacidadeVideo:
    janela_opengl: bool=False
    input_compatível: bool=False
    hud_compatível: bool=False
    pixels_todos_iguais: bool=False
    fps_comprovadamente_melhor: bool=False
    sem_readback: bool=True
    dispositivo_real_medido: bool=False
    perfil: str='sdl_surface'


def selecionar(caps=None, *, laboratorio=False):
    caps=CapacidadeVideo() if caps is None else caps
    razoes=[]
    if not caps.janela_opengl:razoes.append('janela_sdl_surface_sem_opengl')
    if not caps.input_compatível:razoes.append('eventos_de_entrada_sem_adapter')
    if not caps.hud_compatível:razoes.append('hud_sem_adapter')
    if not caps.pixels_todos_iguais:razoes.append('paridade_rgba_nao_comprovada')
    if not caps.fps_comprovadamente_melhor:razoes.append('ganho_fps_nao_comprovado')
    if not caps.sem_readback:razoes.append('readback_gpu_cpu')
    if not caps.dispositivo_real_medido:razoes.append('sem_medicao_android')
    if not laboratorio:razoes.append('ativacao_apenas_em_laboratorio')
    return {'schema':'pixelrush.qa.backend_gate.v327747',
            'backend':'gles_laboratorio' if not razoes else 'cpu_sdl_original',
            'pronto_para_trocar_entrada_real':False,
            'fallback_preservado':True,'aprovacao_necessaria':tuple(razoes),
            'camera_original_preservada':True,
            'fases_gpu_prontas_no_laboratorio':(
                'gles2_presenter','gles3_shader_exato','gles3_pbo_ring')}


def diagnostico_display():
    try:
        from pixelrush_qa_gles_gate_v327734 import diagnosticar
        from pixelrush_qa_gles_exact_v327736 import gate_integracao
        # Os metadados não criam GL e não modificam a tela.
        info=diagnosticar()
        g=selecionar()
        return {'janela':info,'arbitragem':g,
                'shader_gate_offline_sem_android':gate_integracao(
                    {'igualdade_total':True},medicao_android=False)}
    except (ImportError,RuntimeError,AttributeError) as exc:
        return {'arbitragem':selecionar(),'falha':type(exc).__name__}
