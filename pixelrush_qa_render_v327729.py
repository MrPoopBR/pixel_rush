# -*- coding: utf-8 -*-
"""QA v3.277.29: eliminacao de limpeza redundante do compositor 2.5D.

Cada render_scene nao-foreground ja limpa integralmente o buffer antes de desenhar
o primeiro pixel. A antiga _city_surface fazia OUTRO fill de 450 x 500 pixels
imediatamente antes. A eliminacao nao pula camadas nem altera sua ordem.
Foregound permanece com o caminho original, sem risco a mapas com transparencia.
Compatibilidade testada com SDL dummy pixel a pixel, multiplos canais e cenas.
"""
import pygame
import os
from weakref import ref

# QA752: alias zero-copy apenas quando World possui a Surface destino.
# OFF ate testes integrais de ambient_occlusion, multiinstancia e GPU.
_QA_BORROW_GEOMETRY=os.environ.get('PIXELRUSH_QA_GEOMETRY_BORROW','1')=='1'
# Fechamento #2/#10: um mesmo canal técnico pode ser solicitado diversas
# vezes no MESMO frame (GPU/oclusão/reflexos). O cache é por LivingWorld,
# condicionado ao estado completo, instância, Surface e qualidade. Imagem
# principal/FG continuam sempre desenhados. Desligue para rollback.
_QA_TECH_SAME_FRAME=os.environ.get('PIXELRUSH_QA_TECH_SAME_FRAME','1')=='1'
_QA_TECH_KINDS=frozenset(('geometry','normal','material','flow','fxmask'))
_QA_TECH_STATS={'consultas':0,'hits':0,'renders':0,'invalidados':0}


_INSTALADO = False
_ORIGINAL = None


def preparar_perfil_qa_android():
    """QA779: conectar as aceleracoes JA existentes no jogo Android QA.

    A configuracao opt-in por variavel individual tem precedencia. Um driver
    sem GLES3 ou sem biblioteca nativa deve cair no SDL/pygame, nunca impedir
    o carregamento, nem afetar a branch main, DEV ou AAB.
    """
    import sys
    if os.environ.get('PIXELRUSH_QA_ANDROID') != '1':
        return False
    if sys.platform != 'android' and 'ANDROID_ARGUMENT' not in os.environ:
        return False
    if os.environ.get('PIXELRUSH_QA_ACCEL_PROFILE','agressivo') != 'agressivo':
        return False
    for nome,valor in (
            ('PIXELRUSH_QA_GLES_BRIDGE','1'),
            ('PIXELRUSH_QA_GPU_ZOOM','1'),
            ('PIXELRUSH_QA_GLES3_CONTEXT','1'),
            ('PIXELRUSH_QA_GLES_PBO','1'),
            ('PIXELRUSH_QA_CAMERA_AUTOTUNE','1'),
            ('PIXELRUSH_QA_NATIVE_AUTO','1'),
            ('PIXELRUSH_QA_CITY_INCREMENTAL','1'),
            ('PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW','1'),
            ('PIXELRUSH_QA_CITY_TECH_COVER','1'),
            ('PIXELRUSH_QA_CLASSIC_INCREMENTAL','1'),
            ('PIXELRUSH_QA_TRACE','1')):
        os.environ.setdefault(nome,valor)
    return True


