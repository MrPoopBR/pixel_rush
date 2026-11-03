# -*- coding: utf-8 -*-
"""QA 3.277.48: limpeza de caches frios parcelada APOS a apresentacao.

A cada 180 frames o QA antigo varria todos os mundos em um unico frame,
sempre multiplo do quinto quadro de redraw. Agora so sob pressao RSS o
trabalho e distribuido, maximo 12 entradas inspecionadas por apresentacao.
Nao toca estados/itens de gameplay e nunca remove caches do bioma ativo.
"""
from weakref import ref

class EscalonadorTrimQA:
    def __init__(self, limite_por_passo=12):
        self.limite_por_passo=max(1,min(64,int(limite_por_passo)))
        self._pendencias=None
        self._fonte=None
        self._mundos=None
        self.removidos=0
        self.passos=0
        self.concluidos=0
        self.falhas=0

    @property
    def ativo(self):
        return self._pendencias is not None

    def cancelar(self):
        self._pendencias=self._fonte=self._mundos=None

    def iniciar(self, mundos, fonte, rss, teto):
        """Nao agenda uma segunda varredura ate finalizar a atual."""
        if self.ativo or rss is None or rss<=teto:
            return False
        self._mundos=tuple(ref(w) for w in tuple(mundos))
        self._fonte=fonte
        self._pendencias=self._gerar_pendencias()
        self.removidos=0
        self.passos=0
        return True

    def _gerar_pendencias(self):
        for mundo_ref in self._mundos:
            world=mundo_ref()
            if world is None:
                continue
            # Nenhuma copia de Surface: apenas snapshots de chaves.
            for attr in ('props_cache','cache','fx_cache','normal_cache',
                         'material_cache','flow_cache','geometry_cache',
                         '_qa_mirror_props','_qa_deform_buffers','_city_surfaces'):
                cache=getattr(world,attr,None)
                if cache:
                    for key in tuple(cache):
                        yield (mundo_ref,attr,key)
            city=getattr(world,'city2',None)
            scaled=getattr(city,'_scaled',None)
            if scaled and world.biome!='cidade':
                # O LRU nunca cai abaixo das 8 entradas conservadas.
                for key in tuple(scaled):
                    yield (mundo_ref,'_city_scaled',key)
            # QA750: as 13 vinhetas noturnas 450x500 RGBA ocupavam
            # cerca de 11 MiB por Cidade. Sob RSS alto, conservar o
            # nivel atual e vizinhos; liberar somente texturas frias,
            # parcelado nos mesmos passos ja fora do quinto quadro.
            # QA753: enquanto Cidade inativa, as duas Surfaces de
            # scroll de 450x500 sao frias. Remover em lote no mesmo
            # escalonador de RSS, nunca no quinto quadro ou bioma ativo.
            if city is not None and world.biome!='cidade':
                from pixelrush_qa_incremental_scene_v327750 import tem_cache_cena
                if tem_cache_cena(city):
                    yield (mundo_ref,'_qa_city_incremental_cache',None)
            veils=getattr(city,'_night_veils',None)
            if veils and len(veils)>4:
                for key in tuple(veils):
                    yield (mundo_ref,'_city_night_veil',key)
        if self._fonte:
            for key in tuple(self._fonte):
                yield (None,'_SOURCE',key)

    def _aplicar(self, world_ref, attr, key):
        if attr=='_SOURCE':
            # Reavaliar biomas vivos a cada passo: mudancas de cena sao seguras.
            ativos={w().biome for w in self._mundos if w() is not None}
            if key not in ativos and key in self._fonte:
                self._fonte.pop(key,None)
                return True
            return False
        world=world_ref()
        if world is None:
            return False
        active=world.biome
        if attr=='_qa_city_incremental_cache':
            if active=='cidade':
                return False
            from pixelrush_qa_incremental_scene_v327750 import descartar_cena
            return bool(descartar_cena(getattr(world,'city2',None)))
        if attr=='_city_scaled':
            city=getattr(world,'city2',None)
            scaled=getattr(city,'_scaled',None)
            if active!='cidade' and scaled is not None and len(scaled)>8:
                if key in scaled:
                    scaled.pop(key,None)
                    return True
            return False
        if attr=='_city_night_veil':
            city=getattr(world,'city2',None)
            veils=getattr(city,'_night_veils',None)
            if veils is None or key not in veils or len(veils)<=4:
                return False
            # Nunca descartar o nivel ativo nem transicoes imediatas
            # da cidade atual, para nao provocar frame5 de recompilacao.
            if active=='cidade':
                current=max(0,min(12,int(getattr(world,'night',0.)*12+.5)))
                if isinstance(key,int) and abs(key-current)<=1:
                    return False
            veils.pop(key,None)
            return True
        cache=getattr(world,attr,None)
        if cache is None or key not in cache:
            return False
        if attr=='_city_surfaces':
            frio=isinstance(key,tuple) and key and key[0] in (
                'geometry','flow','material','normal','fxmask')
            # QA751: se uma pospassagem ainda consome este mapa, desalocar
            # sob pressao provocaria outra Surface de 450x500 no frame seguinte.
            # Ausencia de marcador mantém semantica legada de limpeza.
            ultimo=getattr(world,'_qa_surface_last_used',{}).get(key)
            if frio and ultimo is not None:
                biome_uso,frame_uso=ultimo
                frame_atual=getattr(world,'frame',frame_uso)
                frio=(biome_uso!=active or frame_atual-frame_uso>180)
        elif attr in ('_qa_mirror_props','_qa_deform_buffers'):
            frio=isinstance(key,tuple) and key and key[0]!=active
        elif attr=='props_cache':
            frio=isinstance(key,tuple) and key and key[0]!=active
        else:
            frio=key!=active
        if frio:
            cache.pop(key,None)
            return True
        return False

    def passo(self):
        """Processa no maximo N chaves; excecao cancela e permite fallback."""
        if not self.ativo:
            return False
        try:
            for _ in range(self.limite_por_passo):
                try:
                    item=next(self._pendencias)
                except StopIteration:
                    self.concluidos+=1
                    self.cancelar()
                    return False
                self.removidos+=int(self._aplicar(*item))
            self.passos+=1
            return True
        except Exception:
            self.falhas+=1
            self.cancelar()
            raise

    def diagnostico(self):
        return {'ativo':self.ativo,'limite_chaves_por_frame':self.limite_por_passo,
                'removidos_ultima_varredura':self.removidos,
                'passos_ultima_varredura':self.passos,
                'varreduras_concluidas':self.concluidos,'falhas':self.falhas}
