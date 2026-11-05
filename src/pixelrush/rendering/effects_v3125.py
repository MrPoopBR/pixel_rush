"""Pixel Rush 3.103 — materiais 2D, cabos Verlet e atmosfera contextual.

Pygame obrigatório; NumPy é aceleração OPCIONAL do relighting CPU. Sem GPU
não há PBR físico completo, raymarching nem SSR: evitar nomenclatura enganosa.
"""
import math
import random
from collections import OrderedDict
import pygame

try:
    import numpy as np
except ImportError:
    np = None


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] * (1-t) + b[i] * t) for i in range(3))


class SurfaceMaterial:
    """Normal-map estimado por luminância, luz direcional difusa e brilho especular.

    Cache de materiais quantizados por fase: não processa cada pixel em cada
    quadro. Alpha é preservado. Funciona sem NumPy em modo sem relighting.
    """
    def __init__(self, limit=16):
        self.cache = OrderedDict()
        self.limit = limit
        self.enabled = np is not None

    def clear(self):
        self.cache.clear()

    def render(self, source, key, night, phase, layer):
        if not self.enabled or layer >= 3:
            return source
        # Mais frequente no amanhecer/anoitecer; paleta discreta para pixel art.
        bucket = max(0, min(7, int(float(phase) * 8)))
        dark_bucket = max(0, min(5, int(float(night) * 5 + .5)))
        ck = (key, bucket, dark_bucket)
        if ck in self.cache:
            self.cache.move_to_end(ck)
            return self.cache[ck]
        try:
            rgb = pygame.surfarray.array3d(source).astype(np.float32)
            a = pygame.surfarray.array_alpha(source)
            lum = rgb[...,0] * .27 + rgb[...,1] * .62 + rgb[...,2] * .11
            # Height field calculado do albedo: não equivale a normal map pintado.
            gx, gy = np.gradient(lum / 255.0)
            nx = -gx * 1.8
            ny = -gy * 1.8
            denom = np.sqrt(nx * nx + ny * ny + 1.0)
            nx /= denom
            ny /= denom
            nz = 1.0 / denom
            az = 2.0 * math.pi * (bucket + .5) / 8.0
            lx = .53 * math.cos(az)
            ly = -.42 * math.sin(az)
            lz = .74
            diffuse = np.maximum(0.0, nx * lx + ny * ly + nz * lz)
            darkness = dark_bucket / 5.0
            # Preserva a hierarquia: distantes menos contrastados, foco na pista.
            diffuse_strength = (.16, .21, .24)[min(2, layer)]
            gain = (.82 + .14 * diffuse + diffuse_strength * (diffuse-.50))
            gain *= (1.0 - darkness * .23)
            specular = np.power(np.maximum(0.0, diffuse), 13.0) * (.022 + darkness * .020)
            out = np.clip(rgb * gain[...,None] + 255.0 * specular[...,None], 0, 255).astype(np.uint8)
            result = source.copy()
            buf = pygame.surfarray.pixels3d(result)
            buf[:] = out
            del buf
            # Rim-light leve nos contornos opacos voltados ao céu, sem blur grande.
            if layer == 2 and darkness > .16:
                edge = pygame.mask.from_surface(source, 60).outline(4)
                accent = mix((110,155,209), (205,239,249), darkness)
                if len(edge) > 2:
                    pygame.draw.lines(result, accent, False, edge, 1)
            self.cache[ck] = result
            while len(self.cache) > self.limit:
                self.cache.popitem(last=False)
            return result
        except (ValueError, pygame.error, MemoryError, TypeError):
            # Renderização original segue utilizável sem relighting.
            self.enabled = False
            self.cache.clear()
            return source


class VerletCable:
    """Cabo discreto ancorado aos dois lados; 9 nós com vento e passagem."""
    def __init__(self, seed=0):
        r = random.Random(seed)
        self.points = [pygame.Vector2(i * 16.0, 3.0 * math.sin(i * math.pi / 8.0)) for i in range(9)]
        self.prev = [p.copy() for p in self.points]
        self.last_tick = -1
        self.phase = r.random() * 6.28

    def step(self, frame, wind=0.0, wake=0.0):
        if frame == self.last_tick:
            return
        self.last_tick = frame
        for i in range(1, 8):
            p = self.points[i]
            prev = self.prev[i]
            vx, vy = (p.x-prev.x) * .91, (p.y-prev.y) * .91
            prev.update(p.x, p.y)
            p.x += vx + wind * (.2 + i * .02) + math.sin(frame * .038+self.phase+i) * .12 + wake * .2
            p.y += vy + .095
        for _ in range(4):
            self.points[0].update(0, 0)
            self.points[-1].update(128, 0)
            for i in range(8):
                a, b = self.points[i], self.points[i+1]
                delta = b-a
                dist = delta.length()
                if dist < 0.01:
                    continue
                correction = delta * ((dist-16.15)/dist)
                if i == 0:
                    b -= correction
                elif i == 7:
                    a += correction
                else:
                    a += correction * .5
                    b -= correction * .5

    def draw(self, surface, left, top, biome='cidade', night=0.0):
        base = (88,100,118) if biome != 'floresta' else (78,123,86)
        for a,b in zip(self.points, self.points[1:]):
            pa = (int(left+a.x), int(top+a.y))
            pb = (int(left+b.x), int(top+b.y))
            pygame.draw.line(surface, (30,43,56), (pa[0],pa[1]+2), (pb[0],pb[1]+2), 3)
            pygame.draw.line(surface, base, pa, pb, 2)
        if night > .1 and biome == 'cidade_futurista':
            for i in (2,5):
                point=self.points[i]
                pygame.draw.circle(surface,(112,230,252),(int(left+point.x),int(top+point.y)),2)


