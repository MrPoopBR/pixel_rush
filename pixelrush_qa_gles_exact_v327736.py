# -*- coding: utf-8 -*-
"""Somente bancada QA: shaders GLES2/GLES3 que reproduzem pygame-ce 2.5.8.

Códigos de referência da tag pygame-ce 2.5.8:
src_c/simd_transform_sse2.c: SSE2/NEON, pesos de 8 bits por eixo;
src_c/transform.c: GENERIC, pesos de 16 bits por eixo.

Os testes com Mesa Linux NÃO autorizam substituir a câmera no Android.
Nunca importar este módulo em main.py nem no renderizador ativo.
"""

VERTEX_ES2 = """attribute vec2 a_pos;
void main(){gl_Position=vec4(a_pos,0.0,1.0);}"""
VERTEX_ES3 = """#version 300 es
in vec2 a_pos;
void main(){gl_Position=vec4(a_pos,0.0,1.0);}"""

FRAGMENT_ES2 = """precision highp float;
precision highp int;
uniform sampler2D u_scene;
uniform vec2 u_expanded;
uniform vec2 u_crop_bottom;
const vec2 SRC=vec2(__W__.0,__H__.0);
const float SCALE=__STEP__.0;
void main(){
  vec2 xy=floor(gl_FragCoord.xy-vec2(0.5));
  if (all(equal(u_expanded,SRC))) {
    gl_FragColor=texture2D(u_scene,(xy+vec2(0.5))/SRC);
    return;
  }
  float dx=xy.x+u_crop_bottom.x;
  float dy=u_expanded.y-1.0-xy.y-u_crop_bottom.y;
  float nx=dx*(SRC.x-1.0);
  float ny=dy*(SRC.y-1.0);
  float ix=floor(nx/u_expanded.x);
  float iy=floor(ny/u_expanded.y);
  float wx=floor(SCALE*(nx-ix*u_expanded.x)/u_expanded.x);
  float wy=floor(SCALE*(ny-iy*u_expanded.y)/u_expanded.y);
  float by=SRC.y-1.0-iy;
  vec4 a=floor(texture2D(u_scene,vec2((ix+0.5)/SRC.x,(by+0.5)/SRC.y))*255.0+0.5);
  vec4 b=floor(texture2D(u_scene,vec2((ix+1.5)/SRC.x,(by+0.5)/SRC.y))*255.0+0.5);
  vec4 c=floor(texture2D(u_scene,vec2((ix+0.5)/SRC.x,(by-0.5)/SRC.y))*255.0+0.5);
  vec4 d=floor(texture2D(u_scene,vec2((ix+1.5)/SRC.x,(by-0.5)/SRC.y))*255.0+0.5);
  vec4 linha0=floor((a*(SCALE-wx)+b*wx)/SCALE);
  vec4 linha1=floor((c*(SCALE-wx)+d*wx)/SCALE);
  gl_FragColor=floor((linha0*(SCALE-wy)+linha1*wy)/SCALE)/255.0;
}"""

FRAGMENT_ES3 = """#version 300 es
precision highp float;
precision highp int;
uniform sampler2D u_scene;
uniform vec2 u_expanded;
uniform vec2 u_crop_bottom;
const ivec2 SRC=ivec2(__W__,__H__);
const int SCALE=__STEP__;
out vec4 color;
ivec4 sample_byte(ivec2 pixel){
 return ivec4(round(texelFetch(u_scene,pixel,0)*255.0));
}
void main(){
  ivec2 xy=ivec2(gl_FragCoord.xy);
  if (all(equal(ivec2(u_expanded),SRC))) {
    color=texelFetch(u_scene,xy,0);
    return;
  }
  ivec2 expanded=ivec2(u_expanded);
  ivec2 crop=ivec2(u_crop_bottom);
  int dx=xy.x+crop.x;
  int dy=expanded.y-1-xy.y-crop.y;
  int nx=dx*(SRC.x-1);
  int ny=dy*(SRC.y-1);
  int ix=nx/expanded.x;
  int iy=ny/expanded.y;
  int wx=SCALE*(nx%expanded.x)/expanded.x;
  int wy=SCALE*(ny%expanded.y)/expanded.y;
  int by=SRC.y-1-iy;
  ivec4 a=sample_byte(ivec2(ix,by));
  ivec4 b=sample_byte(ivec2(ix+1,by));
  ivec4 c=sample_byte(ivec2(ix,by-1));
  ivec4 d=sample_byte(ivec2(ix+1,by-1));
  ivec4 row0=(a*(SCALE-wx)+b*wx)/SCALE;
  ivec4 row1=(c*(SCALE-wx)+d*wx)/SCALE;
  color=vec4((row0*(SCALE-wy)+row1*wy)/SCALE)/255.0;
}"""


def shaders(api, backend, size=(450, 800)):
    """Gera vertex/fragment para o backend real do pygame-ce."""
    width, height = map(int, size)
    if not 1 < width <= 2048 or not 1 < height <= 2048:
        raise ValueError('Tamanho fora do gate QA')
    if api not in ('GLES2', 'GLES3'):
        raise ValueError('API GPU nao suportada')
    if backend not in ('SSE2', 'NEON', 'GENERIC'):
        raise ValueError('Backend pygame-ce desconhecido: ' + str(backend))
    step = 65536 if backend == 'GENERIC' else 256
    fragment = FRAGMENT_ES2 if api == 'GLES2' else FRAGMENT_ES3
    vertex = VERTEX_ES2 if api == 'GLES2' else VERTEX_ES3
    return vertex, fragment.replace('__W__', str(width)).replace('__H__', str(height)).replace('__STEP__', str(step))


def geometria_camera(width, height, zoom, foco_y):
    """Replica recorte da CameraCinematica após suavização do zoom."""
    width, height = int(width), int(height)
    z = float(zoom)
    if z < .002:
        return (width, height), (0, 0)
    extra_x = max(1, int(width * z))
    extra_y = max(1, int(height * z))
    sy = max(0, min(2 * extra_y, extra_y + int(foco_y)))
    return (width + 2 * extra_x, height + 2 * extra_y), (extra_x, 2 * extra_y - sy)


def gate_integracao(resultado, medicao_android=False):
    """Sem igualdade e ganho em hardware Android, NUNCA integrar."""
    return bool(medicao_android and resultado.get('igualdade_total') and
                resultado.get('ganho_estavel_fps_android') and
                resultado.get('egl_android_aprovado') and
                resultado.get('sem_regressoes_saves_fisica'))
