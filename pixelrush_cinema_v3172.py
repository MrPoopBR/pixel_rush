"""Pixel Rush v3.172.0 — direção artística, musical e justiça dos percursos.

Os desenhos são exclusivamente cosméticos. Geometria de colisões é lida, não
alterada; o gerador só injeta uma pausa quando dois comandos incompatíveis
sairiam consecutivamente. Não inclui rede ou dependências pagas.
"""
import math
from collections import OrderedDict
import pygame

PALETAS = {
    'cidade': ((95, 117, 162), (183, 198, 212), (245, 205, 130)),
    'neve': ((107, 142, 196), (229, 242, 252), (177, 217, 245)),
    'deserto': ((151, 100, 75), (236, 189, 120), (255, 220, 142)),
    'vulcao': ((75, 49, 65), (143, 90, 89), (255, 171, 73)),
    'floresta': ((44, 84, 66), (106, 165, 111), (188, 223, 160)),
    'cidade_futurista': ((44, 65, 117), (99, 201, 226), (231, 126, 248)),
    'ilhas_celestes': ((109, 152, 185), (209, 237, 239), (159, 250, 212)),
}


class DiretorMusical:
    """Mixagem gradativa dos quatro stems existentes, sem reiniciar playback."""
    def __init__(self):
        self.valores = [0., 0., 0., 0.]
        self.ritmo = 0.
        self.intensidade = 0.
        self.base_volume = 0.

    def atualizar(self, audio, estado, volume, velocidade, combo, perigo=False, bioma='cidade', recorde=False):
        ativo = estado == 'JOGANDO'
        velocidade = max(0., min(1., (float(velocidade) - 5.) / 17.))
        movimento = min(1., max(0., float(combo) / 24.))
        alvo = 0.0 if not ativo else min(1., .18 + velocidade * .42 + movimento * .22 + .20 * bool(perigo) + .15 * bool(recorde))
        self.intensidade += (alvo - self.intensidade) * .055
        brilho = .18 if bioma in ('cidade_futurista','ilhas_celestes') else 0.
        meditacao = .20 if bioma in ('floresta','neve','ilhas_celestes') else 0.
        objetivos = (
            volume * (.07 + .14 * self.intensidade),
            volume * (.04 + meditacao * .34 + .045 * (1. - self.intensidade)),
            volume * (.014 + .16 * self.intensidade + brilho * .08),
            volume * (.012 + .14 * self.intensidade * self.intensidade),
        ) if ativo else (0., 0., 0., 0.)
        canais = getattr(audio,'canais_stems',())
        for n, canal in enumerate(canais[:4]):
            self.valores[n] += (objetivos[n] - self.valores[n]) * .075
            canal.set_volume(max(0., min(.23, self.valores[n])))
        if getattr(audio,'canal_musica',None) is not None:
            if estado == 'JOGANDO':
                base_alvo = volume * (.68 + .24 * self.intensidade)
            elif estado == 'PAUSA':
                base_alvo = volume * .32
            else:
                base_alvo = volume * .62
            self.base_volume += (base_alvo - self.base_volume) * .065
            audio.canal_musica.set_volume(min(1.,max(0.,self.base_volume)))
        if getattr(audio, 'canal_ritmo', None):
            obj = min(.16, volume * (.014 + .12 * self.intensidade)) if ativo else 0.
            self.ritmo += (obj - self.ritmo) * .085
            audio.canal_ritmo.set_volume(self.ritmo)
        return tuple(round(v, 4) for v in self.valores)


class AuditorJustica:
    """Audita sequências reais do diretor e insere repouso em transições extremas."""
    ACOES = frozenset(('SALTO','ESCOLHA','PASSAGEM'))
    CHOQUES = frozenset((('PASSAGEM','SALTO'),('SALTO','PASSAGEM'),('ESCOLHA','PASSAGEM'),('PASSAGEM','ESCOLHA')))

    def __init__(self, diretor):
        self.diretor = diretor
        self.ultimo = None
        self.correcoes = 0
        self.verificacoes = 0
        self.eventos = []

    def proxima(self, metros, cenario='cidade'):
        sequencia = self.diretor.proxima(metros, cenario)
        self.verificacoes += 1
        if sequencia is not None and (self.ultimo, sequencia) in self.CHOQUES:
            self.correcoes += 1
            if len(self.eventos) < 40:
                self.eventos.append((str(cenario), int(metros), self.ultimo, sequencia))
            sequencia = 'DESCANSO'
        self.ultimo = sequencia
        return sequencia

    def reiniciar(self):
        self.diretor.reiniciar()
        self.ultimo = None
        self.correcoes = 0
        self.verificacoes = 0
        self.eventos.clear()

    @staticmethod
    def analisar_geometria(jogador_rect, rects, margem=12):
        """Relata obstáculos com folga de reação, sem mover hitboxes."""
        p = pygame.Rect(jogador_rect)
        itens = sorted((pygame.Rect(r) for r in rects), key=lambda r: r.left)
        erros=[]
        for a,b in zip(itens, itens[1:]):
            if b.left - a.right < margem:
                erros.append({'tipo':'intervalo_curto','separacao_px':b.left-a.right})
        for r in itens:
            if r.w<=0 or r.h<=0:
                erros.append({'tipo':'hitbox_invalida','rect':tuple(r)})
        return erros


