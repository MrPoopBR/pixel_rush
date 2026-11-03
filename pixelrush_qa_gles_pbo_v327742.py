# -*- coding: utf-8 -*-
"""QA 3.277.42: triplo PBO GLES3 experimental para upload de quadro RGBA.

Evita glTexSubImage2D quando bytes do quadro sao identicos. Em GLES3,
usa ring de PIXEL_UNPACK_BUFFER com orphaning por glBufferData para evitar
stall por buffer em uso na GPU. Não ha readback nem alteracao dos shaders.
Sem suporte ao driver: retornar False e fazer upload direto original.
"""
import ctypes as C
import time

GL_PIXEL_UNPACK_BUFFER=0x88EC
GL_STREAM_DRAW=0x88E0
GL_TEXTURE_2D=0x0DE1
GL_RGBA=0x1908
GL_UNSIGNED_BYTE=0x1401


class GLES3PboUnavailable(RuntimeError):
    pass


class UploadGLES3PBOQA:
    def __init__(self,presenter,count=3):
        if count<2 or count>4:
            raise ValueError('Ring de PBO fora do intervalo QA')
        if not presenter.version.startswith('OpenGL ES 3'):
            raise GLES3PboUnavailable('GLES3 obrigatorio; GLES2 usa caminho original')
        self.p=presenter
        gl=presenter.gl
        self.buffers=(C.c_uint*count)()
        self.next=0
        self.last=None
        self.encoded=0
        self.skipped=0
        self.bytes_uploaded=0
        self.cpu_ns=0
        self._closed=False
        gl.glGenBuffers.restype=None
        gl.glGenBuffers.argtypes=[C.c_int,C.POINTER(C.c_uint)]
        gl.glBindBuffer.restype=None
        gl.glBindBuffer.argtypes=[C.c_uint,C.c_uint]
        gl.glBufferData.restype=None
        gl.glBufferData.argtypes=[C.c_uint,C.c_ssize_t,C.c_void_p,C.c_uint]
        self._gen=gl.glGenBuffers
        self._bind=gl.glBindBuffer
        self._data=gl.glBufferData
        self._gen(count,self.buffers)
        if not all(self.buffers):
            raise GLES3PboUnavailable('PBO sem handle valido')
        self._delete=None
        try:
            gl.glDeleteBuffers.restype=None
            gl.glDeleteBuffers.argtypes=[C.c_int,C.POINTER(C.c_uint)]
            self._delete=gl.glDeleteBuffers
        except AttributeError:
            pass

    def enviar(self,data,width,height):
        if self._closed:
            raise GLES3PboUnavailable('ring fechado')
        if not isinstance(data,bytes) or len(data)!=width*height*4:
            raise ValueError('frame rgba sem 4 canais')
        if data==self.last:
            self.skipped+=1
            return False
        start=time.perf_counter_ns()
        self._bind(GL_PIXEL_UNPACK_BUFFER,self.buffers[self.next])
        try:
            # Orphaning da memoria do PBO; evita sobrescrever buffer pendente.
            ptr=C.cast(C.c_char_p(data),C.c_void_p)
            self._data(GL_PIXEL_UNPACK_BUFFER,len(data),ptr,GL_STREAM_DRAW)
            self.p._f['glTexSubImage2D'](
                GL_TEXTURE_2D,0,0,0,width,height,GL_RGBA,GL_UNSIGNED_BYTE,None)
        finally:
            self._bind(GL_PIXEL_UNPACK_BUFFER,0)
        if self.p._f['glGetError']()!=0:
            raise GLES3PboUnavailable('GL error durante upload PBO')
        self.last=data
        self.encoded+=1
        self.bytes_uploaded+=len(data)
        self.next=(self.next+1)%len(self.buffers)
        self.cpu_ns+=time.perf_counter_ns()-start
        return True

    def fechar(self):
        if not self._closed:
            self._bind(GL_PIXEL_UNPACK_BUFFER,0)
            if self._delete is not None:
                self._delete(len(self.buffers),self.buffers)
            self._closed=True
            self.last=None

    def diagnostico(self):
        return {'schema':'pixelrush.qa.gles3.pbo.v327742',
                'driver':self.p.renderer,'pbo_buffers':len(self.buffers),
                'frames_upload':self.encoded,'frames_idênticos_pulados':self.skipped,
                'bytes_uploaded':self.bytes_uploaded,
                'upload_cpu_total_ms':round(self.cpu_ns/1e6,3),
                'android_gpu_medido':False}
