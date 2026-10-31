"""Pixel Rush v3.127.0 — acabamento modular neve e deserto.

Herda integralmente a regra de composição e colisoes do cenário 2.0:
nenhuma mudança nos fatores de parallax, chao, controle de scroll, spawn,
profundidade, material GPU ou modo leve. Elementos são gravados nos chunks
225x250 na inicialização, nunca desenhados como objetos soltos na pista.
"""
import random
import pygame
from pixelrush_biomes2_v3126 import (ModularBiomeScene as _Biome126,
                                       MODULAR_BIOMES, SUPPORTED_BIOMES,
                                       LW, LH, _rect, _line, _p, _rgb)


class ModularBiomeScene(_Biome126):
    def _snow_house(self, surf, x, ybase, w, h, seed):
        super()._snow_house(surf,x,ybase,w,h,seed)
        x=int(x);ybase=int(ybase);w=int(w);h=int(h)
        y=ybase-h
        rng=random.Random(10073+seed*7)
        # Alvenaria de pedra clara, contornos, pequenas placas azulejadas.
        for row, yy in enumerate(range(y+8, ybase-22, 9)):
            for xx in range(x+4+row%2*5,x+w-7,10):
                _line(surf,(72,87,138),xx,yy,xx+5,yy)
                _rect(surf,(142,150,195),xx+1,yy+2,3,1)
        # Fachada interna: moldura dos cantos, separacao entre andares.
        for side in (x+1,x+w-6):
            _rect(surf,(65,74,128),side,y+8,2,h-14)
            _line(surf,(151,155,207),side+1,y+9,side+1,ybase-8)
        for yy in range(y+26,ybase-12,28):
            _rect(surf,(59,72,119),x+3,yy,max(3,w-9),2)
            _line(surf,(156,163,213),x+4,yy+2,x+w-7,yy+2)
        # Telhas na borda lateral, sem quebrar o telhado original.
        for xx in range(x+6,x+w-6,9):
            _rect(surf,(250,253,255),xx,y+3,6,2)
            _rect(surf,(165,210,240),xx+2,y+5,4,1)
        # Iluminação arquitetônica colocada *dentro* da fachada.
        for xx in range(x+9,x+w-9,17):
            if rng.random()<.72:
                _rect(surf,(64,74,122),xx,ybase-20,6,10)
                _rect(surf,(250,219,149),xx+1,ybase-19,4,8)
                _line(surf,(255,246,214),xx+1,ybase-18,xx+1,ybase-13)
        # Pequenas arandelas presas à parede, sem adicionar sprites na pista.
        if w>42:
            _rect(surf,(61,70,115),x+6,ybase-29,3,5)
            _rect(surf,(255,222,138),x+7,ybase-27,3,2)
            _rect(surf,(213,238,255),x+6,ybase-31,5,2)

    def _pine(self,surf,x,base,height,snow=True):
        super()._pine(surf,x,base,height,snow)
        x=int(x);base=int(base);height=int(height)
        tip=base-9-height*3//4
        # Sombras e agulhas em pequenos agrupamentos que pertencem à copa.
        for j in range(3):
            cy=base-13-j*(height//4)
            width=max(3,(height//2-j*3)//2)
            if snow:
                _line(surf,(21,70,90),x-4,cy+3,x+4,cy+3)
                _line(surf,(151,201,220),x-width//2,cy-2,x+width//2,cy-2)
                _rect(surf,(252,253,255),x-2,cy-5,5,2)
            else:
                _line(surf,(34,89,59),x-5,cy+3,x+4,cy+3)
                _line(surf,(114,193,120),x-width//2,cy-2,x+width//2,cy-2)
        if snow:
            _rect(surf,(243,250,255),x-2,tip+6,4,2)

    def _lamp(self,surf,x,ybase,cold=True):
        super()._lamp(surf,x,ybase,cold)
        x=int(x); ybase=int(ybase)
        _rect(surf,(36,48,83) if cold else (81,59,56),x-2,ybase-20,1,13)
        _line(surf,(148,159,187) if cold else (201,154,111),x,ybase-20,x,ybase-5)
        _rect(surf,(255,247,194),x-2,ybase-26,3,2)
        # Nunca desenhar luz no nivel da rua; o topo é ybase-30.

    def _desert_palace(self,surf,x,base,width,h,idx):
        super()._desert_palace(surf,x,base,width,h,idx)
        x=int(x);base=int(base);width=int(width);h=int(h)
        top=base-h
        rng=random.Random(9243+idx*13)
        # Pedras de arenito e rejunte em blocos desenhados diretamente na parede.
        for row,yy in enumerate(range(top+13,base-13,9)):
            for xx in range(x+4+(row%2)*4,x+width-5,11):
                _line(surf,(148,95,80),xx,yy,xx+5,yy)
                _rect(surf,(240,187,125),xx+1,yy+2,2,1)
        for yy in (top+8,top+24):
            _line(surf,(248,206,148),x+3,yy,x+width-4,yy)
        # azulejos cerâmicos nas bordas existentes.
        for xx in range(x+8,x+width-7,13):
            _rect(surf,(83,132,134),xx,top+8,3,3)
            _rect(surf,(166,206,178),xx+1,top+8,1,1)
        if width>=40:
            _rect(surf,(111,80,89),x+width//2-5,base-17,10,15)
            _rect(surf,(184,142,116),x+width//2-3,base-15,6,13)
            _line(surf,(245,213,158),x+width//2-3,base-14,x+width//2-3,base-5)
        # Ornamentação presa ao reboco — sem plantas flutuantes.
        for xx in (x+3,x+width-8):
            _rect(surf,(124,84,85),xx,top+14,3,8)
            _rect(surf,(244,194,138),xx+1,top+15,1,5)

    def _palm(self,surf,x,ground,size,idx):
        super()._palm(surf,x,ground,size,idx)
        x=int(x);ground=int(ground);size=int(size)
        crown_y=ground-size
        for dx,dy in ((-15,2),(-9,-5),(7,-7),(16,3)):
            _line(surf,(127,185,98),x+3,crown_y,x+dx,crown_y+dy)
        # trama horizontal do tronco
        for yy in range(ground-size+8,ground-3,6):
            _line(surf,(74,51,45),x,yy,x+4,yy-1)

    def _cactus(self,surf,x,ground,height):
        super()._cactus(surf,x,ground,height)
        x=int(x);ground=int(ground);height=int(height)
        for yy in range(ground-height+6,ground-4,8):
            _rect(surf,(136,187,110),x,yy,1,2)
            _rect(surf,(235,206,154),x-3,yy+2,2,1)

    def _make_chunk(self,layer,index):
        tile=super()._make_chunk(layer,index)
        # Detalhes estáticos extras apenas em locais ancorados; todo pixel
        # criado uma vez por variante. Não desenhar no céu ou em cima do jogador.
        if self.biome=='neve':
            if layer=='mid':
                # rebites e ornamentos PRESOS ao viaduto horizontal de y=159.
                for xx in range(8,LW,24):
                    _rect(tile,(92,102,156),xx,157,3,2)
                    _rect(tile,(254,231,165),xx+1,160,2,2)
            elif layer=='near':
                for xx in range(6,LW,16):
                    _line(tile,(183,204,220),xx,231,xx+7,231)
                    _rect(tile,(107,127,145),xx+3,244,6,1)
                # A neve acumula no passeio, NAO no asfalto.
                _line(tile,(250,251,252),0,227,LW-1,227,1)
                for xx in range(14,LW,52):
                    _rect(tile,(227,241,250),xx,229,14,2)
        else:
            if layer=='mid':
                for xx in range(8,LW,36):
                    _rect(tile,(245,199,143),xx,178,6,2)
                    _rect(tile,(112,83,92),xx+4,193,2,8)
            elif layer=='near':
                for xx in range(2,LW,15):
                    _line(tile,(190,131,104),xx,239,xx+8,239,1)
                    _rect(tile,(230,169,117),xx+1,230,5,1)
        return tile
