"""Pixel Rush 3.110 - stems sintéticos PCM sample-aligned, renderizados uma vez.

As quatro faixas usam EXATAMENTE N amostras e grade de 120 BPM. São sons
sintéticos, não gravações de estúdio; pygame.mixer não garante início de canais
com precisão de uma amostra. Não reiniciar em mudanças climáticas.
"""
import math
from functools import lru_cache

NOTE = (65.406, 65.406, 73.416, 82.407, 55.0, 55.0, 61.735, 65.406)

@lru_cache(maxsize=2)
def render_stems(rate=22050):
    import numpy as np
    beats=8; bpm=120
    n=int(rate*beats*60/bpm)
    t=np.arange(n,dtype=np.float64)/rate
    beat=np.minimum(beats-1,(t*.5**-1).astype(np.int32))
    u=(t*2.0)%1.0
    freqs=np.array(NOTE,dtype=np.float64)[beat]
    # Bass: oscillator contínuo e envelope por batida, sem resampling.
    bass=(np.sin(2*np.pi*freqs*t)*.65+np.sin(2*np.pi*freqs*2*t)*.16)
    bass*=np.minimum(1.,u*24.)*np.exp(-u*2.0)*.20
    # Pad: acordes quartais com movimento lento estéreo.
    chord=np.array((261.63,329.63,392.0,440.0),dtype=np.float64)
    pad=np.zeros_like(t)
    for f in chord:
        pad+=(np.sin(2*np.pi*f*t+.3*np.sin(2*np.pi*.21*t)) /len(chord))
    pad*=.17*(.68+.32*np.sin(2*np.pi*.125*t)**2)
    # Drums/hat: impulsos de kick, snare e ruído determinístico.
    rng=np.random.default_rng(3110)
    kick=(np.sin(2*np.pi*(68-27*u)*t)*np.exp(-u*17.) * (u<.30))*.22
    snare_u=(u+.5)%1.0
    noise=rng.standard_normal(n)*.075
    snare=noise*np.exp(-snare_u*35.)*(snare_u<.23)
    drums=kick+snare
    melody_notes=np.array((523.25,587.33,659.25,783.99,659.25,587.33,523.25,440.),dtype=np.float64)
    mel=(np.sin(2*np.pi*melody_notes[beat]*t)+.16*np.sin(2*np.pi*melody_notes[beat]*2*t))
    mel*=.14*np.exp(-u*2.5)*np.minimum(1.,u*24)
    fade=min(160,n//16)
    if fade:
        ramp=np.linspace(0,1,fade,endpoint=False)
    results=[]
    for idx,sig in enumerate((bass,pad,drums,mel)):
        sig=np.tanh(sig)
        if fade:
            # Bordas do loop suaves: menor clique no reinício.
            sig[:fade]*=ramp
            sig[-fade:]*=ramp[::-1]
        pan=(.04,.28,0.0,-.22)[idx]
        pcm=np.stack((sig*(1-pan),sig*(1+pan)),axis=1)
        pcm=np.int16(np.clip(pcm,-.98,.98)*32767)
        results.append(np.ascontiguousarray(pcm))
    assert len({p.shape for p in results})==1
    return tuple(results)

def criar_stems_pygame():
    import pygame
    config=pygame.mixer.get_init()
    if not config or config[1]!=-16 or config[2]!=2:return (None,)*4
    try:
        return tuple(pygame.sndarray.make_sound(s) for s in render_stems(int(config[0])))
    except (ImportError,ValueError,pygame.error):
        return (None,)*4

if __name__=='__main__':
    import sys,wave
    stem=render_stems()[0]
    with wave.open(sys.argv[1],'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(22050);f.writeframes(stem.tobytes())
