"""v3.176.0: polimento ARTÍSTICO das nove skins e acabamento das poses.

Não modifica esqueleto, colisões, ``Jogador.rect`` nem temporizadores.
Partindo do atlas já aprovado em 80x80, realça volumes por dentro da
silhueta: nunca desenha pernas/cabeças/patas extras, nunca usa blur.
A geração acontece uma única vez por skin/estado; o jogo usa o cache.
"""
from __future__ import annotations
from collections import OrderedDict
import pygame

# Intensidades por material; sombras suaves para não destruir arte aprovada.
_MATERIAIS = {
    'AZUL':    ((172, 235, 255), (23, 41, 72), .13),
    'VERDE':   ((209, 243, 133), (38, 100, 59), .11),
    'ROSA':    ((255, 232, 250), (151, 65, 121), .12),
    'DOURADO': ((255, 248, 158), (111, 64, 28), .17),
    'ROXO':    ((222, 163, 255), (48, 29, 99), .14),
    'ROBO':    ((210, 251, 255), (42, 82, 136), .18),
    'CHAMA':   ((255, 237, 133), (123, 44, 29), .14),
    'COSMICA': ((225, 232, 255), (62, 36, 122), .16),
    'PLATINA': ((232, 252, 255), (49, 88, 132), .19),
}
_STATES = ('OCIOSO','CORRER','IMPULSO','SUBINDO','PULAR','CAINDO',
           'AGACHAR','SWIPE_DOWN','POUSO','MORRER')


def _mix(a, b, v):
    return tuple(max(0,min(255, int(round(a[i]*(1-v)+b[i]*v)))) for i in range(3))


def _vis(surface, x, y, minimum=128):
    return (0 <= x < surface.get_width() and 0 <= y < surface.get_height()
            and surface.get_at((x,y)).a >= minimum)


def _pixel_se_pele(surface, x, y, color):
    # Só atualiza materiais que já fazem parte da silhueta.
    if _vis(surface,x,y,235):
        r,g,b,a=surface.get_at((x,y))
        c=_mix((r,g,b),color,.72)
        surface.set_at((x,y),(*c,a))


def refinar_quadro(original, skin, estado, fase):
    """Recolorização seletiva no INTERIOR da arte original; alfa 100% idêntico."""
    if estado not in _STATES or skin not in _MATERIAIS:
        return original.copy()
    luz, sombra, potencia = _MATERIAIS[skin]
    quadro=original.copy()
    w,h=quadro.get_size()
    # Raster final com micro-rim interno: sem novos pixels na silhueta.
    for y in range(2, h-2):
        for x in range(2,w-2):
            r,g,b,a=original.get_at((x,y))
            if a < 120:
                continue
            # Detecção de borda no alfa original, sem criar halos externos.
            t=original.get_at((x,y-1)).a < 128
            l=original.get_at((x-1,y)).a < 128
            d=original.get_at((x,y+1)).a < 128
            rgt=original.get_at((x+1,y)).a < 128
            color=(r,g,b)
            # Conserva a face intacta: região principal do personagem.
            if (t or l) and a > 225:
                power = potencia*(1.0 if t else .65)
                if y < 52:
                    power *= .50
                color=_mix(color,luz,power)
            elif (d or rgt) and a > 225:
                power=potencia*(.57 if y<52 else .72)
                color=_mix(color,sombra,power)
            # Volume corporal suave: materiais tornam-se distintos.
            elif 52 <= y <= 70 and 24 <= x <= 59 and a > 225:
                color=_mix(color, luz if x <= 37 else sombra, .044 if x<=37 else .035)
            if color != (r,g,b):
                quadro.set_at((x,y),(*color,a))

    # Detalhes minúsculos articulados com cada skin, NÃO membros extras.
    # As posições têm máscara estrita: pixels transparentes permanecem zero.
    cx=40
    if estado in ('AGACHAR', 'SWIPE_DOWN'):
        yy=60
    elif estado == 'POUSO':
        yy=57
    else:
        yy=56
    ident = {'AZUL':(238,110,135), 'VERDE':(214,246,151),
             'ROSA':(255,249,255), 'DOURADO':(255,250,176),
             'ROXO':(201,141,255), 'ROBO':(159,246,255),
             'CHAMA':(255,223,122), 'COSMICA':(229,206,255),
             'PLATINA':(200,242,255)}[skin]
    # Do peito à fivela, linhas interrompidas e brilho em material existente.
    _pixel_se_pele(quadro,cx-4,yy+3,ident)
    _pixel_se_pele(quadro,cx-3,yy+3,ident)
    _pixel_se_pele(quadro,cx+4,yy+5,ident)
    if estado in ('CORRER','IMPULSO','SUBINDO','CAINDO','POUSO'):
        # Reflexo no material da bota, acompanhando o quadro original.
        foot_y=72 if estado != 'POUSO' else 70
        for xx in (32+(fase%2),48-(fase%2)):
            _pixel_se_pele(quadro,xx,foot_y,ident)
    if skin in ('ROBO','PLATINA','DOURADO'):
        for x,y in ((28,52),(49,54),(35,64)):
            _pixel_se_pele(quadro,x,y,ident)
    return quadro