class AtmosphereFlow:
    """Campo escalar 2D reduzido com advecção e turbulência por vento/impacto.

    É uma aproximação de fluxo ambiental, NÃO um solver Navier–Stokes.
    """
    def __init__(self, seed=13):
        self.cols, self.rows = 37, 9
        self.field = [[0.0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.phase = seed
        self.wind = 0.0
        self.impulses = []
        self._low = pygame.Surface((self.cols * 4, self.rows * 4), pygame.SRCALPHA)
        self.opacity = 0.0

    def excite(self, x, force=1.0):
        column = max(0, min(self.cols-1, int(x / 450.0 * self.cols)))
        self.impulses.append((column, min(2.0, force)))
        if len(self.impulses) > 8:
            self.impulses.pop(0)

    def update(self, frame, biome, climate, speed):
        self.phase += 1
        dusty = climate in ('tempestade_areia','areia','tempestade','nevasca','cinzas','polen')
        smoky = biome in ('vulcao','floresta')
        self.opacity = .48 if dusty else (.17 if smoky else .06)
        wind = .85 if dusty else .30
        wind += min(1.5, speed / 13.0) * .2
        self.wind = wind
        old = self.field
        fresh = []
        for j in range(self.rows):
            row=[]
            for i in range(self.cols):
                # semi-Lagrangiano discretizado + difusão fraca
                upstream = old[j][max(0, i-1)]
                local = old[j][i]
                yup = old[max(0,j-1)][i]
                vortex = math.sin(i*.63 + j*.77 + self.phase*.065) * .021
                source = .028 if j>3 and smoky else .012
                row.append(max(0.,min(1., local*.67 + upstream*.18*wind + yup*.09 + source + vortex)))
            fresh.append(row)
        for col, force in self.impulses:
            for j in range(2, 7):
                for dx in (-1,0,1):
                    i=max(0,min(self.cols-1,col+dx))
                    fresh[j][i] = min(1.0, fresh[j][i] + .13*force)
        self.impulses.clear()
        self.field=fresh

    def draw(self, surface, biome, night):
        if self.opacity < .08:
            return
        self._low.fill((0,0,0,0))
        if biome == 'vulcao': color=(148,110,105)
        elif biome == 'floresta': color=(140,190,145)
        elif biome == 'deserto': color=(224,184,127)
        else: color=(166,190,220)
        for j,row in enumerate(self.field):
            for i,v in enumerate(row):
                strength = v * self.opacity
                if strength > .018:
                    pygame.draw.rect(self._low,(*color,min(80,int(strength*155))), (i*4,j*4,4,4))
        large=pygame.transform.smoothscale(self._low,(450,200))
        surface.blit(large,(0,465))


class WorldDebris:
    """Partículas quicantes e decals persistentes por chunk, sem alterar colisões."""
    def __init__(self):
        self.active=[]
        self.decals={}

    def emit(self, chunk, local_x, biome, kind='pouso', count=6):
        rng=random.Random(int(chunk*923+local_x*13+len(self.active)))
        palette={'cidade':(124,137,151),'neve':(228,242,250),'deserto':(217,175,113),
                 'vulcao':(239,120,62),'floresta':(134,190,97),'cidade_futurista':(109,221,248),
                 'ilhas_celestes':(181,239,223)}
        color=palette.get(biome,(176,189,206))
        for _ in range(count):
            self.active.append({'wx': float(chunk*360+local_x), 'y':716.0,
                                'vx':rng.uniform(-2.6,2.0), 'vy':rng.uniform(-3.4,-.7),
                                'color':color,'age':0})
        if len(self.active) > 42:
            self.active=self.active[-42:]
        # v3.125.0: marcas/pegadas persistentes desativadas.
        # Particulas temporarias do impacto continuam normalmente.

    def tick(self, speed):
        for p in self.active:
            p['wx']+=p['vx']
            p['y']+=p['vy']
            p['vy']+=.22
            if p['y']>=725:
                p['y']=725
                p['vy']=-abs(p['vy'])*.42
                p['vx']*=.80
            p['age']+=1
        self.active=[p for p in self.active if p['age']<70]

    def draw(self, target, travel, layer_speed=.382):
        cam=travel*layer_speed
        # v3.125.0: nao desenhar linhas ou pegadas permanentes no solo.
        for p in self.active:
            x=p['wx']-cam
            if -10<x<460:
                pygame.draw.rect(target,p['color'],(int(x),int(p['y']),2,2))
