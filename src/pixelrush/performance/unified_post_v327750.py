# -*- coding: utf-8 -*-
"""v3.277.50-QA: contratacao unica dos passes de pos-camera e apresentacao.

Esta funcao e chamada pelo loop REAL (depois do gamefeel e do GPU processor).
Nao omite nenhum efeito, nao altera zoom, camera, ordem de pixels, nem flags.
Pode combinar a rota de camera CPU ou a ponte GLES experimental ja existente,
sem modificar o contrato do HUD, entrada ou estado fisico.
Otimiza somente o blit final em caso de origem == framebuffer de destino;
todo o restante replica a ordem e o tipo exato de draw/scale legado.
"""
import os
import pygame

_STATUS={'quadros':0,'camera':0,'camera_ignorada':0,'escala':0,
         'sem_escala':0,'blits_finais':0,'blits_redundantes_pulados':0,
         'fallbacks':0,'modo':'qa_cpu_igual'}
_HABILITADO=os.environ.get('PIXELRUSH_QA_POST_PIPELINE','1')=='1'


def habilitado():
    return _HABILITADO and os.environ.get('PIXELRUSH_QA_POST_PIPELINE','1')=='1'


def diagnostico():
    return dict(_STATUS,habilitado=habilitado(),
                preserva_hud=True,preserva_zoom_cpu=True,
                fps_android_comprovado=False,pixels_rgba_homologados=False)


def finalizar_quadro(imagem, tela, tamanho_final, pos_final, superficies_escala,
                    camera, jogador, velocidade, momento, usar_camera,
                    inicio_sub, fim_sub, marcar):
    """Equivalente a ordem original, com o mesmo cache de superficies do jogo.

    inicio_sub, fim_sub e marcar sao as funcoes do profiler REAL do loop.
    Em excecao, nao captura silenciosamente erro de SDL: a integridade de
    frame nao deve ser escondida, e o caminho legado permanece selecionavel.
    """
    if not habilitado():
        _STATUS['fallbacks']+=1
    if usar_camera:
        inicio_sub('camera_smoothscale')
        try:
            imagem=camera.aplicar(imagem,jogador,velocidade,momento,True)
            _STATUS['camera']+=1
        finally:
            fim_sub()
    else:
        _STATUS['camera_ignorada']+=1
    marcar('apresentacao')
    if tamanho_final==imagem.get_size():
        superficie_final=imagem
        _STATUS['sem_escala']+=1
    else:
        inicio_sub('apresentacao_escala_final')
        try:
            superficie_final=superficies_escala.get(tamanho_final)
            if superficie_final is None:
                try:
                    superficie_final=pygame.Surface(tamanho_final).convert()
                except Exception:
                    superficie_final=pygame.Surface(tamanho_final)
                superficies_escala[tamanho_final]=superficie_final
                if len(superficies_escala)>3:
                    superficies_escala.popitem(last=False)
            else:
                superficies_escala.move_to_end(tamanho_final)
            pygame.transform.scale(imagem,tamanho_final,superficie_final)
            _STATUS['escala']+=1
        finally:
            fim_sub()
    inicio_sub('apresentacao_blit_final')
    try:
        # Mesmo objeto Surface, mesma dimensao e (0,0): blit sobre si mesma
        # era trabalho redundante. Nunca supor igualdade a partir de pixels.
        if (superficie_final is tela and pos_final==(0,0) and
                superficie_final.get_size()==tela.get_size() and
                not (tela.get_flags() & pygame.SRCALPHA) and
                tela.get_colorkey() is None and
                tela.get_alpha() in (None,255)):
            _STATUS['blits_redundantes_pulados']+=1
        else:
            tela.blit(superficie_final,pos_final)
            _STATUS['blits_finais']+=1
    finally:
        fim_sub()
    inicio_sub('apresentacao_swap')
    try:
        pygame.display.flip()
    finally:
        fim_sub()
    _STATUS['quadros']+=1


def restaurar_estatisticas_para_teste():
    _STATUS.update(quadros=0,camera=0,camera_ignorada=0,escala=0,
                   sem_escala=0,blits_finais=0,blits_redundantes_pulados=0,
                   fallbacks=0,modo='qa_cpu_igual')
