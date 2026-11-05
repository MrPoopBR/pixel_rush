"""Fluxo visual integrado à janela do Pixel Rush (v3.270.0).

A apresentação não inicializa nem encerra o Pygame, não altera RNG/física,
não manipula saves, moedas ou player. O chamador controla persistência.
"""
from __future__ import annotations
import os
import pygame
from prototipo_tutorial_v3270 import Estado, desenhar, W, H


def precisa_tutorial(dados):
    # Saves antigos com corridas concluídas não devem perder progresso nem
    # precisar refazer o tutorial por causa da migração da versão.
    return (not dados.get('tutorial_inicial_concluido', False)
            and int(dados.get('estatisticas_permanentes', {}).get('partidas', 0)) == 0)


def qa_sem_abertura():
    # QA de replay já existente não deve ter seu fluxo de eventos alterado.
    return (os.environ.get('PIXELRUSH_QA_SKIP_TUTORIAL') == '1'
            or os.environ.get('PIXELRUSH_REPRO') in ('record', 'replay'))


def _acao_do_clique(etapa, x, y, primeiro):
    if etapa == 'abertura' and pygame.Rect(16, 638, 418, 54).collidepoint(x,y):
        return 'pular_abertura'
    if pygame.Rect(16,717,418,65).collidepoint(x,y):
        return {'abertura':'iniciar','pulo':'pular','agachar':'agachar','fim':'concluir'}[etapa]
    return None


def _coordenada_virtual(pos, tamanho):
    larg, alt = tamanho
    escala = min(larg / W, alt / H)
    if escala <= 0: return (-999,-999)
    return (int((pos[0] - (larg-W*escala)/2)/escala),
            int((pos[1] - (alt-H*escala)/2)/escala))


def executar_apresentacao(primeiro, *, eventos_simulados=None, limite_qa=0):
    """Retorna 'concluido' ou 'cancelado'; não salva dados por conta própria.

    eventos_simulados é permitido apenas em testes internos, não é usado no jogo.
    """
    est=Estado()
    fonte={
       'tiny':pygame.font.SysFont('arial',14,bold=True),
       'small':pygame.font.SysFont('arial',15),
       'body':pygame.font.SysFont('arial',18),
       'head':pygame.font.SysFont('arial',26,bold=True),
       'button':pygame.font.SysFont('arial',23,bold=True),
    }
    palco=pygame.Surface((W,H)).convert()
    relogio=pygame.time.Clock()
    imagens={}; tick=0
    while True:
        eventos=pygame.event.get()
        if eventos_simulados:
            eventos+=eventos_simulados.get(tick, [])
        for evento in eventos:
            if evento.type == pygame.QUIT:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return 'cancelado'
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_ESCAPE, getattr(pygame,'K_AC_BACK',pygame.K_ESCAPE)):
                    return 'cancelado'
                if est.etapa == 'abertura' and evento.key == pygame.K_p:
                    acao='pular_abertura'
                elif evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_UP):
                    acao={'abertura':'iniciar','pulo':'pular','agachar':None,'fim':'concluir'}[est.etapa]
                elif evento.key in (pygame.K_DOWN,pygame.K_s) and est.etapa=='agachar':
                    acao='agachar'
                else: acao=None
            elif evento.type in (pygame.MOUSEBUTTONDOWN,pygame.FINGERDOWN):
                tela=pygame.display.get_surface()
                if evento.type == pygame.FINGERDOWN:
                    pos=(evento.x*tela.get_width(),evento.y*tela.get_height())
                else:pos=evento.pos
                acao=_acao_do_clique(est.etapa,*_coordenada_virtual(pos,tela.get_size()),primeiro)
            else: continue
            if acao=='concluir':
                return 'concluido'
            if not acao: continue
            if est.etapa == 'abertura' and not primeiro:
                return 'concluido'
            est.acao(acao)
        est.progredir()
        desenhar(palco,est,fonte)
        tela=pygame.display.get_surface()
        if tela is None:return 'cancelado'
        w,h=tela.get_size(); esc=min(w/W,h/H)
        tw,th=max(1,int(W*esc)),max(1,int(H*esc))
        tela.fill((5,10,20))
        if (tw,th)==(W,H): tela.blit(palco,((w-tw)//2,(h-th)//2))
        else: tela.blit(pygame.transform.scale(palco,(tw,th)),((w-tw)//2,(h-th)//2))
        pygame.display.flip()
        tick+=1
        if limite_qa and tick >= limite_qa:return 'cancelado'
        relogio.tick(0 if os.environ.get('SDL_VIDEODRIVER')=='dummy' else 60)
