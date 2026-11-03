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

# QA752: alias zero-copy apenas quando World possui a Surface destino.
# OFF ate testes integrais de ambient_occlusion, multiinstancia e GPU.
_QA_BORROW_GEOMETRY=os.environ.get('PIXELRUSH_QA_GEOMETRY_BORROW','0')=='1'

_INSTALADO = False
_ORIGINAL = None


def instalar():
    global _INSTALADO, _ORIGINAL
    if _INSTALADO:
        return
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
        # A instrumentacao interna confirma onde o mundo 2.5D gasta CPU.
        from pixelrush_profiler_v3204 import sub_inicio, sub_fim
        sub_inicio('mundo_composicao_interna')
        emprestimo=_QA_BORROW_GEOMETRY and kind=='geometry'
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
    # Scroll incremental 2.5D so liga quando o frame COMPLETO vence
    # o blit direto e 16 comparacoes de pixels sao idênticas.
    from pixelrush_qa_scroll_auto_v327742 import instalar as instalar_scroll_qa
    instalar_scroll_qa()
    # v3.277.50: scroll incremental pixel-preservado de chunks sem sprites
    # e strips classicos; opt-in ate gate final RGBA/CPU no aparelho.
    from pixelrush_qa_incremental_scene_v327750 import instalar as instalar_incremental_qa
    instalar_incremental_qa()
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
    _INSTALADO = True


def restaurar_para_teste():
    """Somente em regressao offline, nunca executado no APK."""
    global _INSTALADO
    if _INSTALADO:
        from pixelrush_world_v3130 import LivingWorld
        LivingWorld._city_surface = _ORIGINAL
        from pixelrush_qa_incremental_scene_v327750 import restaurar_para_teste as restaurar_incremental
        restaurar_incremental()
        from pixelrush_qa_scroll_auto_v327742 import restaurar_para_teste as restaurar_scroll
        restaurar_scroll()
        from pixelrush_qa_city_tiles_v327749 import restaurar_para_teste as restaurar_tiles
        from pixelrush_qa_city_weather_v327749 import restaurar_para_teste as restaurar_clima
        restaurar_tiles()
        restaurar_clima()
        from pixelrush_qa_gles_bridge_v327749 import restaurar_para_teste as restaurar_bridge
        restaurar_bridge()
        _INSTALADO = False
