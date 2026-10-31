"""Pixel Rush v3.123.0: atividades decorativas da Cidade (sem hitboxes).

Diretor deterministico e economicamente limitado: as entidades decorativas
sao calculadas por deslocamento/fase, nao precisam de lista infinita de spawn.
Nenhum objeto pode bloquear a pista ou alterar a fisica do jogador.
"""
from __future__ import annotations
import math
import pygame

class CityLifeDirector:
    """Atividades nas vias secundarias, iluminacao, vento e atmosfera."""
    MAX_PEDESTRIANS = 2
    MAX_VEHICLES = 2
    MAX_BIRDS = 3
    MAX_PARTICLES = 12

    def __init__(self):
        self.frame = -1
        self.wind = 0.0
        self.spring_x = 0.0
        self.spring_v = 0.0
        self.wake = 0.0
        self._last_travel = 0.0
        self._halo = self._create_halo()
        self._headlamp = self._create_headlamp()
        self._car = (self._make_car((83, 178, 218)), self._make_car((232, 124, 124)))
        self._walker = (self._make_walker((241, 173, 137)), self._make_walker((111, 168, 196)))
        self._bike = self._make_bike()
        self._particle_rect = pygame.Rect(0, 0, 2, 2)
        # Corda de seis nos por integracao de Verlet, com extremos fixos.
        self._rope = [[i*10.8, (5-abs(2.5-i))*1.5] for i in range(6)]
        self._rope_prev = [[x, y] for x, y in self._rope]
        self._rope_length = 11.2

    @staticmethod
    def _create_halo():
        glow = pygame.Surface((78, 78), pygame.SRCALPHA)
        for radius, alpha in ((35, 5), (27, 9), (19, 16), (11, 24), (5, 42)):
            pygame.draw.circle(glow, (255, 202, 121, alpha), (39, 39), radius)
        return glow

    @staticmethod
    def _create_headlamp():
        glow = pygame.Surface((32, 14), pygame.SRCALPHA)
        for i in range(12):
            pygame.draw.line(glow, (249, 212, 130, int(65*(1.0-i/12))), (i+1, 5), (i+1, 9), 1)
        return glow

    @staticmethod
    def _make_car(color):
        s = pygame.Surface((27, 13), pygame.SRCALPHA)
        dark = (46, 57, 78)
        pygame.draw.rect(s, dark, (1, 6, 24, 5), border_radius=2)
        pygame.draw.rect(s, color, (2, 5, 22, 5), border_radius=2)
        pygame.draw.polygon(s, color, ((6,5), (10,1), (19,1), (23,5)))
        pygame.draw.rect(s, (171, 217, 236), (10, 2, 8, 3))
        pygame.draw.rect(s, (254, 229, 148), (23, 6, 2, 2))
        pygame.draw.circle(s, (45, 49, 66), (7, 11), 2)
        pygame.draw.circle(s, (45, 49, 66), (20, 11), 2)
        return s

    @staticmethod
    def _make_walker(color):
        frames = []
        for phase in (0, 1):
            s = pygame.Surface((8, 19), pygame.SRCALPHA)
            ink = (44, 50, 70)
            pygame.draw.circle(s, (243, 198, 162), (4, 3), 3)
            pygame.draw.rect(s, color, (2, 7, 5, 7))
            pygame.draw.line(s, ink, (3, 14), (2 if phase else 4, 18), 1)
            pygame.draw.line(s, ink, (5, 14), (6 if phase else 3, 18), 1)
            pygame.draw.line(s, (233, 199, 156), (2, 8), (0, 12), 1)
            pygame.draw.line(s, (233, 199, 156), (6, 8), (7, 11), 1)
            frames.append(s)
        return tuple(frames)

    @staticmethod
    def _make_bike():
        s = pygame.Surface((19, 16), pygame.SRCALPHA)
        for x in (4, 15):
            pygame.draw.circle(s, (57, 62, 80), (x, 12), 3, 1)
        pygame.draw.lines(s, (120, 171, 177), False, ((4,12),(10,6),(15,12),(8,12),(4,12)), 1)
        pygame.draw.circle(s, (238, 191, 148), (10, 3), 2)
        pygame.draw.line(s, (83, 91, 110), (10, 5), (10, 9), 2)
        return s

    def tick(self, frame, travel, climate='limpo'):
        if frame == self.frame:
            return
        previous = self.frame
        self.frame = frame
        self._last_travel = travel
        storm = climate in ('tempestade','vento','vento_folhas','vento_neon','tempestade_vento')
        # passo discreto com amortecimento, custo constante
        gust = (math.sin(frame*.033) + .30*math.sin(frame*.091)) * (1.6 if storm else .55)
        self.wind = gust
        drive = gust*.05 + (self.wake*.014)
        self.spring_v = (self.spring_v + drive - self.spring_x*.10)*.87
        self.spring_x = max(-5.0, min(5.0, self.spring_x + self.spring_v))
        self.wake *= .94
        # Integrador de Verlet real: posicao atual/anterior; restricoes rigidas.
        # Apenas seis nos prealocados e quatro iteracoes por update.
        for i in range(1,5):
            node=self._rope[i]; prev=self._rope_prev[i]
            old_x,old_y=node[0],node[1]
            node[0] += (node[0]-prev[0])*.88 + gust*.052 + self.wake*.026
            node[1] += (node[1]-prev[1])*.88 + .16
            prev[0],prev[1]=old_x,old_y
        for _ in range(4):
            self._rope[0][0]=0.;self._rope[0][1]=0.
            self._rope[-1][0]=54.;self._rope[-1][1]=0.
            for j in range(5):
                a=self._rope[j];b=self._rope[j+1]
                dx=b[0]-a[0];dy=b[1]-a[1]
                span=max(.0001, math.hypot(dx,dy))
                err=(span-self._rope_length)/span
                if j>0:
                    a[0]+=dx*err*.50;a[1]+=dy*err*.50
                if j+1<5:
                    b[0]-=dx*err*.50;b[1]-=dy*err*.50
        self._rope[0][0]=0.;self._rope[0][1]=0.
        self._rope[-1][0]=54.;self._rope[-1][1]=0.
        # sem interpolacao dependente de FPS para entidades do cenário (apenas visual)
        if previous >= 0 and frame < previous:
            self.spring_x = self.spring_v = 0.

    def react_to_player(self, intensity=1.):
        self.wake = min(6.0, self.wake + float(intensity)*2.0)

    @staticmethod
    def _safe_blit(target, sprite, x, y):
        if -sprite.get_width() < x < target.get_width() and -sprite.get_height() < y < target.get_height():
            target.blit(sprite, (int(x), int(y)))

    def draw_bridge_life(self, target, travel, night, frame, quality=1):
        """Sempre atras do skyline proximo, acima da ponte fisica (y=133)."""
        # O trem original ja existe. Dois carros adicionais no maximo.
        # Ponte superior em y~133 (ampliada x2) — rodas apoiadas em y=264.
        for i in range(self.MAX_VEHICLES if quality else 1):
            world_pos = (i*273 + frame*(.60+i*.18) - travel*.10)
            x = int(world_pos % (target.get_width()+110))-52
            y = 133*2-13
            tex = self._car[i]
            self._safe_blit(target, tex, x, y)
            if night>.40:
                self._safe_blit(target, self._headlamp, x+17, y+2)
        # Personagens de fundo, bem menores e nao sobrepostos ao jogador.
        for i in range(self.MAX_PEDESTRIANS if quality else 1):
            x = int((i*235 + frame*(.27+i*.07)-travel*.14)%(target.get_width()+110))-52
            y = 171*2-19  # segunda ponte/viaduto
            frames=self._walker[i]
            self._safe_blit(target, frames[(frame//13+i)%2], x, y)
        # micro-narrativa: ciclista atravessa o viaduto esporadicamente
        if quality and (int(travel//600)%4)==2:
            x=int((frame*.91-travel*.18)% (target.get_width()+100))-45
            self._safe_blit(target,self._bike,x,171*2-16)

    def draw_suspended_cables(self, target, travel, frame, quality=1):
        """Cabos dinamicos entre postes do viaduto: resposta de mola amortecida."""
        if not quality:
            return
        # Cabos aparecem ENTRE pilastras; os extremos estao na mesma cota.
        period = 108
        shift = int(travel*.28) % period
        for cell in range(-1, 6):
            x0 = cell*period-shift
            x1 = x0+54
            if x1<-5 or x0>target.get_width()+5:
                continue
            y=135*2+4
            # Mesma malha de Verlet reciclada por trecho (6 nos fisicos).
            points = [(int(x0+p[0]),int(y+p[1])) for p in self._rope]
            pygame.draw.lines(target,(64,78,110),False,points,2)
            pygame.draw.lines(target,(119,132,160),False,points,1)

    def draw_windows_lights(self,target,near_tiles,night,frame,quality=1,map_kind='image'):
        """Pontos de luz ancorados nas fachadas, restritos a noite e orcamento."""
        if night<.20:return
        for x,variant,flip in near_tiles:
            # lanternas fixas da fachada nas posicoes do modulo 3122
            for cx in (154,336):
                sx=int(x+cx*2+12)
                sy=375
                if sx<-50 or sx>target.get_width()+50:continue
                flicker=1.0 if (frame//19+cx)%23 else .70
                if map_kind=='image':
                    # superficie pequena pregerada, nenhuma alocacao dinamica
                    if flicker==1.0:
                        target.blit(self._halo,(sx-39,sy-39))
                    else:
                        # nao usa cópia / set_alpha por frame
                        pygame.draw.circle(target,(255,210,130),(sx,sy),2)
                elif map_kind=='fxmask':
                    pygame.draw.circle(target,(255,225,155,int(110*night)),(sx,sy),4)
            if not quality:
                continue
            # poucos pontos iluminados por modulo — sem ficarem boiando
            for seed,wx in enumerate((55,235,385)):
                sx=int(x+wx*2)
                sy=411 if seed%2==0 else 389
                if not(2<=sx<target.get_width()-2):continue
                if (frame//43+seed*7+int(self._last_travel//900))%7==0:
                    continue
                if map_kind=='image':
                    color=(255,224,151)
                    pygame.draw.rect(target,color,(sx,sy,5,3))
                elif map_kind=='fxmask':
                    pygame.draw.rect(target,(255,206,124,int(55+70*night)),(sx,sy,5,3))

    def draw_atmosphere(self, target, travel, frame, night, climate, quality=1):
        """Poeira, vapor e folhas em pooling analitico, sem objetos descartados."""
        if not quality:
            count=4
        else:
            count=self.MAX_PARTICLES
        rainy=climate in ('chuva','tempestade')
        wind=self.wind
        for i in range(count):
            # Usa dispersao deterministica e ciclo finito: repeticao sem alocar.
            p=(frame*(.42+(i%3)*.08)+i*41.0)
            x=int((i*67.0+p*.42+travel*.07+wind*3)%(target.get_width()+20))-10
            y=int(352 + ((i*37.0-p*.53)%102))
            if rainy:
                col=(153,201,227)
                pygame.draw.line(target,col,(x,y),(x-2,y+6),1)
            elif i%4==0:
                # vapor de bueiro, junto ao chao e sem encobrir a pista
                if y>427:
                    pygame.draw.circle(target,(146,151,157),(x,y),2)
            elif i%3==0:
                pygame.draw.rect(target,(143,179,119),(x,y,2,1))
            else:
                pygame.draw.rect(target,(171,169,152),(x,y,1,1))

    def draw_pigeons(self, target, travel, frame, quality=1):
        if not quality:return
        # Grupo sobre a faixa superior do viaduto; decola pela aproximação.
        epoch=int(travel//1100)
        if epoch%3!=1:return
        y0=133*2-3
        for i in range(self.MAX_BIRDS):
            sx=int((i*16+270-travel*.12)% (target.get_width()+40))-20
            proximity=abs(sx-120)
            flight=max(0.,(100.-proximity)/100.)
            sy=int(y0 - flight*(18+i*9) - math.sin(frame*.12+i)*2)
            pygame.draw.line(target,(70,65,84),(sx,sy),(sx+3,sy-2),1)
            pygame.draw.line(target,(70,65,84),(sx+3,sy-2),(sx+6,sy),1)

    def draw_wet_reflections(self,target,travel,frame,night,climate):
        """Pequenos reflexos de agua sob os edificios, sem espelho de tela inteira."""
        if climate not in ('chuva','tempestade'):
            return
        y0=480
        for i in range(8):
            x=int((i*71-travel*.63)% (target.get_width()+30))-15
            w=5+(i%3)*3
            col=(151,172,185) if night<.4 else (214,171,133)
            pygame.draw.line(target,col,(x,y0+i%3*4),(x+w,y0+i%3*4),1)
            if night>.25 and i%2==0:
                pygame.draw.line(target,(218,191,144),(x+2,y0+8),(x+w-1,y0+8),1)
