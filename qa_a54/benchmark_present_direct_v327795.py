# -*- coding: utf-8 -*-
"""R25: benchmark do framebuffer SDL RGB direto, comparacao interprocessos."""
import argparse,hashlib,json,os,random,resource,statistics,sys,time
from collections import OrderedDict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
p=argparse.ArgumentParser()
p.add_argument('--candidate',type=int,choices=(0,1),required=True)
p.add_argument('--output',type=Path,required=True)
args=p.parse_args()
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ['PIXELRUSH_QA_R25_DIRECT_PRESENT']=str(args.candidate)
import pygame
pygame.init()
from src.pixelrush.performance.unified_post_v327750 import finalizar_quadro,diagnostico,restaurar_estatisticas_para_teste
def nop(*args):pass
cases=(
  ('rgb_900', (900,1600), (900,1600), (0,0),'rgb'),
  ('rgb_1080_letterbox',(1080,2400),(1080,1920),(0,240),'rgb'),
  ('rgb_360',(450,800),(360,640),(45,80),'rgb'),
  ('rgba_fallback',(900,1600),(900,1600),(0,0),'rgba'),
  ('colorkey_fallback',(450,800),(360,640),(45,80),'colorkey'),
  ('no_scale',(450,800),(450,800),(0,0),'rgb'),
)
hashes={}
p50={}
direct={}
frame_count=36
for name,canvas,outsize,pos,mode in cases:
    screen=pygame.display.set_mode(canvas)
    source=(pygame.Surface((450,800),pygame.SRCALPHA,32)
            if mode=='rgba' else pygame.Surface((450,800)).convert())
    rng=random.Random(20261105)
    source.fill((30,66,116,223) if mode=='rgba' else (30,66,116))
    for _ in range(180):
        pygame.draw.rect(source,(rng.randrange(256),rng.randrange(256),rng.randrange(256)),
                         (rng.randrange(450),rng.randrange(800),10,17))
    if mode=='colorkey':source.set_colorkey((1,2,3))
    surfaces=OrderedDict()
    restaurar_estatisticas_para_teste()
    samples=[]
    for frame in range(frame_count):
        screen.fill((18,35,58))
        pygame.draw.rect(source,(frame*31%256,frame*17%256,frame*53%256),
                         (frame*37%440,frame*29%780,9,12))
        t=time.perf_counter_ns()
        finalizar_quadro(source,screen,outsize,pos,surfaces,None,None,6.,False,False,nop,nop,nop)
        duration=(time.perf_counter_ns()-t)/1e6
        if frame>5:samples.append(duration)
        if frame in (0,1,2,5,10,15,20,25,30,35):
            hashes[name+':'+str(frame)]=hashlib.sha256(
                pygame.image.tobytes(screen,'RGBA')).hexdigest()
    p50[name]=round(statistics.median(samples),5)
    direct[name]=diagnostico()['escala_direta']
assert len(hashes)==60
result={'schema':'qa.r25.direct_present.v327795','candidate':bool(args.candidate),
        'rgba_hashes':hashes,'sample_count':len(hashes),'direct_counts':direct,
        'p50_ms':p50,'rss_max_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'android_tested':False}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,indent=2),encoding='utf8')
print('R25 apresentacao direta',result['direct_counts'],'p50',result['p50_ms'])
pygame.quit()
