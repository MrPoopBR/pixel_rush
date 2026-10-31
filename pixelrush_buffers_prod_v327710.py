"""v3.277.10-PROD — gerenciamento de memória da preparação incremental.

O processamento SDL permanece no thread principal. Retém unicamente os estados
compactados das alternativas inativas e descarta cada buffer depois de usá-lo.
O som, a geometria, shaders e a conversão convert_alpha() ficam inalterados.
A entrada temporaria usa frombuffer para evitar copia RGBA antes da conversao.
Não altera a ordem nem os tempos da escolha de cenários.
"""
from collections import deque
import hashlib
import ctypes
import gc
import io
import pickle
import threading
import time
import zlib
import json
from pathlib import Path

import pygame
import pixelrush_atlas_prod_v32776 as atlas
import pixelrush_world_v3185 as motor
import pixelrush_world_prod_v32777 as world_module

_BIOMAS = ('neve','deserto','cidade_futurista')
_DIR = Path(__file__).resolve().parent / 'assets' / 'buffers_prod_v32779'
try:
    _MANIFESTO = json.loads((_DIR / 'manifest.json').read_text(encoding='utf8'))
except (OSError, ValueError):
    _MANIFESTO = {}  # Instalação parcial: usar o carregador original do jogo.

# Os .pbuf existentes foram serializados com esta classe do módulo original.
# Usar a mesma identidade mantém todos os recursos byte a byte.
from pixelrush_buffers_prod_v32779 import _Buffer

class _Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'pixelrush_atlas_prod_v32776' and name == '_restore_surface':
            return _Buffer
        return super().find_class(module, name)

def _walk_buffers(obj):
    seen=set();seen_containers=set();res=[]
    def visit(o):
        if isinstance(o,_Buffer):
            if id(o) not in seen:
                res.append(o);seen.add(id(o))
        elif isinstance(o,(dict,list,tuple,set)):
            if id(o) in seen_containers:return
            seen_containers.add(id(o))
            if isinstance(o,dict):
                for k,v in o.items():visit(k);visit(v)
            else:
                for v in o:visit(v)
    visit(obj)
    return res

def _replace(obj):
    visited={}
    def go(o):
        if isinstance(o,_Buffer):
            assert o.surface is not None
            return o.surface
        if isinstance(o,(str,bytes,int,float,bool,type(None),pygame.Surface)):
            return o
        oid=id(o)
        if oid in visited:return visited[oid]
        if isinstance(o,dict):
            visited[oid]=o
            for k,v in list(o.items()):
                nk,nv=go(k),go(v)
                if nk is not k:del o[k]
                o[nk]=nv
            return o
        if isinstance(o,list):
            visited[oid]=o
            for i,v in enumerate(o):o[i]=go(v)
            return o
        if isinstance(o,tuple):
            new=tuple(go(v) for v in o);visited[oid]=new;return new
        if isinstance(o,set):
            new={go(v) for v in o};visited[oid]=new;return new
        return o
    return go(obj)