class EsquivaPerfeita:
    LIMIAR_PERFEITO = 9

    @classmethod
    def observar(cls, obstaculo, distancia_quadrada):
        d2=max(0.,float(distancia_quadrada))
        if d2 <= 18*18:
            obstaculo._perfeita_min_d2 = min(getattr(obstaculo,'_perfeita_min_d2',float('inf')), d2)
        return getattr(obstaculo,'_perfeita_min_d2',float('inf'))

    @classmethod
    def concluiu(cls, obstaculo):
        d2=getattr(obstaculo,'_perfeita_min_d2',float('inf'))
        return not getattr(obstaculo,'_perfeita_colidiu',False) and d2 <= cls.LIMIAR_PERFEITO**2


class MovimentoExpressivo:
    """Poses expressivas e ecos de movimento sem alterar Sprite.rect/hitbox."""
    _poses = OrderedDict()
    _limite_poses = 128

    @classmethod
    def aplicar_pose(cls, jogador, frame):
        if jogador is None or getattr(jogador,'morrendo',False) or getattr(jogador,'jetpack_fase',None) is not None:
            return
        base = jogador.image
        if not getattr(jogador,'no_chao',True):
            estado = 'descendo' if getattr(jogador,'velocidade_y',0)>1.2 else 'subindo'
        elif getattr(jogador,'agachado',False):
            estado = 'agachado'
        elif getattr(jogador,'anim_pouso_ticks',0)>0:
            estado = 'pouso'
        else:
            estado = 'corrida'
        fase=(frame//3)%2
        chave=(id(base),estado,fase)
        entrada=cls._poses.get(chave)
        pronta=entrada[1] if entrada is not None and entrada[0] is base else None
        if pronta is None:
            w,h=base.get_size()
            ajustes = {
                'subindo':(-2,3), 'descendo':(2,-2), 'pouso':(3,-3),
                'corrida':((2 if fase else -1),(0 if fase else 1)),
                'agachado':(1,-1),
            }
            aw,ah=ajustes[estado]
            temp=pygame.transform.scale(base,(max(1,w+aw),max(1,h+ah)))
            pronta=pygame.Surface((w,h),pygame.SRCALPHA)
            # Centro e apoio nos pés permanecem estáveis.
            pronta.blit(temp, ((w-temp.get_width())//2,h-temp.get_height()))
            cls._poses[chave]=(base,pronta)
            if len(cls._poses)>cls._limite_poses:
                cls._poses.popitem(last=False)
        else:
            cls._poses.move_to_end(chave)
        jogador.image=pronta

    @staticmethod
    def desenhar(surf, jogador, frame, cor=None):
        if jogador is None or getattr(jogador,'morrendo',False):
            return
        r=jogador.rect
        cor=tuple(cor[:3]) if cor else (169,229,252)
        t=frame*.24
        if getattr(jogador,'no_chao',False) and not getattr(jogador,'agachado',False):
            # Movimento horizontal sugerido por poucos traços que não tocam a pista.
            for i in range(3):
                yy=r.bottom-24-i*9+int(math.sin(t+i)*2)
                pygame.draw.line(surf,cor,(max(1,r.left-12-i*6),yy),(max(1,r.left-5-i*5),yy),1)
        elif not getattr(jogador,'no_chao',True):
            cx=r.centerx; cy=r.centery
            desc=getattr(jogador,'velocidade_y',0) > 1.5
            if desc:
                for i in range(3):
                    pygame.draw.line(surf,cor,(cx-10-i*8,cy-12),(cx-10-i*8,cy-20-i*4),1)
            else:
                for i in range(3):
                    pygame.draw.line(surf,cor,(cx-12-i*7,cy+9),(cx-12-i*7,cy+14+i*4),1)
            pygame.draw.arc(surf,cor,(r.x-3,r.y+10,r.w+6,r.h-8),math.pi*.13,math.pi*.37,1)
        if getattr(jogador,'anim_pouso_ticks',0) > 0 and getattr(jogador,'no_chao',False):
            t0=min(10, getattr(jogador,'anim_pouso_ticks',0))
            w=18+(10-t0)*4
            pygame.draw.arc(surf,cor,(r.centerx-w,r.bottom-9,w*2,9),0,math.pi,1)


class CameraCinematica:
    """Zoom e enquadramento suave apenas visual; nenhum deslocamento de hitboxes."""
    def __init__(self):
        self.zoom=0.
        self.foco_y=0.
        self._cache_size=(450,800)
        # Mesmos pixels e interpolação; a Surface expandida só muda se o tamanho variar.
        self._cache_zoom_tamanho = None
        self._cache_zoom_expandido = None

    def aplicar(self, imagem, jogador=None, velocidade=6, momento=False, ativo=True):
        if not ativo or jogador is None:
            self.zoom *= .9
            return imagem
        alvo_zoom=.034 if momento else min(.025, max(0., (velocidade-8.)*.0018))
        self.zoom += (alvo_zoom-self.zoom)*.045
        p_y=0. if getattr(jogador,'no_chao',True) else max(-10.,min(10.,(jogador.rect.centery-600)*.06))
        self.foco_y += (p_y-self.foco_y)*.065
        if self.zoom<.002:
            return imagem
        w,h=imagem.get_size()
        extra_x=max(1,int(w*self.zoom)); extra_y=max(1,int(h*self.zoom))
        tamanho=(w+extra_x*2,h+extra_y*2)
        if self._cache_zoom_tamanho != tamanho or self._cache_zoom_expandido is None:
            self._cache_zoom_expandido = pygame.Surface(tamanho).convert(imagem)
            self._cache_zoom_tamanho = tamanho
        expanded=pygame.transform.smoothscale(imagem,tamanho,self._cache_zoom_expandido)
        sx=extra_x; sy=max(0,min(2*extra_y,extra_y+int(self.foco_y)))
        return expanded.subsurface((sx,sy,w,h))


class CenasCinematograficas:
    """Marcos monumentais ancorados na distância do mundo; arte cacheada."""
    def __init__(self):
        self._assets={}
        self.ultimo_bioma=None

    @staticmethod
    def momento(travel):
        pos=float(travel)%6400.
        return 580 <= pos <= 3400

    def desenhar(self,surf,bioma,travel,frame=0,night=0):
        if bioma not in PALETAS or not self.momento(travel):
            return False
        if bioma not in self._assets:
            self._assets[bioma]=self._criar(bioma)
        pos=float(travel)%6400.
        x=int(402-(pos-850)*.25)
        image=self._assets[bioma]
        y=245 if bioma in ('cidade','cidade_futurista') else (225 if bioma=='ilhas_celestes' else 275)
        if x < -image.get_width() or x>=450:
            return False
        surf.blit(image,(x,y))
        accent=PALETAS[bioma][2]
        if bioma in ('cidade_futurista','vulcao','ilhas_celestes'):
            for k in range(4):
                px=x+44+k*42
                py=y+36+int(math.sin(frame*.09+k)*3)
                if 0<=px<450:
                    pygame.draw.line(surf,accent,(px,py),(px+5,py),1)
        return True

    def _criar(self,bioma):
        w,h=350,210
        s=pygame.Surface((w,h),pygame.SRCALPHA)
        dark,mid,accent=PALETAS[bioma]
        # Silhueta dominante, profundamente integrada aos estratos do cenário.
        if bioma=='cidade':
            for i,(x,hh) in enumerate(((7,94),(49,126),(111,102),(211,144),(269,107),(317,92))):
                pygame.draw.rect(s,dark,(x,h-hh,25+(i%3)*8,hh))
                for yy in range(h-hh+10,h-12,12):
                    pygame.draw.line(s,accent,(x+6,yy),(x+14,yy),1)
            pygame.draw.arc(s,mid,(43,39,260,120),math.pi,2*math.pi,8)
            pygame.draw.line(s,accent,(58,101),(291,101),3)
        elif bioma=='cidade_futurista':
            for x,hh,ww in ((14,125,40),(69,178,46),(140,156,56),(223,198,48),(293,139,40)):
                pygame.draw.rect(s,dark,(x,h-hh,ww,hh))
                pygame.draw.rect(s,mid,(x+5,h-hh+6,ww-10,hh-13),2)
                for yy in range(h-hh+15,h-6,18):
                    pygame.draw.line(s,accent,(x+10,yy),(x+ww-10,yy),1)
            pygame.draw.arc(s,mid,(27,32,292,152),math.pi,2*math.pi,7)
            pygame.draw.line(s,accent,(41,116),(311,116),3)
        elif bioma=='neve':
            pygame.draw.polygon(s,dark,[(0,h),(43,98),(85,143),(153,45),(206,112),(269,72),(347,h)])
            pygame.draw.polygon(s,mid,[(75,126),(153,45),(211,116),(174,91),(150,79),(123,117)])
            pygame.draw.line(s,accent,(148,49),(161,67),3)
            for x,y in ((70,152),(246,135),(285,166)):
                pygame.draw.polygon(s,mid,[(x-12,h),(x-6,y),(x+7,y-6),(x+15,h)])
                pygame.draw.line(s,accent,(x-7,y+2),(x+8,y-2),2)
        elif bioma=='deserto':
            pygame.draw.polygon(s,dark,[(0,h),(20,132),(53,126),(87,151),(118,90),(174,88),(189,159),(248,120),(286,121),(309,h)])
            pygame.draw.rect(s,mid,(105,86,82,12))
            pygame.draw.rect(s,dark,(136,35,19,50))
            pygame.draw.polygon(s,mid,[(105,75),(145,33),(187,75)])
            for x in (21,258):
                pygame.draw.rect(s,mid,(x,125,24,h-125))
                pygame.draw.line(s,accent,(x,127),(x+24,127),3)
        elif bioma=='vulcao':
            pygame.draw.polygon(s,dark,[(0,h),(46,154),(96,113),(120,126),(154,23),(184,45),(202,91),(274,123),(350,h)])
            pygame.draw.polygon(s,mid,[(93,h),(153,27),(182,50),(215,h)])
            pygame.draw.polygon(s,(40,33,45),[(142,36),(151,20),(166,19),(181,39),(160,47)])
            pygame.draw.lines(s,accent,False,[(162,46),(169,70),(166,107),(180,140),(179,h-15)],7)
            pygame.draw.lines(s,(255,224,138),False,[(166,68),(163,92),(174,139)],2)
            for k in range(8):
                x=142+int(math.sin(k*.75)*12); yy=15+k*7
                pygame.draw.circle(s,(*mid,110),(x,yy),12+k,0)
        elif bioma=='floresta':
            pygame.draw.polygon(s,dark,[(0,h),(33,121),(71,143),(111,76),(159,103),(194,35),(233,92),(273,57),(350,h)])
            pygame.draw.polygon(s,mid,[(149,h),(194,38),(229,h)])
            for xx in (185,195,206):
                pygame.draw.line(s,(128,208,223),(xx,75),(xx-9,h-10),4)
            pygame.draw.line(s,accent,(186,87),(196,h-12),2)
            for xx in (51,270):
                pygame.draw.rect(s,dark,(xx,h-98,14,98))
                pygame.draw.circle(s,mid,(xx+6,h-103),34)
        elif bioma=='ilhas_celestes':
            for x,y,ww in ((10,96,114),(163,31,156),(254,113,96)):
                pygame.draw.polygon(s,dark,[(x,y+22),(x+10,y),(x+ww-12,y-4),(x+ww,y+23),(x+ww//2,y+75)])
                pygame.draw.line(s,mid,(x+9,y+3),(x+ww-9,y+1),5)
                pygame.draw.line(s,accent,(x+ww//2,y+44),(x+ww//2-4,y+95),2)
            pygame.draw.rect(s,mid,(231,24,18,26))
            pygame.draw.polygon(s,accent,[(217,26),(240,2),(263,26)])
        # O monumento deve pertencer ao horizonte: perde opacidade gradualmente
        # nas bordas laterais e na base (sem linhas retas ou peças voando).
        alpha=pygame.surfarray.pixels_alpha(s)
        for x in range(w):
            lateral=min(1., (x+1)/38., (w-x)/38.)
            for y in range(h):
                inferior=min(1., max(0., (h-y-1)/74.))
                intensidade=.86 * lateral * inferior
                if alpha[x,y]:
                    alpha[x,y]=int(alpha[x,y]*intensidade)
        del alpha
        return s
