# -*- coding: utf-8 -*-
"""Prova QA784: quadros reais Cidade dia/noite/chuva com alfa oculto."""
import os,pygame,ctypes as C
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ['PIXELRUSH_QA_GLES_PBO']='0'
from pixelrush_qa_city_bootstrap_v327759 import instalar as init
init()
from pixelrush_world_v3130 import LivingWorld
import pixelrush_qa_gles_present_v327735 as pres
from pixelrush_qa_gles_exact_v327736 import shaders
from pixelrush_qa_gles_twopass_v327784 import FullscreenTwoPassQA,_cpu_result
pygame.init();pygame.transform.set_smoothscale_backend('SSE2')
pres.VERT,pres.FRAG=shaders('GLES3','SSE2',(450,800))
p=pres.GLES2DirectPresenterQA(450,800,fullscreen=True)
two=FullscreenTwoPassQA(p)
read=p._fcall('glReadPixels',None,[C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint,C.c_uint,C.c_void_p])
x,y,w,h=p.qa_viewport
world=LivingWorld('cidade')
world.lightweight=False
casos=0
try:
    for i,(night,climate) in enumerate(((0,'limpo'),(.5,'chuva'),(.95,'tempestade'))):
        for j in range(5):
            world.update(6.3,night,climate,.36)
        for alpha in (False,True):
            s=pygame.Surface((450,800),pygame.SRCALPHA if alpha else 0,32)
            s.fill((25,51,101,0) if alpha else (25,51,101))
            world.draw(s)
            pygame.draw.rect(s,(23,36,60,190) if alpha else (23,36,60),(0,0,450,72))
            z=.034 if i==2 else (.025 if i else .008)
            two.draw(s,z,4-i)
            actual=C.create_string_buffer(w*h*4)
            read(x,y,w,h,0x1908,0x1401,actual)
            expected=pygame.image.tobytes(
                pygame.transform.scale(_cpu_result(s,z,4-i),(w,h)),'RGBA',True)
            assert actual.raw==expected,('Cidade RGBA divergente',night,climate,alpha,z)
            casos+=1
    assert casos==6
    print('QA784 Cidade RGBA real',pygame.display.get_window_size(),'casos',casos,'divergencias',0)
finally:
    two.close();p.close();pygame.quit()