class _Manager:
    def __init__(self):
        self._lock=threading.Lock()
        self._event=threading.Event()
        self._todo=deque()
        self._requested=set()
        self._ready={}
        self._quality=None
        self._progress={}
        # Reuso controlado: preparar somente a primeira visita por bioma/qualidade.
        # Nas revisitas os atlas originais ja foram aquecidos; reconstruir caches
        # aqui aloca centenas de MB em arenas nativas sem ganho de fluidez.
        self._visited=set()
        self._cursor=0
        self._fraction=0.38
        self._ticks_since_trim=0
        try:
            # O descarte de Surface libera referências, mas o alocador nativo
            # pode guardar as páginas e fazer o RSS subir a cada revisita.
            # Chamada oportunista: disponível no glibc; ausente -> não faz nada.
            self._trim=getattr(ctypes.CDLL(None), 'malloc_trim', None)
            if self._trim is not None:
                self._trim.argtypes=[ctypes.c_size_t]
                self._trim.restype=ctypes.c_int
        except (OSError, AttributeError):
            self._trim=None
        self._epoch=0
        self._thread=threading.Thread(target=self._worker,name='pixelrush-atlas-buffers',daemon=True)
        self.stats={'loaded':[],'used':[],'fallback':[],'activation_ms':[],'max_buffer_mib':0}
        self._thread.start()

    def _worker(self):
        while True:
            self._event.wait(0.2)
            self._event.clear()
            while True:
                with self._lock:
                    if not self._todo:break
                    key,epoch=self._todo.popleft()
                try:
                    path=_DIR/(key+'.pbuf')
                    with path.open('rb') as file:
                        if hashlib.file_digest(file,'sha256').hexdigest()!=_MANIFESTO[key]['sha256']:
                            raise ValueError('buffers preparados não íntegros')
                        file.seek(0)
                        state,buffers,used_bytes=pickle.load(file)
                    if state.get('biome') != key.removesuffix('_lite'):
                        raise ValueError('bioma divergente')
                    if len(buffers)!=_MANIFESTO[key]['count']:
                        raise ValueError('quantidade de superfícies divergente')
                    stage=(state,buffers,used_bytes)
                except Exception:
                    stage=None
                with self._lock:
                    self._requested.discard((key,epoch))
                    if self._epoch==epoch and stage is not None:
                        self._ready[key]=stage
                        self.stats['loaded'].append(key)
                        self.stats['max_buffer_mib']=max(self.stats['max_buffer_mib'],sum(x[2] for x in self._ready.values())/1048576)
                # A thread não mantém o último estado já entregue em variáveis locais.
                stage=state=buffers=used_bytes=None

    def reclaim_idle(self):
        self._ticks_since_trim+=1
        if self._ticks_since_trim % 150 == 0:
            # Coleção apenas da geração jovem (sem uma pausa GC integral).
            gc.collect(0)
            if self._trim is not None:
                self._trim(0)

    def update(self,light,biome):
        if self._quality!=light:
            with self._lock:
                self._quality=light;self._epoch+=1
                self._todo.clear();self._requested.clear();self._ready.clear();self._progress.clear()
        with self._lock:
            novo_pedido=False
            for name in _BIOMAS:
                key=name+('_lite' if light else '')
                if (name!=biome and key not in self._visited and key not in self._ready
                        and (key,self._epoch) not in self._requested):
                    self._requested.add((key,self._epoch))
                    self._todo.append((key,self._epoch))
                    novo_pedido=True
            # Acordar a thread apenas quando surgirem pedidos novos.
            # O sinal anterior, a cada tick de simulacao, causava wakeups
            # mesmo quando os atlas ja estavam preparados.
            if novo_pedido:
                self._event.set()
            if not self._ready:
                return
            # Um buffer compactado existe para cada superfície ainda não pronta.
            # Prepara apenas parte das três opções para limitar RAM.
            candidates=[(name, self._ready.get(name)) for name in (
                b+('_lite' if light else '') for b in _BIOMAS if b!=biome)]
        start=time.perf_counter_ns()
        for shift in range(len(candidates)):
            key,stage=candidates[(self._cursor+shift)%len(candidates)]
            if stage is None:continue
            buffers=stage[1]
            desired=int(len(buffers)*self._fraction + 0.999)
            index=self._progress.get(key,0)
            if index>=desired:continue
            slot=buffers[index]
            raw=zlib.decompress(slot.raw)
            slot.surface=pygame.image.frombuffer(raw,slot.size,'RGBA').convert_alpha()
            slot.raw=None
            self._progress[key]=index+1
            self._cursor+=1
            # No máximo uma superfície por atualização; inclui overhead SDL.
            self.stats['max_buffer_mib']=max(self.stats['max_buffer_mib'],sum(x[2] for x in self._ready.values())/1048576)
            break

    def get(self,biome,light):
        key=biome+('_lite' if light else '')
        with self._lock:
            stage=self._ready.pop(key,None)
            self._progress.pop(key,None)
            self._visited.add(key)
        if stage is None:
            self.stats['fallback'].append(key)
            return None
        start=time.perf_counter_ns()
        try:
            state,buffers,_=stage
            for slot in buffers:
                if slot.surface is not None:continue
                raw=zlib.decompress(slot.raw)
                # Exatamente o mesmo resultado do _restore_surface original.
                slot.surface=pygame.image.frombuffer(raw,slot.size,'RGBA').convert_alpha()
                slot.raw=None
            state=_replace(state)
            instance=atlas.ModularBiomeScene.__new__(atlas.ModularBiomeScene)
            lampas=state.pop('_lampas_indexadas_v32776',())
            instance.__dict__.update(state)
            if biome=='cidade_futurista':instance._build_global_overlays()
            if biome=='deserto':
                instance._lamp_pixels={id(instance._poses[p][layer][i]):points for p,layer,i,points in lampas}
            return instance
        except (ValueError, TypeError, KeyError, IndexError, zlib.error, pygame.error):
            # Pacote incompleto: o chamador usa o atlas original, validado por SHA.
            return None
        finally:
            self.stats['activation_ms'].append((key,round((time.perf_counter_ns()-start)/1e6,3)))

_mgr=None
def instalar():
    global _mgr
    if _mgr is not None:return _mgr
    _mgr=_Manager()
    old_update=world_module.LivingWorld.update
    old_scene=motor.ModularBiomeScene
    def update(self,*a,**k):
        _mgr.update(bool(self.lightweight),self.biome)
        return old_update(self,*a,**k)
    def load_scene(biome,lightweight=False):
        if biome in _BIOMAS:
            got=_mgr.get(biome,lightweight)
            if got is not None:return got
        return old_scene(biome,lightweight=lightweight)
    world_module.LivingWorld.update=update
    motor.ModularBiomeScene=load_scene
    # Reivindicar páginas apenas após o desenho, sem competir com a criação
    # das superfícies durante LivingWorld.update().
    old_flip=pygame.display.flip
    def flip():
        _mgr.reclaim_idle()
        return old_flip()
    pygame.display.flip=flip
    return _mgr
