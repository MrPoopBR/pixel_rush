# -*- coding: utf-8 -*-
"""Bancada offline de camera e cenografia para QA 3.277.39.

SDL dummy Linux NAO equivale ao driver/GPU do Android. O relatorio nunca
afirma ganho de FPS no aparelho, e nao altera jogo ou shader ativo.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import sys
import time
from types import SimpleNamespace
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import pygame
from pixelrush_city2_v3118 import CityPilotScene
from pixelrush_qa_gles_exact_v327736 import gate_integracao,shaders


def quantis(valores):
    v=sorted(valores)
    return {'n':len(v),'mediana_ms':round(statistics.median(v),4),
            'p95_ms':round(v[round(.95*(len(v)-1))],4),
            'max_ms':round(v[-1],4)}


def medir(funcao,rodadas=90,warmup=12):
    amostras=[]
    for i in range(rodadas+warmup):
        t=time.perf_counter_ns()
        funcao()
        if i>=warmup:
            amostras.append((time.perf_counter_ns()-t)/1e6)
    return quantis(amostras)


def camera():
    antigo=pygame.transform.get_smoothscale_backend()
    imagem=pygame.Surface((450,800)).convert()
    for y in range(800):
        pygame.draw.line(imagem,((y*7)%256,(y*13)%256,(y*29)%256),(0,y),(449,y))
    for x in range(35,450,27):
        pygame.draw.rect(imagem,(31,198,243),(x,(x*13)%640,19,27))
    tamanho=(470,840)
    buffer=pygame.Surface(tamanho).convert(imagem)
    resultados={}
    byte_ref=None
    try:
        for candidato in [antigo]+[x for x in ('GENERIC','SSE2','NEON') if x!=antigo]:
            try:pygame.transform.set_smoothscale_backend(candidato)
            except (pygame.error,ValueError):continue
            com_buffer=medir(lambda:pygame.transform.smoothscale(imagem,tamanho,buffer))
            sem_buffer=medir(lambda:pygame.transform.smoothscale(imagem,tamanho))
            bytes_atuais=pygame.image.tobytes(
                pygame.transform.smoothscale(imagem,tamanho,buffer),'RGB')
            if candidato==antigo:byte_ref=bytes_atuais
            resultados[candidato]={'destino_reutilizado':com_buffer,
                                   'destino_novo':sem_buffer,
                                   'pixel_identico_ao_original':bytes_atuais==byte_ref}
    finally:
        pygame.transform.set_smoothscale_backend(antigo)
    return {'backend_original':antigo,'zoom_saida':list(tamanho),
            'imagem_rgb':list(imagem.get_size()),'resultados':resultados}


def original(scene,target,variant,flip,x,frame,night,climate,phase):
    # Referencia extraida da _render_chunk original de pixelrush_city2_v3118.py.
    from pixelrush_city2_v3115 import WIDTH,SCENE_W,SCENE_H,SCALE
    tex=scene._scaled_surface(variant,'image')
    r=pygame.Rect(max(0,-x),0,min(SCENE_W,WIDTH-x)-max(0,-x),SCENE_H)
    if r.w>0:target.blit(tex,(max(0,x),0),r)
    for sp in variant.sprites:
        asset=scene.lib.assets.get(sp.kind)
        if asset is None:continue
        tex=asset.image;width=tex.get_width()
        wind=1.5 if climate in ('vento','tempestade','nevasca') else 1.
        dx=int(round(math.sin(frame*.025+sp.phase)*sp.sway*wind))
        px=x+sp.x*SCALE+dx
        if px>=WIDTH+2 or px+width<=-2:continue
        scene._draw_sprite(target,sp.kind,px,sp.y*SCALE,frame,night,climate,'image',False)


def mundo_2_5d():
    base=pygame.Surface((900,500),pygame.SRCALPHA)
    base.fill((0,0,0,0))
    for i in range(25):
        pygame.draw.rect(base,(30+i*5,120+i*3,190,140+i%5*20),
                         ((i*79)%850,(i*61)%460,45,39))
    sprite=pygame.Surface((25,26),pygame.SRCALPHA)
    pygame.draw.circle(sprite,(245,165,92,173),(12,13),12)
    conjunto=[SimpleNamespace(kind='marca',x=(i*83)%900,y=(i*13)%240,
                    phase=i*.31,sway=1.+i%5) for i in range(50)]
    variant=SimpleNamespace(sprites=conjunto)
    def cena():
        s=CityPilotScene.__new__(CityPilotScene)
        s.lib=SimpleNamespace(assets={'marca':SimpleNamespace(image=sprite)})
        s._scaled_surface=lambda variant,kind:base
        s._draw_sprite=lambda surf,kind,x,y,frame,night,climate,map_kind,flip:surf.blit(sprite,(x,y))
        return s
    def quadro(s,fun,frame):
        tela=pygame.Surface((450,500),pygame.SRCALPHA)
        for x in (-800,-250,200,650):
            fun(s,tela,variant,False,x,frame,.25,
                'vento' if frame%2 else 'limpo',.6)
        return tela
    velho=cena()
    novo=cena()
    iguais=True
    for frame in range(0,16):
        a=quadro(velho,original,frame)
        b=quadro(novo,lambda *args:args[0]._render_chunk(*args[1:]),frame)
        if pygame.image.tobytes(a,'RGBA')!=pygame.image.tobytes(b,'RGBA'):
            iguais=False;break
    med_old=cena(); med_new=cena()
    i_old=[0];i_new=[0]
    def ciclo_old():
        quadro(med_old,original,i_old[0]);i_old[0]+=1
    def ciclo_new():
        quadro(med_new,lambda *args:args[0]._render_chunk(*args[1:]),i_new[0]);i_new[0]+=1
    return {'pixels_iguais_16_quadros':iguais,
            'referencia':medir(ciclo_old,80,12),
            'cache_movimentos':medir(ciclo_new,80,12),
            'resultado_apenas_sintetico':True}


def executar():
    pygame.init();pygame.display.set_mode((450,800))
    try:
        vs,fs=shaders('GLES2',pygame.transform.get_smoothscale_backend(),(450,800))
        retorno={
            'schema':'pixelrush.qa.camera_world.benchmark.v327739',
            'ambiente':'Linux SDL dummy; nao Android real',
            'pygame':pygame.version.ver,
            'camera_smoothscale':camera(),
            'mundo_2_5d':mundo_2_5d(),
            'gpu':{
                'shader_gles2_sha256':hashlib.sha256((vs+fs).encode()).hexdigest(),
                'benchmark_real_android':False,
                'renderer_egl_real_android':None,
                'gpu_integracao_autorizada':gate_integracao(
                    {'igualdade_total':True,'ganho_estavel_fps_android':False,
                     'egl_android_aprovado':False,'sem_regressoes_saves_fisica':True},False),
                'observacao':'Shader mantido isolado; medir upload, GPU, EGL e swap em aparelho antes da integracao.',
            },
        }
        return retorno
    finally:
        pygame.quit()


if __name__=='__main__':
    doc=executar()
    destino=Path('qa-benchmark-camera-world-v327739.json')
    destino.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(doc,ensure_ascii=False,indent=2))
    if not doc['mundo_2_5d']['pixels_iguais_16_quadros'] or doc['gpu']['gpu_integracao_autorizada']:
        raise SystemExit('Falha de equivalencia ou gate GPU indevido')
