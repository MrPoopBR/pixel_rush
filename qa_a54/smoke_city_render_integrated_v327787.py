# -*- coding: utf-8 -*-
"""QA787: smoke QA785+QA786 preservadas e mapas tecnicos rollback off/on."""
import argparse,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
p=argparse.ArgumentParser();p.add_argument('--enabled',choices=('0','1'),required=True)
a=p.parse_args()
os.environ['PIXELRUSH_QA_ANDROID']='0'
os.environ['PIXELRUSH_QA_GLES_BRIDGE']='0'
os.environ['PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW']='1'
os.environ['PIXELRUSH_QA_CITY_TECH_COVER']=a.enabled
import pygame
pygame.init();pygame.display.set_mode((450,800))
from pixelrush_qa_render_v327729 import instalar,restaurar_para_teste
instalar()
from pixelrush_qa_city_opaque_overdraw_v327786 import diagnostico as opaque_diag
from pixelrush_qa_city_technical_cover_v327787 import diagnostico as technical_diag
from pixelrush_world_v3130 import LivingWorld
world=LivingWorld('cidade');world.lightweight=False
assert world.city2._scaled_limit==20
hashes=[]
try:
    for i in range(1,22):
        night=(0.,.43,.9)[i//8]
        climate=('limpo','chuva','tempestade')[i//8]
        world.update(36 if i>12 else 6.3,night,climate,.37)
        target=pygame.Surface((450,800),pygame.SRCALPHA,32)
        target.fill((31,77,97,i*10%256))
        world.draw(target)
        hashes.append(hashlib.sha256(pygame.image.tobytes(target,'RGBA')).hexdigest())
        if i%5==0:
            for draw in (world.draw_effect_mask,world.draw_normal_map,
                         world.draw_geometry_map,world.draw_material_map,
                         world.draw_flow_map):
                surf=pygame.Surface((450,800),pygame.SRCALPHA,32)
                surf.fill((115,26,187,0))
                draw(surf)
                hashes.append(hashlib.sha256(pygame.image.tobytes(surf,'RGBA')).hexdigest())
    stats=technical_diag()
    old=opaque_diag()
    assert old['chunks_hidden']>0,old
    assert (stats['clip_geo_mat']>0 and stats['clip_fxmask']>0)==(a.enabled=='1'),stats
    assert len(hashes)==41,len(hashes)
    print(json.dumps({'enabled':a.enabled,'hashes':hashes,
        'clip_geo_mat':stats['clip_geo_mat'],'clip_fxmask':stats['clip_fxmask'],
        'chunks_hidden_qa786':old['chunks_hidden'],'cache_limit':world.city2._scaled_limit}))
finally:
    restaurar_para_teste()
    pygame.quit()
