"""Geometria 3D real para profundidade 2.5D do Pixel Rush.

ModernGL desktop: cubos com faces, normais e textura aprovada, renderizados em
framebuffer com depth test. A textura permanece na GPU entre quadros; o jogo
principal ainda usa Pygame e o compositor final existente faz readback.

Não é pipeline 100% GPU nem port Android GLES. É uma camada 3D experimental
integrada ao shader de materiais sem substituir o cenário aprovado.
"""
import os
import struct
import math

VERTEX_25D='''#version 330
in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;
uniform float scroll;
uniform float t;
out vec3 normal_out;
out vec2 uv_out;
void main(){
  float z=in_position.z;
  float perspective=1.+z*.24;
  float drift=scroll*(.010+z*.003);
  gl_Position=vec4(in_position.x-drift,
                    in_position.y+sin(t*.16+in_position.x)*.008,
                    .3-z*.17,perspective);
  normal_out=in_normal;
  uv_out=in_uv;
}
'''
FRAGMENT_25D='''#version 330
uniform sampler2D art;
uniform vec3 light_dir;
uniform float night;
in vec3 normal_out;
in vec2 uv_out;
out vec4 color;
void main(){
  vec3 n=normalize(normal_out);
  float ndl=max(.12,dot(n,normalize(light_dir)));
  vec3 col=texture(art,uv_out).rgb;
  col*=mix(.50,.93,ndl)*(1.-night*.24);
  color=vec4(col,.42);
}
'''


def _mesh_boxes():
    vertices=[]
    # Volumes discretos de pano de fundo: paredes laterais e pilares distantes.
    volumes=(( -1.84,-.27, .37,.60, .48), (-1.05,-.42,.25,.48,.36),
             (1.08,-.33,.33,.57,.58),(1.82,-.23,.41,.65,.51))
    # Cada face tem normal e mapeamento UV da mesma arte aprovada.
    faces=((0,1,2,3,(0,0,1)),(5,4,7,6,(0,0,-1)),
           (4,0,3,7,(-1,0,0)),(1,5,6,2,(1,0,0)),
           (3,2,6,7,(0,1,0)),(4,5,1,0,(0,-1,0)))
    for idx,(cx,cy,w,h,depth) in enumerate(volumes):
        x0=cx-w/2; x1=cx+w/2; y0=cy-h/2; y1=cy+h/2; z0=.15; z1=.15+depth
        pts=((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
             (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))
        u0=.12 + idx*.17; v0=.33; u1=u0+.14; v1=.86
        uvs=((u0,v1),(u1,v1),(u1,v0),(u0,v0))
        for a,b,c,d,norm in faces:
            for k in (0,1,2,0,2,3):
                pi=(a,b,c,d)[k]
                uv=uvs[k]
                vertices.extend((*pts[pi],*norm,*uv))
    return struct.pack(f'{len(vertices)}f',*vertices),len(vertices)//8

class MeshParallax25D:
    def __init__(self,ctx,gl,width,height,asset_dir):
        self.ctx=ctx;self.gl=gl
        self.width=width;self.height=height
        self.asset_dir=asset_dir
        self.source=None;self.biome=None
        self.prog=ctx.program(vertex_shader=VERTEX_25D,fragment_shader=FRAGMENT_25D)
        data,self.vertex_count=_mesh_boxes()
        self.vbo=ctx.buffer(data)
        self.vao=ctx.vertex_array(self.prog,[(self.vbo,'3f 3f 2f','in_position','in_normal','in_uv')])
        self.color=ctx.texture((width,height),4)
        self.color.filter=(gl.LINEAR,gl.LINEAR)
        self.color.repeat_x=False;self.color.repeat_y=False
        self.depth=ctx.depth_renderbuffer((width,height))
        self.framebuffer=ctx.framebuffer(color_attachments=[self.color],depth_attachment=self.depth)
        self.prog['art'].value=0

    def _set_biome(self,biome):
        if self.biome==biome:return
        if self.source is not None:
            self.source.release()
        self.source=None
        name=biome if biome in ('cidade','neve','deserto','vulcao','floresta','cidade_futurista','ilhas_celestes') else 'cidade'
        import pygame
        surf=pygame.image.load(os.path.join(self.asset_dir,name+'.png')).convert_alpha()
        self.source=self.ctx.texture(surf.get_size(),4,pygame.image.tobytes(surf,'RGBA',True))
        self.source.filter=(self.gl.LINEAR,self.gl.LINEAR)
        self.source.repeat_x=False;self.source.repeat_y=False
        self.biome=biome

    def draw(self,biome,scroll,frame,night):
        self._set_biome(biome)
        self.framebuffer.use()
        self.ctx.viewport=(0,0,self.width,self.height)
        self.framebuffer.clear(0.,0.,0.,0.,depth=1.)
        self.ctx.enable(self.gl.DEPTH_TEST)
        self.ctx.disable(self.gl.BLEND)
        self.source.use(location=0)
        self.prog['scroll'].value=(float(scroll)%10000)/60.
        self.prog['t'].value=float(frame)/60.
        self.prog['night'].value=float(night)
        self.prog['light_dir'].value=(-.55,.68,.72)
        self.vao.render(self.gl.TRIANGLES,vertices=self.vertex_count)
        self.ctx.disable(self.gl.DEPTH_TEST)
        return self.color

    def close(self):
        for x in (self.source,self.framebuffer,self.depth,self.color,self.vao,self.vbo,self.prog):
            if x is not None:
                try:x.release()
                except Exception:pass