def instalar():
    global _INSTALADO, _ORIGINAL
    if _INSTALADO:
        return
    # Antes dos imports QA: cada modulo captura as flags no boot.
    preparar_perfil_qa_android()
    from pixelrush_world_v3130 import LivingWorld
    _ORIGINAL = LivingWorld._city_surface

    def _city_surface_qa(self, kind='image', foreground_only=False):
        if foreground_only:
            return _ORIGINAL(self, kind, foreground_only)
        chave = (kind, False)
        surf = self._city_surfaces.get(chave)
        if surf is None:
            from pixelrush_world_v3130 import WIDTH, GROUND, TOP
            surf = pygame.Surface((WIDTH, GROUND - TOP), pygame.SRCALPHA)
            self._city_surfaces[chave] = surf
        # render_scene executa fill completo para cada kind, inclusive image.
        from pixelrush_world_v3130 import MODULAR_BIOMES
        cena = self._get_modular() if self.biome in MODULAR_BIOMES else self.city2
        # O world retorna essas Surfaces exclusivamente para leitura/SDL.
        # Nunca reutilizar em outro frame, bioma, scene ou mutação de
        # parâmetros. Isto evita recompor o mesmo mapa várias vezes
        # no frame5, sem nenhum copy/blit adicional de 450x500.
        assinatura=None
        if _QA_TECH_SAME_FRAME and kind in _QA_TECH_KINDS:
            assinatura=(kind,self.biome,self.frame,self.travel,self.night,
                        self.climate,self.phase,bool(self.lightweight),
                        getattr(cena,'visual_quality',None))
            _QA_TECH_STATS['consultas']+=1
            estados=getattr(self,'_qa_technical_frame_states',None)
            registro=estados.get(kind) if estados is not None else None
            if (registro is not None and registro[0]==assinatura and
                    registro[1]() is cena and registro[2]() is surf):
                _QA_TECH_STATS['hits']+=1
                return surf
            if registro is not None:
                _QA_TECH_STATS['invalidados']+=1
        # A instrumentacao interna confirma onde o mundo 2.5D gasta CPU.
        from pixelrush_profiler_v3204 import sub_inicio, sub_fim
        sub_inicio('mundo_composicao_interna')
        emprestimo=(_QA_BORROW_GEOMETRY and kind=='geometry' and
                    self._city_surfaces.get(chave) is surf and
                    callable(getattr(cena,'ambient_occlusion',None)))
        if emprestimo:
            # O mesmo mundo mantem a Surface viva em _city_surfaces.
            # Nao emprestar destinos de testes externos ou efemeros.
            cena._qa_geometry_borrow_target=surf
        try:
            cena.render_scene(surf, self.travel, self.frame, self.night,
                              self.climate, self.phase, foreground_only=False,
                              map_kind=kind)
        finally:
            if emprestimo:
                cena._qa_geometry_borrow_target=None
            sub_fim()
        if assinatura is not None:
            estados=getattr(self,'_qa_technical_frame_states',None)
            if estados is None:
                estados={}
                self._qa_technical_frame_states=estados
            # Weakrefs impedem manter cenas e buffers de biomas
            # aposentados vivos por causa do cache QA.
            estados[kind]=(assinatura,ref(cena),ref(surf))
            _QA_TECH_STATS['renders']+=1
        # QA751: mapa nao-image pode estar em uso pela GPU real neste frame.
        # Guardar apenas biome/frame (nunca Surface extra) para o trim RSS
        # impedir desalocacoes/recriacao do mesmo mapa sob pressao.
        if kind!='image':
            usados=getattr(self,'_qa_surface_last_used',None)
            if usados is None:
                usados={}
                self._qa_surface_last_used=usados
            usados[chave]=(self.biome,self.frame)
        return surf

    LivingWorld._city_surface = _city_surface_qa
    # Otimizacao QA isolada: blits das camadas de profundidade com recorte alfa.
    from pixelrush_qa_alpha_blit_v327731 import instalar as instalar_alpha_blit_qa
    instalar_alpha_blit_qa()
    # v3.277.33 QA: cache de nuvens sem perda de pixels e instrumentacao
    # das camadas visuais de verdade usadas nos sete biomas.
    from pixelrush_qa_scene_v327733 import instalar as instalar_cenario_qa
    instalar_cenario_qa()
    # Seleciona SIMD alternativo APENAS se mais rapido e RGB identico.
    # Sem backend seguro: mantem smoothscale nativo original.
    from pixelrush_qa_camera_v327733 import instalar as instalar_camera_qa
    instalar_camera_qa()
    # C/NEON usa a camera original ate provar igualdade e ganho no frame real.
    from pixelrush_qa_camera_native_auto_v327742 import instalar as instalar_camera_native_qa
    instalar_camera_native_qa()
    # QA753: skips pixel-inertes FG da Cidade (validacao por instancia) e
    # lista temporaria de blits quando faixa SDL exige so uma copia.
    # Instalar ANTES do scroll opt-in para preservar ordem de wrappers.
    # QA759: v3122 nao chama __init__ do v3118 que fornece os metadados
    # usados pelo render herdado. Instalar ANTES do wrapper de hotpath,
    # somente no QA, sem trocar a arte ja preparada.
    from pixelrush_qa_city_bootstrap_v327759 import instalar as instalar_city_bootstrap_qa
    instalar_city_bootstrap_qa()
    # QA785: 20 slots para o hotset de mapas do quinto quadro, sem mexer
    # na arte nem na politica de eviccao ou memoria dos outros biomas.
    from pixelrush_qa_city_scaled_budget_v327785 import instalar as instalar_city_budget_qa
    instalar_city_budget_qa()
    from pixelrush_qa_hotpath_v327753 import instalar as instalar_hotpath_qa
    instalar_hotpath_qa()
    # Scroll incremental 2.5D so liga quando o frame COMPLETO vence
    # o blit direto e 16 comparacoes de pixels sao idênticas.
    from pixelrush_qa_scroll_auto_v327742 import instalar as instalar_scroll_qa
    instalar_scroll_qa()
    # v3.277.50: scroll incremental pixel-preservado de chunks sem sprites
    # e strips classicos; opt-in ate gate final RGBA/CPU no aparelho.
    from pixelrush_qa_incremental_scene_v327750 import instalar as instalar_incremental_qa
    instalar_incremental_qa()
    # QA786: remover apenas far/mid COMPLETAMENTE encobertos nos mapas
    # opacos normal/flow, depois de gate RGBA de todos os atlases near.
    # Nao alterar imagem/sprites/iluminacao nem o cache QA785.
    from pixelrush_qa_city_opaque_overdraw_v327786 import instalar as instalar_city_opaque_qa
    instalar_city_opaque_qa()
    # QA787: culling do quinto quadro (geometry/material e fxmask) validado
    # por RGBA no mundo real. Capturar DEPOIS de QA786, restaurar antes.
    from pixelrush_qa_city_technical_cover_v327787 import instalar as instalar_city_technical_qa
    instalar_city_technical_qa()
    # v3.277.44: batching nas classes v3128/v3130 do mundo REAL,
    # desativado por padrao ate prova de ganho Android.
    from pixelrush_qa_modular_batch_v327744 import instalar as instalar_modular_batch_qa
    instalar_modular_batch_qa()
    # v3.277.49: otimizacoes do compositor/Cidade efetivamente usado.
    # O plano de tiles e util para multipass image/normal/geometry; a
    # atmosfera/reflexos atuam no caminho real do render de cidade.
    from pixelrush_qa_city_tiles_v327749 import instalar as instalar_city_tiles_qa
    instalar_city_tiles_qa()
    from pixelrush_qa_city_weather_v327749 import instalar as instalar_city_weather_qa
    instalar_city_weather_qa()
    # QA749: ponte GLES pode receber a Surface CPU do jogo como textura,
    # preservando HUD/input. Nao instala sem flag experimental explicita.
    # Antes do wrapper de flip da telemetria, para medi-lo corretamente.
    from pixelrush_qa_gles_bridge_v327749 import instalar as instalar_gles_bridge_qa
    instalar_gles_bridge_qa()
    # QA v3.277.42: pool meteorologico, limite de cache e Perfetto opcionais;
    # sempre reaproveita o compositor e a camera originais.
    from pixelrush_qa_performance_integrated_v327742 import instalar as instalar_perf_qa
    instalar_perf_qa()
    # QA v3.277.47: aquece somente paginas dos atlas SHA fora do jogo,
    # sem instanciar cenas SDL, sem alterar sorteio, RAM do processo nem
    # o periodo original 5:1. Fallback em qualquer falha de leitura.
    from pixelrush_qa_atlas_io_v327747 import instalar_no_boot_qa
    instalar_no_boot_qa()
    # GC cooperativo instalado DEPOIS dos wrappers de flip de telemetria;
    # nenhum collect() pode coincidir com o quinto quadro 5:1.
    from pixelrush_qa_gc_cooperativo_v327757 import instalar as instalar_gc_qa
    instalar_gc_qa()
    # QA761: após World.switch, liberar alias geometry da cena anterior
    # somente se apontar para buffer que o World acabou de aposentar.
    from pixelrush_qa_geometry_retire_v327761 import instalar as instalar_geometry_retire_qa
    instalar_geometry_retire_qa()
    # QA773: reuso do replay circular, pixel-exato com rollback.
    from pixelrush_qa_replay_pool_v327773 import instalar as instalar_replay_qa
    instalar_replay_qa()
    # R11/A54: instrumentar DEPOIS de todos os wrappers preexistentes.
    # Somente QA Android; sem mudanca de shader, biome, tela ou jogo.
    if os.environ.get('PIXELRUSH_QA_ANDROID') == '1':
        from pixelrush_qa_r11_passes_v327776 import instalar as instalar_r11_passes
        instalar_r11_passes()
    _INSTALADO = True


