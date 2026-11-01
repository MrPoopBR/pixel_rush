# -*- coding: utf-8 -*-
"""Animações exclusivas PROD: sem texturas carregadas/frame, sem mexer na física."""
import math
import pygame

TITULOS_TUTORIAL = {
    'pt_BR': 'TUTORIAL CONCLUÍDO!', 'en_US': 'TUTORIAL COMPLETED!',
    'es_ES': '¡TUTORIAL COMPLETADO!', 'fr_FR': 'TUTORIEL TERMINÉ !',
    'de_DE': 'TUTORIAL ABGESCHLOSSEN!', 'it_IT': 'TUTORIAL COMPLETATO!',
    'tr_TR': 'EĞİTİM TAMAMLANDI!',
    'ja_JP': 'チュートリアル完了！', 'ko_KR': '튜토리얼 완료!',
    'zh_CN': '教程完成！', 'ru_RU': 'ОБУЧЕНИЕ ЗАВЕРШЕНО!',
    'hi_IN': 'ट्यूटोरियल पूरा!', 'ar_SA': 'اكتمل التدريب!',
    'pt_PT': 'TUTORIAL CONCLUÍDO!',
}
_FONTE_CACHE = {}

def _fonte(idioma, tamanho):
    chave = (idioma, tamanho)
    if chave not in _FONTE_CACHE:
        try:
            from pixelrush_fontes_prod_v32771 import fonte_unicode
            fonte = fonte_unicode(idioma, tamanho)
            # Idiomas latinos sem fonte Unicode dedicada retornam None.
            # A primeira corrida completa chega aqui e precisa de fonte real.
            _FONTE_CACHE[chave] = fonte or pygame.font.SysFont('arial', tamanho, bold=True)
        except (ImportError, ValueError, OSError, pygame.error):
            _FONTE_CACHE[chave] = pygame.font.SysFont('arial', tamanho, bold=True)
    return _FONTE_CACHE[chave]

def desenhar_mensagem_tutorial(tela, idioma, frame):
    w = tela.get_width()
    texto = TITULOS_TUTORIAL.get(idioma, TITULOS_TUTORIAL['en_US'])
    painel = pygame.Rect(18, 188, w-36, 70)
    pygame.draw.rect(tela, (11, 60, 49), painel, border_radius=13)
    pygame.draw.rect(tela, (116, 255, 178), painel, 3, border_radius=13)
    tam = 23
    while tam > 10 and _fonte(idioma,tam).size(texto)[0] > painel.width-24:
        tam -= 1
    surf = _fonte(idioma,tam).render(texto, True, (254, 244, 165))
    tela.blit(surf, surf.get_rect(center=painel.center))
    for i in range(14):
        a = frame * 0.05 + i * 2.39996
        x = int(w/2 + math.cos(a) * (120 + 12*math.sin(frame*.07+i)))
        y = int(221 + math.sin(a) * 62)
        pygame.draw.circle(tela, (250, 224, 101), (x, y), 1 + (i % 3))

def desenhar_fx_palavra(tela, frame, ate, fonte):
    w = tela.get_width()
    t = (frame % 180) / 180.0
    pulso = .5 + .5 * math.sin(frame * .19)
    cor = (255, int(185 + 65 * pulso), 102)
    cy = 174
    pygame.draw.circle(tela, cor, (w//2, cy), int(40 + 23 * pulso), 2)
    for i in range(20):
        a = i * 0.314159 + t*4.0
        d = 66 + 35 * ((frame+i*11)%70)/70.0
        pygame.draw.circle(tela, (255, 236, 145),
                           (int(w/2+math.cos(a)*d),int(cy+math.sin(a)*d*.64)),
                           1+(i%3))

@__import__('functools').lru_cache(maxsize=1)
def _fonte_entrada():
    return pygame.font.Font(None, 29)

def desenhar_entrada(tela, frame, final):
    rest = max(0, final-frame)
    if rest <= 0: return
    y = 125
    opacidade = max(0, min(255, int(rest*4)))
    pygame.draw.rect(tela, (20, 50, 65), (88, y, tela.get_width()-176, 42), border_radius=11)
    pygame.draw.rect(tela, (75, 216, 214), (88, y, tela.get_width()-176, 42), 2, border_radius=11)
    f = _fonte_entrada()
    tex = f.render('3  2  1  ...  GO!', True, (235, 249, 255))
    tela.blit(tex, tex.get_rect(center=(tela.get_width()//2,y+21)))

def desenhar_transicao(tela, bioma, progresso, frame):
    # Custo fixo: dezenas de primitivas Pygame, nenhum novo buffer grande.
    w, h = tela.get_size()
    meio = max(0., 1.0 - abs(progresso-.5)*2)
    if meio <= 0.01:return
    if bioma == 'cidade_futurista':
        cor = (84, 226, 246)
        for k in range(4):
            raio = int(85 + k*47 + 16*math.sin(frame*.10+k))
            pygame.draw.ellipse(tela, cor, (w//2-raio//2,h//2-raio,raio,raio*2), 2)
        for j in range(12):
            xx = (j*59+frame*8)%w
            pygame.draw.line(tela, (225, 126, 252), (xx,180),(xx,180+int(145*meio)),2)
    elif bioma == 'neve':
        for j in range(55):
            xx = int((j*83 + frame*3 + j*j) % w)
            yy = int((j*117 + frame*8) % h)
            pygame.draw.circle(tela, (235, 248, 255), (xx,yy), 1+(j%3))
    elif bioma == 'deserto':
        for j in range(44):
            xx = int((j*51 - frame*9)%w)
            yy = int((j*109 + frame*2)%h)
            pygame.draw.line(tela,(235,188,110),(xx,yy),(min(w,xx+17),yy-3),1+(j%2))
    else:  # Cidade: letreiros noturnos / faixas de trânsito e luzes urbanas.
        for j in range(14):
            xx = (j*71 + frame*6)%w
            yy = 230 + (j*83)%320
            pygame.draw.rect(tela, (247, 207, 105), (xx,yy,13,3),border_radius=1)
            pygame.draw.line(tela,(103,222,250),(xx+7,yy-15),(xx+7,yy+15),1)
