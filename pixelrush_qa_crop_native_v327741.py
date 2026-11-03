# -*- coding: utf-8 -*-
"""QA v3.277.41: camera de recorte em C/NEON com igualdade inteira.

SOMENTE bancada; nao importado por main.py, jogo nem compositor de producao.
Uma biblioteca compilada explicitamente no CI ou num teste ARM e obrigatoria.
O backend original de pygame permanece intacto. Para 32bpp, reproduz os
coeficientes e truncamentos de pygame-ce 2.5.8 SSE2/NEON ou GENERIC.
"""
import ctypes as C
from pathlib import Path
import pygame


class NativeCameraUnavailable(RuntimeError):
    pass


class Crop32QA:
    """Bancada pura: nao altera camera.zoom, foco, hardware ou fisica."""

    def __init__(self, library_path):
        path=Path(library_path)
        # QA v3.277.42: no Android a biblioteca e instalada no diretório
        # nativo lib/arm64-v8a do APK; dlopen usa o SONAME do linker Android.
        # Na bancada desktop permanecem validos os caminhos absolutos.
        if path.is_file():
            load_name=str(path.resolve())
        elif path.name==str(library_path) and str(library_path).endswith('.so'):
            load_name=str(library_path)
        else:
            raise NativeCameraUnavailable('Biblioteca QA nativa ausente')
        try:
            self.lib=C.CDLL(load_name)
            fun=self.lib.pixelrush_crop_camera32
        except (OSError,AttributeError) as e:
            raise NativeCameraUnavailable('Biblioteca QA nativa invalida') from e
        fun.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,
                      C.c_void_p,C.c_int,C.c_int,C.c_int,
                      C.c_int,C.c_int,C.c_int,C.c_int,C.c_int]
        fun.restype=C.c_int
        self.func=fun
        self.saida=None
        self.formato=None

    @staticmethod
    def suportado(imagem):
        return (isinstance(imagem,pygame.Surface) and
                imagem.get_bytesize()==4 and
                imagem.get_width()>=2 and imagem.get_height()>=2)

    def processar(self,imagem,tamanho,recorte,backend=None):
        if not self.suportado(imagem):
            raise NativeCameraUnavailable('Bancada exige Surface 32bpp')
        metodo=backend or pygame.transform.get_smoothscale_backend()
        if metodo not in ('GENERIC','SSE2','NEON'):
            raise NativeCameraUnavailable('Backend original nao suportado')
        w,h=imagem.get_size()
        fw,fh=map(int,tamanho)
        x,y=map(int,recorte)
        if fw<w or fh<h or x<0 or y<0 or x+w>fw or y+h>fh:
            raise ValueError('Recorte fora do alvo de zoom')
        formato=(w,h,imagem.get_bitsize(),imagem.get_masks())
        if self.saida is None or self.formato!=formato:
            self.saida=pygame.Surface((w,h)).convert(imagem)
            self.formato=formato
        dst=self.saida
        # Mantenha ambos BufferProxy vivos durante a chamada nativa.
        buf_src=imagem.get_view('0')
        buf_dst=dst.get_view('0')
        try:
            src=C.addressof(C.c_ubyte.from_buffer(buf_src))
            dest=C.addressof(C.c_ubyte.from_buffer(buf_dst))
            resultado=self.func(src,w,h,imagem.get_pitch(),dest,w,h,
                                dst.get_pitch(),fw,fh,x,y,
                                16 if metodo=='GENERIC' else 8)
        finally:
            del buf_src,buf_dst
        if resultado!=h:
            raise NativeCameraUnavailable('Erro no recorte C: '+str(resultado))
        return dst


def gate_android(prova):
    """Ganho e RGB identico no PC nao liberam experimento no Android."""
    return bool(prova.get('testes_pixels_android_reais') and
                prova.get('sem_diferencas_em_frame_completo') and
                prova.get('ganho_camera_p95_android') and
                prova.get('ganho_fps_cadencia_android') and
                prova.get('sem_aumento_rss') and
                prova.get('preservacao_fisica_e_saves') and
                prova.get('homologacao_usuario'))
