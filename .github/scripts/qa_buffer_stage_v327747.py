#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA 3.277.47 — identifica a PRIMEIRA fase que diverge no quinto quadro.

Compara dois renderizadores de fundo PROD e preserva RNG entre as fases.
NUNCA altera o jogo. A alternativa offscreen segue REPROVADA quando houver
qualquer divergencia RGBA; as duracoes sao exploratorias, nao FPS Android.
"""
import json, os, random, sys
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import pygame
from test_qa_buffer_full_v327746 import game_module, criar_contexto, overlay_por_quadro, rgba
from pixelrush_qa_ultraleve_v327730 import CacheFundoUltraQA

def first_diff(a,b):
    sa,sb=rgba(a),rgba(b)
    if sa==sb:
        return None
    for i in range(0,min(len(sa),len(sb)),4):
        if sa[i:i+4]!=sb[i:i+4]:
            return {'x':(i//4)%450,'y':(i//4)//450,
                    'rgba_ref':list(sa[i:i+4]),'rgba_alt':list(sb[i:i+4])}
    return {'motivo':'comprimento_diferente'}


def executar_bioma(game,bioma,frames=35):
    before_creation=random.getstate()
    bg,clima,cenas=criar_contexto(game,bioma,'limpo')
    after_creation=random.getstate()
    random.setstate(before_creation)
    alt,altclima,altcenas=criar_contexto(game,bioma,'limpo')
    random.setstate(after_creation)
    original=pygame.Surface((450,800)).convert()
    alternative=original.copy()
    scratch=original.copy()
    c1=CacheFundoUltraQA(periodo=5)
    c2=CacheFundoUltraQA(periodo=5)
    names=('parallax','profundidade_cinematografica','profundidade_bioma',
           'nuvens_clima','cenas_memoraveis','chao_hud')
    counts=dict.fromkeys(names,0)
    first=[]
    total_mismatch=0
    for i in range(frames):
        frame=19+i*11
        night=(0.,.3,.6,.95)[(i//5)%4]
        cor=(62+i%25,96+(i*2)%30,136)
        tipo={'cidade':('limpo','chuva','tempestade'),
              'neve':('limpo','nevasca','neve'),
              'deserto':('limpo','areia','tempestade_areia')}[bioma][(i//5)%3]
        clima.tipo=altclima.tipo=tipo
        clima.tempo=altclima.tempo=frame
        bg.clima_tipo=alt.clima_tipo=tipo
        state=random.getstate()
        bg.update(8.8)
        advanced=random.getstate()
        random.setstate(state)
        alt.update(8.8)
        random.setstate(advanced)
        for b in (bg,alt):
            b.peso_noite=night
            b.world.night=night
            b.world.climate=tipo
        key=(bioma,tipo,night>=.5,False,original.get_size())
        hit1=c1.reusar(original,key,True)
        hit2=c2.reusar(alternative,key,True)
        assert hit1==hit2,('ciclo_desigual',bioma,i)
        if not hit1:
            scratch.blit(alternative,(0,0))
            color1=clima.aplicar_ceu(cor)
            color2=altclima.aplicar_ceu(cor)
            steps=[
                ('parallax',
                 lambda d,b,c,e:b.draw(d,e,night>=.5),color1,color2),
                ('profundidade_cinematografica',
                 lambda d,b,c,e:game.profundidade_cinematografica(d,bioma,night,False),
                 None,None),
                ('profundidade_bioma',
                 lambda d,b,c,e:game.desenhar_profundidade_bioma(
                     d,bioma,b.world.travel,night,False,tipo),None,None),
                ('nuvens_clima',
                 lambda d,b,c,e:c._desenhar_nuvens_clima(d,e)
                    if tipo!='limpo' else None,color1,color2),
                ('cenas_memoraveis',
                 lambda d,b,c,e:e.desenhar(d,bioma,b.world.travel,
                                            frame,night,leve=False),
                 cenas,altcenas),
            ]
            frame_first=None
            for name,func,extra1,extra2 in steps:
                st=random.getstate()
                func(original,bg,clima,extra1)
                done=random.getstate()
                random.setstate(st)
                func(scratch,alt,altclima,extra2)
                random.setstate(done)
                mismatch=first_diff(original,scratch)
                if mismatch and frame_first is None:
                    frame_first=name
                    counts[name]+=1
                    if len(first)<16:
                        first.append({'frame':i,'fase':name,'clima':tipo,
                                      'noite':night,'pixel':mismatch})
            c1.guardar(original,key,True)
            c2.guardar(scratch,key,True)
            alternative.blit(scratch,(0,0))
        rng=random.getstate()
        overlay_por_quadro(game,original,bg,frame)
        done=random.getstate()
        random.setstate(rng)
        overlay_por_quadro(game,alternative,alt,frame)
        random.setstate(done)
        diff=first_diff(original,alternative)
        if diff:
            total_mismatch+=1
            if hit1 or not any(e['frame']==i for e in first):
                counts['chao_hud']+=1
                if len(first)<16:
                    first.append({'frame':i,'fase':'chao_hud','clima':tipo,
                                  'noite':night,'pixel':diff})
    return {'bioma':bioma,'frames':frames,'quadros_divergentes':total_mismatch,
            'primeiras_fases':counts,'exemplos':first,
            'alternativa_aprovada':False,'codigo_do_jogo_modificado':False,
            'fps_android_inferido':False}


def main():
    pygame.init()
    pygame.display.set_mode((450,800))
    game=game_module()
    report={'schema':'pixelrush.qa.buffer.stage.v327747',
            'versao':'v3.277.47-QA','modo':'diagnostico_nao_integrado',
            'resultados':{biome:executar_bioma(game,biome)
                          for biome in ('cidade','neve','deserto')},
            'android_testado':False,'apk_compilado':False,
            'render_original_preservado':True}
    pygame.quit()
    path=ROOT/'qa-buffer-stage-v327747.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    assert all(v['frames']==35 for v in report['resultados'].values())


if __name__=='__main__':
    main()
