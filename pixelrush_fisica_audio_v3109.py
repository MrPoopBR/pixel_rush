"""Pixel Rush v3.109 — geometria SDF colidível e reverberação convolucional real.

A mutação SDF só age em obstáculos existentes durante impulsos destrutivos.
A revisão da máscara também altera efetivamente o teste de colisão desses objetos.
Nenhuma parte deste módulo modifica a colisão do terreno permanente.
"""
import math
from collections import OrderedDict

import pygame


def esculpir_obstaculo(obj, x, y, raio=32):
    """Remove volume elíptico via signed distance da geometria E da colisão.

    Retorna True quando uma máscara residual existe, False quando foi esvaziada.
    Coordenadas em espaço de tela; a máscara acompanha o sprite até sair da cena.
    """
    import numpy as np
    if not hasattr(obj, 'image') or not hasattr(obj, 'rect'):
        return False
    imagem = obj.image.convert_alpha().copy()
    w, h = imagem.get_size()
    if min(w,h) <= 0:
        return False
    local_x = float(x - obj.rect.x)
    local_y = float(y - obj.rect.y)
    sy, sx = np.ogrid[:h, :w]
    # Função de distância assinada de elipse (sem unidade física).
    rx = max(8.0, float(raio))
    ry = max(7.0, float(raio)*.82)
    sdf = np.sqrt(((sx-local_x)/rx)**2 + ((sy-local_y)/ry)**2) - 1.0
    alpha = pygame.surfarray.pixels_alpha(imagem)
    original = alpha.copy()
    fator = np.clip(sdf * 5.0,0,1) * 255
    alpha[...] = (original * fator.T / 255.0).astype(np.uint8)
    del alpha
    mascara = pygame.mask.from_surface(imagem, 128)
    obj.image = imagem
    obj._mascara_sdf_v3109 = mascara
    obj._sdf_destruido_v3109 = True
    obj._sdf_atingido_v3109 = True
    return mascara.count() > 8


def colide_sdf_com_rect(obj, rect_jogador):
    """Colisão real pixel×rect para objeto mutado, inclusive cavidades."""
    mask = getattr(obj, '_mascara_sdf_v3109',None)
    if mask is None:
        return None
    if not rect_jogador.colliderect(obj.rect):
        return False
    # Jogador ainda usa hitbox retangular já reduzida pelo sistema original.
    jogador_mask = pygame.Mask((max(1,rect_jogador.w),max(1,rect_jogador.h)),fill=True)
    return mask.overlap(jogador_mask,(rect_jogador.x-obj.rect.x,rect_jogador.y-obj.rect.y)) is not None


class ReverbConvolucional:
    """Convolução estéreo por FFT com respostas ao impulso determinísticas.

    Sons curtos decorativos recebem reflexões iniciais por bioma e cauda suave.
    É reverberação convolucional real com IR sintético, não IR gravada em espaço real.
    Cache limitado mantém os sons prontos após primeiro uso.
    """
    PERFIS = {
        'cidade': (.20, (0.023,0.041,0.073), 0.24),
        'neve': (.31, (0.043,0.082,0.129),0.22),
        'deserto': (.36, (0.065,0.131,0.190),0.18),
        'vulcao': (.48, (0.062,0.151,0.257),0.28),
        'floresta': (.25, (0.044,0.098,0.164),0.27),
        'cidade_futurista': (.32, (0.030,0.066,0.129),0.25),
        'ilhas_celestes': (.54, (0.084,0.201,0.338),0.29),
    }

    def __init__(self,max_entries=20):
        self.cache=OrderedDict(); self.max_entries=max_entries

    def _impulse(self,bioma,rate):
        import numpy as np
        decay,reflections,mix=self.PERFIS.get(bioma,self.PERFIS['cidade'])
        n=max(2,int(rate*decay))
        ir=np.zeros((n,2),dtype=np.float32)
        ir[0,:]=1.0
        for i,rt in enumerate(reflections):
            sample=min(n-1,int(rt*rate))
            gain=.34/(i+1)
            ir[sample,0]+=gain*(.72 if i%2 else 1.)
            ir[min(n-1,sample+int(rate*.004)),1]+=gain*(1. if i%2 else .72)
        # Cauda difusa reprodutível; HPF físico não afirmado.
        rng=np.random.default_rng(8301 + int(decay*1000))
        noise=rng.normal(0,1,size=(n,2)).astype(np.float32)
        envelope=np.exp(-np.linspace(0,7,n,dtype=np.float32))
        ir+=noise*envelope[:,None]*.003
        return ir,mix

    def aplicar(self,som,bioma,oclusao=0.0):
        if som is None:
            return som
        try:
            import numpy as np
            mixer=pygame.mixer.get_init()
            if not mixer or mixer[1] != -16:return som
            key=(id(som),bioma,int(max(0.,min(1.,oclusao))*4))
            if key in self.cache:
                self.cache.move_to_end(key);return self.cache[key]
            arr=pygame.sndarray.array(som)
            if not arr.size:return som
            rate=mixer[0]
            signal=arr.astype(np.float32)/32768.
            mono = signal.ndim==1
            if mono:signal=np.stack((signal,signal),axis=1)
            if signal.shape[1]!=2:return som
            ir,mix=self._impulse(bioma,rate)
            n=signal.shape[0]+ir.shape[0]-1
            fft_size=1<<(n-1).bit_length()
            wet=np.fft.irfft(np.fft.rfft(signal,n=fft_size,axis=0)*np.fft.rfft(ir,n=fft_size,axis=0),n=fft_size,axis=0)[:n,:]
            result=wet*mix
            result[:len(signal),:]+=signal*(1-mix)
            result*=1.0-float(oclusao)*0.20
            max_amp=np.max(np.abs(result))
            if max_amp>0.98:result*=0.98/max_amp
            pcm=np.ascontiguousarray((np.clip(result,-1,1)*32767).astype(np.int16))
            if mono:pcm=pcm[:,0].copy()
            rendered=pygame.sndarray.make_sound(pcm)
            self.cache[key]=rendered
            while len(self.cache)>self.max_entries:self.cache.popitem(last=False)
            return rendered
        except (pygame.error,ValueError,RuntimeError,ImportError,TypeError):
            return som
