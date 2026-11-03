# -*- coding: utf-8 -*-
"""QA766: reutiliza dicionarios de particulas ambientais entre biomas.

O PoolManager de explosoes ja existe e nao e duplicado. Este modulo
cobre apenas as 8 a 14 particulas de ambiente de ParallaxBackground,
que no legado recriavam todos os dicionarios a cada troca de bioma.
RNG isolado, draw/ordem/velocidade/id de estado preservados.
"""
import os
import math
import random
from functools import wraps

_COLORS={
    "cidade":((170,206,234),(226,198,120),8),
    "neve":((238,246,255),(192,221,240),14),
    "deserto":((240,210,160),(214,170,116),9),
    "vulcao":((255,149,82),(247,205,123),8),
    "floresta":((157,217,124),(245,235,146),8),
    "cidade_futurista":((94,238,249),(206,108,255),9),
    "ilhas_celestes":((226,248,255),(152,240,206),8),
    "reino_submerso":((122,229,238),(174,241,252),9),
}
_DEFAULT=((196,210,224),(235,240,245),8)
_ORIGINALS={}
_ORIGINAL_KILL={}
_STATUS={'reinicios':0,'reusados':0,'criados':0,'fallbacks':0,
         'max_reserva':0,'particulas_excedentes_liberadas':0}

def diagnostico():
    return dict(_STATUS,classes=len(_ORIGINALS),classes_particulas=len(_ORIGINAL_KILL))

def instalar(classe, particula_cls=None):
    # Reutilizacao de dicionarios ambientais + limite ao excedente
    # ocioso do pool ORIGINAL de explosoes (sem limitar ativos/render).
    if particula_cls is not None and particula_cls not in _ORIGINAL_KILL and (
            os.environ.get('PIXELRUSH_QA_PARTICULA_RELEASE','1')=='1'):
        original_kill=particula_cls.kill
        _ORIGINAL_KILL[particula_cls]=original_kill
        @wraps(original_kill)
        def kill(self):
            era_livre=getattr(self,'_pool_livre',False)
            original_kill(self)
            manager=getattr(self,'pool_manager',None)
            if (not era_livre and manager is not None
                    and getattr(self,'_pool_livre',False)):
                base=getattr(manager,'particulas_pool',None)
                free=getattr(manager,'particulas_disponiveis',None)
                if (base is not None and free is not None and
                        len(base)>256 and len(free)>256 and self in free):
                    # Liberar somente o proprio objeto recem morto.
                    # Sprite.kill ja o removeu de TODOS os grupos.
                    free.remove(self)
                    base.remove(self)
                    self.pool_manager=None
                    _STATUS['particulas_excedentes_liberadas']+=1
        particula_cls.kill=kill

    if classe in _ORIGINALS or os.environ.get('PIXELRUSH_QA_PARTICULAS_POOL','1')!='1':
        return
    metodo=classe._reiniciar_particulas_ambiente
    _ORIGINALS[classe]=metodo
    @wraps(metodo)
    def reiniciar(self):
        atual=getattr(self,'_particulas_ambiente',None)
        if not isinstance(atual,list):
            _STATUS['fallbacks']+=1
            return metodo(self)
        reserva=getattr(self,'_qa_reserva_particulas_ambiente',None)
        if reserva is None:
            reserva=[]
            self._qa_reserva_particulas_ambiente=reserva
        try:
            biome=self.cenario
            cores=_COLORS.get(biome,_DEFAULT)
            rng=random.Random(7000+sum(ord(c) for c in biome))
            # List object is NEW as in the original; only private per-particle
            # dictionaries are recycled. No global RNG used.
            reserva.extend(atual)
            novas=[]
            for _ in range(cores[2]):
                if reserva:
                    p=reserva.pop()
                    _STATUS['reusados']+=1
                else:
                    p={}
                    _STATUS['criados']+=1
                p['x']=rng.uniform(0,450)
                p['y']=rng.uniform(190,560)
                p['vx']=rng.uniform(0.04,0.22)
                p['vy']=rng.uniform(-0.03,0.03)
                p['tam']=rng.choice((1,1,2,2,3 if biome in ('neve','cidade_futurista') else 2))
                p['fase']=rng.uniform(0.0,math.tau)
                p['cor_a']=cores[0]
                p['cor_b']=cores[1]
                novas.append(p)
            self._particulas_ambiente=novas
            # At most 14 per scene, never retained after scene release.
            if len(reserva)>14:
                del reserva[:len(reserva)-14]
            _STATUS['max_reserva']=max(_STATUS['max_reserva'],len(reserva))
            _STATUS['reinicios']+=1
        except (AttributeError,TypeError,ValueError,MemoryError):
            _STATUS['fallbacks']+=1
            metodo(self)
    classe._reiniciar_particulas_ambiente=reiniciar

def restaurar_para_teste():
    for classe,original in tuple(_ORIGINALS.items()):
        classe._reiniciar_particulas_ambiente=original
    _ORIGINALS.clear()
    for classe,original in tuple(_ORIGINAL_KILL.items()):
        classe.kill=original
    _ORIGINAL_KILL.clear()
    for chave in _STATUS:
        _STATUS[chave]=0