def refinar_atlas(atlas, skin):
    """Retorna atlas na mesma estrutura e com os mesmos quadros/silhuetas."""
    return {estado:tuple(refinar_quadro(frame,skin,estado,i)
                           for i,frame in enumerate(frames))
            for estado, frames in atlas.items()}


class MovimentoExpressivoPremium:
    """Acabamento sutil no movimento; não altera Sprite.rect nem ações."""
    _poses=OrderedDict()
    _limite_poses=144

    @classmethod
    def aplicar_pose(cls, jogador, frame):
        if jogador is None or getattr(jogador,'morrendo',False) or getattr(jogador,'jetpack_fase',None) is not None:
            return
        base=jogador.image
        if not getattr(jogador,'no_chao',True):
            estado='caindo' if getattr(jogador,'velocidade_y',0)>1.2 else 'subindo'
        elif getattr(jogador,'agachado',False):
            estado='agachado'
        elif getattr(jogador,'anim_pouso_ticks',0)>0:
            estado='pouso'
        else:
            estado='corrida'
        # Subtle volume changes, rather than creating new movement frames.
        fase=(int(frame)//3)%3
        chave=(id(base),estado,fase)
        entry=cls._poses.get(chave)
        sprite=entry[1] if entry and entry[0] is base else None
        if sprite is None:
            w,h=base.get_size()
            deltas = {'corrida':((0,0),(-1,0),(1,-1)),
                      'subindo':((-1,1),(-1,1),(-1,1)),
                      'caindo':((1,-1),(1,-1),(1,-1)),
                      'pouso':((2,-2),(2,-2),(2,-2)),
                      'agachado':((1,-1),(1,-1),(1,-1))}
            dw,dh=deltas[estado][fase]
            # 1px máximo de variação cíclica na corrida.
            temp=pygame.transform.scale(base,(max(1,w+dw),max(1,h+dh)))
            sprite=pygame.Surface((w,h),pygame.SRCALPHA)
            sprite.blit(temp,((w-temp.get_width())//2,h-temp.get_height()))
            cls._poses[chave]=(base,sprite)
            if len(cls._poses)>cls._limite_poses:
                cls._poses.popitem(last=False)
        else:
            cls._poses.move_to_end(chave)
        jogador.image=sprite

    @staticmethod
    def desenhar(surf, jogador, frame, cor=None):
        # A física e os quadros articulados já transmitem a ação;
        # preserva os efeitos cinemáticos aprovados da v3.172 sem duplicá-los.
        from pixelrush_cinema_v3172 import MovimentoExpressivo
        return MovimentoExpressivo.desenhar(surf,jogador,frame,cor)
