# -*- coding: utf-8 -*-
"""QA761 — libera somente alias geometry aposentado após switch de bioma.

Nao muda a Surface de transição, os caches do bioma ativo nem a oclusão
da cena corrente. O clone de geometria fica intacto quando nao e emprestado.
"""
import os
from functools import wraps

_INSTALADO=False
_ORIGINAL=None
_STATS={'trocas':0,'aliases_aposentados':0,'outros_preservados':0}


def diagnostico():
    return dict(_STATS,instalado=_INSTALADO)


def instalar():
    global _INSTALADO,_ORIGINAL
    if _INSTALADO or os.environ.get('PIXELRUSH_QA_GEOMETRY_RETIRE','1')!='1':
        return
    from pixelrush_world_v3130 import LivingWorld
    _ORIGINAL=LivingWorld.switch

    @wraps(_ORIGINAL)
    def switch(self,biome):
        anterior=self.biome
        cena=(self.city2 if anterior=='cidade'
              else getattr(self,'modular',{}).get(anterior))
        buffers=getattr(self,'_city_surfaces',{})
        alvo=buffers.get(('geometry',False))
        emprestado=(alvo is not None and cena is not None
                    and getattr(cena,'_geometry_view',None) is alvo)
        retorno=_ORIGINAL(self,biome)
        if self.biome!=anterior:
            _STATS['trocas']+=1
            # World.switch ja limpou _city_surfaces; se a cena aposentada
            # ainda guarda o proprio buffer, ele impedia liberar ~900KB.
            # Nao modificar snapshots independentes (destinos externos).
            if emprestado and getattr(cena,'_geometry_view',None) is alvo:
                cena._geometry_view=None
                if getattr(cena,'_qa_geometry_borrowed_surface',None) is alvo:
                    cena._qa_geometry_borrowed_surface=None
                _STATS['aliases_aposentados']+=1
            else:
                _STATS['outros_preservados']+=1
        return retorno

    LivingWorld.switch=switch
    _INSTALADO=True


def restaurar_para_teste():
    global _INSTALADO,_ORIGINAL
    if _INSTALADO:
        from pixelrush_world_v3130 import LivingWorld
        LivingWorld.switch=_ORIGINAL
    _ORIGINAL=None
    _INSTALADO=False