def restaurar_para_teste():
    """Somente em regressao offline, nunca executado no APK."""
    global _INSTALADO
    if _INSTALADO:
        # Remover primeiro wrappers externos R11, preservando hooks anteriores.
        from pixelrush_qa_r11_passes_v327776 import restaurar_para_teste as restaurar_r11_passes
        restaurar_r11_passes()
        from pixelrush_qa_gc_cooperativo_v327757 import restaurar_para_teste as restaurar_gc_qa
        restaurar_gc_qa()
        from pixelrush_qa_geometry_retire_v327761 import restaurar_para_teste as restaurar_geometry_retire_qa
        restaurar_geometry_retire_qa()
        from pixelrush_world_v3130 import LivingWorld
        LivingWorld._city_surface = _ORIGINAL
        from pixelrush_qa_city_technical_cover_v327787 import restaurar_para_teste as restaurar_city_technical_qa
        restaurar_city_technical_qa()
        from pixelrush_qa_city_opaque_overdraw_v327786 import restaurar_para_teste as restaurar_city_opaque_qa
        restaurar_city_opaque_qa()
        from pixelrush_qa_incremental_scene_v327750 import restaurar_para_teste as restaurar_incremental
        restaurar_incremental()
        from pixelrush_qa_hotpath_v327753 import restaurar_para_teste as restaurar_hotpath
        restaurar_hotpath()
        from pixelrush_qa_city_scaled_budget_v327785 import restaurar_para_teste as restaurar_city_budget_qa
        restaurar_city_budget_qa()
        from pixelrush_qa_city_bootstrap_v327759 import restaurar_para_teste as restaurar_city_bootstrap_qa
        restaurar_city_bootstrap_qa()
        from pixelrush_qa_scroll_auto_v327742 import restaurar_para_teste as restaurar_scroll
        restaurar_scroll()
        from pixelrush_qa_city_tiles_v327749 import restaurar_para_teste as restaurar_tiles
        from pixelrush_qa_city_weather_v327749 import restaurar_para_teste as restaurar_clima
        restaurar_tiles()
        restaurar_clima()
        from pixelrush_qa_replay_pool_v327773 import restaurar_para_teste as restaurar_replay_qa
        restaurar_replay_qa()
        from pixelrush_qa_gles_bridge_v327749 import restaurar_para_teste as restaurar_bridge
        restaurar_bridge()
        _INSTALADO = False
