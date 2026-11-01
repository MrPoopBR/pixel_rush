"""Plano I v3.220.0: volume organico/arquitetonico em FAR/MID de quatro biomas.

Somente pixels RGB ja opacos dos sprites recebidos da cadeia visual existente.
Nenhuma geometria de colisao, canal alfa, asset de origem ou mapa tecnico e alterado.
Sprites processados no primeiro uso, nunca pixels por frame. Sem RNG.
"""
from collections import OrderedDict
from types import MethodType
import numpy as np
import pygame
from pixelrush_geometria_v3219 import _deslocar

BIOMAS = frozenset(('floresta', 'vulcao', 'cidade_futurista', 'ilhas_celestes'))
PLANOS = frozenset(('far', 'mid'))
LIMITE_TILE = 14  # por cena, 14 x 225 x 250 x 4 B ~ 3.0 MiB


def lapidar(original, bioma, plano):
    """Refina faces/encostas existentes sem criar silhuetas nem trocar alfa."""
    if bioma not in BIOMAS or plano not in PLANOS or not (original.get_flags() & pygame.SRCALPHA):
        return original.copy(), {'rgb': 0, 'alfa_igual': True}
    w, h = original.get_size()
    if w < 44 or h < 50:
        return original.copy(), {'rgb': 0, 'alfa_igual': True}
    rgb = pygame.surfarray.array3d(original)
    alpha = pygame.surfarray.array_alpha(original)
    solido = alpha >= 245
    # Uma vizinhanca realmente conectada e opaca suporta cada alteracao.
    seguro = solido.copy()
    for dx,dy in ((-2,0),(2,0),(0,-2),(0,2),(-1,0),(1,0),(0,-1),(0,1)):
        seguro &= _deslocar(solido,dx,dy)
    seguro[:17,:] = False
    seguro[-17:,:] = False
    seguro[:,:16] = False
    seguro[:,-18:] = False
    # Os tiles modulares 225x250 dobram ao compor o mundo: y>=184 pertence
    # a regiao protegida do encontro visual da pista.
    if (w,h)==(225,250):
        seguro[:,184:] = False
    lum = (rgb[:,:,0].astype(np.uint16)*3 + rgb[:,:,1].astype(np.uint16)*6 + rgb[:,:,2].astype(np.uint16))//10
    material = seguro & (lum>25) & (lum<239)
    if not np.any(material):
        return original.copy(), {'rgb':0,'alfa_igual':True}

    # Bordas largas sao volume real, inferido da mascara opaca em diferentes
    # distancias. Sem desenhar novos contornos de sprites transparentes.
    esquerda = material & ~_deslocar(solido, 7, 0)
    direita = material & ~_deslocar(solido,-8, 0)
    acima = material & ~_deslocar(solido, 0, 8)
    abaixo = material & ~_deslocar(solido,0,-8)
    x,y = np.ogrid[:w,:h]
    mod = np.zeros((w,h), dtype=np.int16)

    if bioma == 'floresta':
        # Troncos e copas arredondados: claridade lateral ampla e oclusao sob
        # a copa; modula as massas ja presentes, sem galhos extras.
        mod[esquerda] += 16
        mod[direita] -= 20
        mod[acima] += 9
        mod[abaixo] -= 15
        # Meios-tons nas massas internas: gradiente continuo, nao linhas
        # decorativas ou textura em xadrez.
        p=(x%52).astype(np.int16)
        eixo=(p-26)
        ondulacao=np.rint(6*(1-(eixo.astype(np.float32)/26)**2)).astype(np.int16)
        mod += np.where(material & (lum>45) & (lum<180), ondulacao-3, 0)
    elif bioma == 'vulcao':
        # Cristas de basalto iluminadas e flancos sombreados: reforcar
        # a geometria do monte e profundidade abaixo das saliencias.
        mod[acima] += 17
        mod[esquerda] += 12
        mod[direita] -= 24
        mod[abaixo] -= 23
        # Inclinacoes do relevo com profundidade sob as faces existentes.
        sombra_profunda = material & (lum>38) & (lum<205) & (y>70) & (x%83>38)
        mod[sombra_profunda] -= 7
    elif bioma == 'cidade_futurista':
        # Facetamento arquitetonico: relevo de vigas/fachadas, incidencias
        # opostas em superficies retas, sem adicionar linhas neon artificiais.
        mod[acima] += 15
        mod[esquerda] += 17
        mod[direita] -= 26
        mod[abaixo] -= 12
        face=(x%72)
        claro=material & (lum>65) & (lum<200) & (face<22)
        sombra=material & (lum>65) & (lum<200) & (face>50)
        mod[claro] += 5
        mod[sombra] -= 8
    else:  # ilhas_celestes
        # Ilhas suspensas: topo claro e underside rochoso contrastante,
        # valorizando formas flutuantes existentes sem inventar outras.
        mod[acima] += 24
        mod[esquerda] += 11
        mod[direita] -= 17
        mod[abaixo] -= 26
        # Planos obliquos largos (fragmentos minerais ja existentes).
        faceta = ((x+2*y)//61)%3
        rocha=material & (lum>48) & (lum<207)
        mod[rocha & (faceta==0)] += 5
        mod[rocha & (faceta==2)] -= 7

    if plano=='far':
        mod=np.rint(mod*.68).astype(np.int16)
    mod[~material]=0
    novo_rgb=np.clip(rgb.astype(np.int16)+mod[:,:,None],0,255).astype(np.uint8)
    contagem=int(np.count_nonzero(np.any(rgb!=novo_rgb,axis=2)))
    if contagem==0:
        return original.copy(), {'rgb':0, 'alfa_igual':True}
    novo=pygame.Surface((w,h),pygame.SRCALPHA,32)
    pix=pygame.surfarray.pixels3d(novo)
    pix[:]=novo_rgb
    del pix
    aa=pygame.surfarray.pixels_alpha(novo)
    aa[:]=alpha
    del aa
    return novo, {'rgb':contagem, 'alfa_igual':True}


def _cacheado(cena, sprite, plano):
    estado=cena._geometria_3220
    cache=estado['cache']
    chave=(plano,id(sprite))
    if chave in cache:
        cache.move_to_end(chave)
        return cache[chave]
    resultado,metricas=lapidar(sprite,cena.biome,plano)
    cache[chave]=resultado
    estado['pixels_rgb']+=metricas['rgb']
    estado['criados']+=1
    estado['bytes']+=resultado.get_pitch()*resultado.get_height()
    while len(cache)>LIMITE_TILE:
        _,velho=cache.popitem(last=False)
        estado['bytes']-=velho.get_pitch()*velho.get_height()
    return resultado


class _VisaoRefinada:
    """Adapta o passe legado do Vulcao somente no ultimo passo visual."""
    def __init__(self, cena, plano, origem):
        self.cena,self.plano,self.origem=cena,plano,origem
    def __len__(self):
        return len(self.origem)
    def __getitem__(self,indice):
        return _cacheado(self.cena,self.origem[indice],self.plano)


def instalar_modular(cena,leve=False):
    if getattr(cena,'_geometria_3220',None) is not None:
        return cena
    cena._geometria_3220={'cache':OrderedDict(),'pixels_rgb':0,'criados':0,'bytes':0,'limite':LIMITE_TILE}
    if leve or cena.biome not in BIOMAS:
        return cena
    # Os biomas comuns acessam os tiles via _tile_map. Encadear DEPOIS dos
    # refinamentos v3.197..v3.219 em vez de substituir a cadeia.
    anterior=cena._tile_map
    cena._geometria_3220_tile_anterior=anterior
    def _tile(self,plano,indice,tipo):
        sprite=self._geometria_3220_tile_anterior(plano,indice,tipo)
        if tipo=='image' and plano in PLANOS and sprite is not None:
            return _cacheado(self,sprite,plano)
        return sprite
    cena._tile_map=MethodType(_tile,cena)
    # O Vulcao usa acesso direto a _layers, atraves dos wrappers legados de
    # identidade e volume. Interceptar o desenho ORIGINAL apenas ao final da
    # cadeia para evitar duplicar ambas as transformacoes.
    if cena.biome=='vulcao':
        base_legada=cena._geo3197_draw_legado
        cena._geo3220_draw_base=base_legada
        def _desenhar_ultimo(self,dst,plano,travel,tipo):
            if tipo!='image' or plano not in PLANOS:
                return self._geo3220_draw_base(dst,plano,travel,tipo)
            anterior_layers=self._layers[plano]
            self._layers[plano]=_VisaoRefinada(self,plano,anterior_layers)
            try:
                return self._geo3220_draw_base(dst,plano,travel,tipo)
            finally:
                self._layers[plano]=anterior_layers
        cena._geo3197_draw_legado=MethodType(_desenhar_ultimo,cena)
    return cena
