# -*- coding: utf-8 -*-
"""QA794: replay visual real, 180 amostras, controle/candidato RGBA."""
import argparse,hashlib,json,os,random,resource,statistics,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
a=argparse.ArgumentParser()
a.add_argument('--candidate',type=int,choices=(0,1),required=True)
a.add_argument('--output',type=Path,required=True)
opts=a.parse_args()
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ['PIXELRUSH_QA_R24_REPLAY_RECYCLE']=str(opts.candidate)
import pygame
pygame.init()
pygame.display.set_mode((450,800))
from pixelrush_extras_v3174 import ReplayCinematografico
replay=ReplayCinematografico()
source=pygame.Surface((450,800)).convert()
assert source.get_bitsize()==32
times=[]
hashes={}
for n in range(1,181):
    source.fill(((n*11)%256,(n*7)%256,(n*19)%256))
    pygame.draw.rect(source,((n*31)%256,(n*17)%256,(n*3)%256),
                     (n*13%440,n*19%780,33,42))
    t=time.perf_counter_ns()
    replay.capturar(source,n*5)
    ms=(time.perf_counter_ns()-t)/1e6
    if n>=73:times.append(ms)
    if n in (72,73,120,180):
        hashes[str(n)]=[hashlib.sha256(pygame.image.tobytes(x,'RGBA')).hexdigest()
                        for x in replay.buffer]
assert len(replay.buffer)==72
# Congelar nao pode modificar um buffer de replay.
replay.iniciar()
last=hashlib.sha256(pygame.image.tobytes(replay.buffer[0],'RGBA')).hexdigest()
replay.capturar(source,1000)
assert hashlib.sha256(pygame.image.tobytes(replay.buffer[0],'RGBA')).hexdigest()==last
assert len(replay.buffer)==72
v=sorted(times)
report={'schema':'qa.r24.replay_pool.1','candidate':bool(opts.candidate),
        'reuses':replay._r24_reutilizacoes,'rgba_hashes':hashes,'snapshots':len(hashes),
        'samples':180,'cached':len(replay.buffer),
        'p50_ms':round(statistics.median(v),5),
        'p95_ms':round(v[int(.95*(len(v)-1))],5),
        'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'android_verified':False}
opts.output.parent.mkdir(parents=True,exist_ok=True)
opts.output.write_text(json.dumps(report,indent=2),encoding='utf8')
print('R24 replay amostras',len(replay.buffer),
      'reutilizacoes',replay._r24_reutilizacoes,'p50',report['p50_ms'],
      'p95',report['p95_ms'])
pygame.quit()
