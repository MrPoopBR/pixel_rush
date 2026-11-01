"""Renderizador opcional GPU ModernGL / OpenGL 3.3 do Pixel Rush v3.107.

Dois passes reais por GPU: materiais/normal-map/distortion e pós-processamento
bloom/CA/motion blur/vignette. O jogo continua no Pygame sem esta dependência.
A execução headless e Android precisam de OpenGL 3.3 real; OpenGL ES puro
não é suficiente para este backend sem portar shaders e gerenciamento de contexto.
"""
import math
import os
import pygame

VERTEX = '''#version 330
in vec2 in_pos;
in vec2 in_uv;
out vec2 uv;
void main(){ uv=in_uv; gl_Position=vec4(in_pos,0.0,1.0); }
'''

MATERIAL = '''#version 330
uniform sampler2D scene;
uniform sampler2D effects;
uniform sampler2D normals;
uniform sampler2D materials;
uniform sampler2D flowmask;
uniform sampler2D geometry;
uniform sampler2D threeD;
uniform float t;
uniform float night;
uniform float climate;
uniform float heat_factor;
uniform float wet_factor;
uniform float grading;
uniform vec3 biome_light;
in vec2 uv;
out vec4 color;
const float PI=3.14159265359;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){
  vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
}
vec3 getNormal(vec2 p){return normalize(texture(normals,clamp(p,vec2(.002),vec2(.998))).rgb*2.-1.);}
float occlusion2D(vec2 p,float depth){
  float oc=0.;
  vec2 pix=1./vec2(textureSize(scene,0));
  for(int k=0;k<8;k++){
    float a=2.*PI*float(k)/8.;
    vec2 sampleUv=p+vec2(cos(a),sin(a))*pix*(4.+float(k%3)*3.);
    vec3 sampleGeo=texture(geometry,clamp(sampleUv,vec2(.002),vec2(.998))).rgb;
    oc+=max(0.,sampleGeo.r-depth-.012)*sampleGeo.g;
  }
  return 1.-clamp(oc*.94,0.,.28);
}
float softShadow(vec2 p,vec2 lightDir){
  float shadow=0.;
  vec2 stepUV=lightDir/vec2(textureSize(scene,0));
  for(int k=1;k<=12;k++){
    vec2 q=p+stepUV*float(k)*4.6;
    vec3 geo=texture(geometry,clamp(q,vec2(.003),vec2(.997))).rgb;
    float cur=texture(geometry,p).r;
    shadow+=smoothstep(.065,.26,geo.r-cur)*geo.g*(1.-float(k)/15.);
  }
  return clamp(1.-shadow*.15,.46,1.);
}
float godRays(vec2 p,vec2 sun){
  vec2 delta=(sun-p)/12.;
  float illum=0.;
  for(int k=0;k<12;k++){
    vec2 q=clamp(p+delta*float(k+1),vec2(.001),vec2(.999));
    float occ=texture(geometry,q).g;
    illum+=(1.-occ)*pow(.89,float(k));
  }
  return illum*.012;
}
vec3 screenReflection(vec2 p,vec3 base,float depth){
  vec2 texel=1./vec2(textureSize(scene,0));
  // Screen-space ray sampling near mirrored point; proxy depth used for rejection.
  vec2 origin=vec2(p.x,clamp(1.36-p.y,.01,.98));
  vec3 acc=vec3(0.);float weight=0.;
  for(int k=0;k<9;k++){
    float offset=float(k)-4.;
    vec2 q=clamp(origin+vec2(texel.x*offset*2.,sin(t*1.8+p.x*125.+offset)*texel.y*1.7),vec2(.002),vec2(.998));
    vec3 geo=texture(geometry,q).rgb;
    float valid=smoothstep(.06,.34,geo.g)*smoothstep(.05,1.,geo.r);
    float ww=valid*(1.-abs(offset)/7.);
    acc+=texture(scene,q).rgb*ww;weight+=ww;
  }
  return weight>.001?acc/weight:base;
}
void main(){
  vec2 p=uv;
  vec3 mask=texture(effects,p).rgb;
  vec3 flow=texture(flowmask,p).rgb;
  vec3 mat=texture(materials,p).rgb;
  vec3 geo=texture(geometry,p).rgb;
  float heat=max(mask.g,flow.b)*heat_factor;
  float water=max(mask.r*.6,flow.r)*wet_factor;
  float vegetation=flow.g;
  float rough=max(0.06,mat.r);
  float localAO=mat.g;
  float specular=mat.b;
  vec2 ripple=vec2(
      sin(p.y*210.+t*3.7)*.002*heat+sin(p.y*115.+t*2.7)*.0016*water+sin(p.y*85.+t*1.4)*.0007*vegetation,
      cos(p.x*125.+t*2.4)*.0012*water+cos(p.x*89.+t*1.2)*.0007*vegetation);
  vec3 base=texture(scene,clamp(p+ripple,vec2(.001),vec2(.999))).rgb;
  vec3 normal=getNormal(p);
  // Directional light and GGX-style microfacet response using estimated maps.
  vec3 lightdir=normalize(vec3(-.52+cos(t*.06)*.16,.18,.88));
  vec3 viewdir=vec3(0.,0.,1.);
  vec3 halfvec=normalize(viewdir+lightdir);
  float ndl=max(dot(normal,lightdir),.05), ndv=max(dot(normal,viewdir),.05);
  float ndh=max(dot(normal,halfvec),.0), vdh=max(dot(viewdir,halfvec),.0);
  float a=max(.025,rough*rough);float a2=a*a;
  float denom=ndh*ndh*(a2-1.)+1.;
  float D=a2/(PI*denom*denom+1e-4);
  float k=(rough+1.)*(rough+1.)/8.;
  float G=(ndv/(ndv*(1.-k)+k))*(ndl/(ndl*(1.-k)+k));
  vec3 F=vec3(.04)+(vec3(1.)-vec3(.04))*pow(1.-vdh,5.);
  vec3 ggx=clamp(D*G*F/(4.*ndv*ndl+1e-3),vec3(0.),vec3(.6));
  float ao=mix(.70,1.0,localAO)*occlusion2D(p,geo.r);
  float shadow=softShadow(p,normalize(vec2(-lightdir.x,-lightdir.y)));
  vec3 lit=base*(.69+.31*ndl)*ao*mix(1.,shadow,geo.g*.52);
  lit+=ggx*ndl*specular*(1.-rough)*.28;
  lit+=biome_light*mask.b*(.15+.76*night)*.30;
  // Geometria tridimensional REAL em textura GL residente, sutil sobre a arte.
  vec4 parallax25=texture(threeD,p);
  lit=mix(lit,parallax25.rgb,parallax25.a*.19);
  float puddle=water*smoothstep(.58,.94,p.y)*min(1.,wet_factor);
  vec3 reflected=screenReflection(p,base,geo.r);
  lit=mix(lit,reflected*.75,puddle*.25*(1.-rough));
  // 12-step god rays sampling occluder silhouettes; screen-space approximation.
  vec2 sun=vec2(.68+.13*sin(t*.055),.81);
  float rays=godRays(p,sun)*smoothstep(.25,.70,p.y)*(1.-night)*(.5+.4*climate);
  lit+=vec3(1.,.81,.61)*rays;
  // Multi-step density integration, fBm noise in screen-space (not true world 3D).
  float integrated=0.,transmittance=1.;
  for(int k=0;k<7;k++){
    float s=(float(k)+.5)/7.;
    vec2 q=p+vec2(.018*s,-.055*s);
    float density=noise(q*vec2(17.,11.)+vec2(t*.028,-t*.012));
    density=.45*density+.25*noise(q*vec2(34.,23.)+t*.016);
    float d=density*climate*.12*(1.-p.y)*geo.g;
    integrated+=d*transmittance/7.;
    transmittance*=1.-d*.18;
  }
  lit=mix(lit,vec3(.58,.67,.79),clamp(integrated,0.,.12));
  vec3 graded=mix(lit,vec3(dot(lit,vec3(.2126,.7152,.0722))),grading*.045);
  graded*=mix(vec3(1.),vec3(.73,.81,1.),night*.20);
  float hudProtect=smoothstep(.68,.75,p.y);
  graded=mix(graded,texture(scene,p).rgb,hudProtect);
  color=vec4(clamp(graded,0.,1.),1.);
}
'''

POST = '''#version 330
uniform sampler2D scene;
uniform sampler2D bloomTexture;
uniform vec2 texel;
uniform float t;
uniform float bloom_amount;
uniform float chroma_amount;
uniform float blur_amount;
uniform float night;
uniform float speed;
in vec2 uv;
out vec4 color;
vec3 sampleScene(vec2 p){return texture(scene,clamp(p,vec2(.001),vec2(.999))).rgb;}
void main(){
  vec2 center=uv-vec2(.5);
  float radial=dot(center,center);
  vec2 ca=center*radial*chroma_amount*(.011+.001*sin(t));
  vec3 c=vec3(sampleScene(uv+ca).r, sampleScene(uv).g, sampleScene(uv-ca).b);
  float blur=blur_amount*speed;
  vec3 motion=c*.56;
  for(int j=1;j<=3;j++){
    vec2 shift=vec2(texel.x*float(j)*blur*1.5,0.0);
    motion+=sampleScene(uv+shift)*.07333;
    motion+=sampleScene(uv-shift)*.07333;
  }
  vec3 bloom=texture(bloomTexture,uv).rgb;
  vec3 result=mix(c,motion,min(.4,blur_amount*.75));
  result+=bloom*bloom_amount*(.8+.28*night);
  float vignette=1.0-smoothstep(.19,.56,radial)*(.09+.025*speed);
  result*=vignette;
  // Curva tonal suave e sem alteração no alfa.
  result=clamp(result,0.0,1.0);
  float hudProtect=smoothstep(.68,.75,uv.y);
  result=mix(result,sampleScene(uv),hudProtect);
  color=vec4(result,1.0);
}
'''

BRIGHT_EXTRACT = '''#version 330
uniform sampler2D scene;
in vec2 uv;
out vec4 color;
void main(){
 vec3 s=texture(scene,uv).rgb;
 float lum=dot(s,vec3(.2126,.7152,.0722));
 float th=smoothstep(.56,.87,lum);
 color=vec4(max(vec3(0.),s-vec3(.46))*th*1.8,1.);
}
'''

GAUSSIAN_BLUR = '''#version 330
uniform sampler2D scene;
uniform vec2 texel;
uniform vec2 direction;
in vec2 uv;
out vec4 color;
void main(){
 vec3 result=texture(scene,uv).rgb*.227027;
 result+=texture(scene,uv+direction*texel*1.384615).rgb*.316216;
 result+=texture(scene,uv-direction*texel*1.384615).rgb*.316216;
 result+=texture(scene,uv+direction*texel*3.230769).rgb*.070270;
 result+=texture(scene,uv-direction*texel*3.230769).rgb*.070270;
 color=vec4(result,1.);
}
'''

class GpuPostProcessor:
    """GPU apenas quando ModernGL e OpenGL 3.3 estão disponíveis.

    Pygame continua responsável por jogo/entrada; a GPU recebe o quadro em
    textura, executa dois fragment shaders e devolve a imagem ao SDL. O caminho
    standalone requer leitura GPU->CPU, portanto a integração não é equivalente
    a um renderizador inteiramente residente na GPU.
    """
    def __init__(self, width=450, height=800, mode='auto'):
        self.enabled=False
        self.error=None
        self.width=int(width)
        self.height=int(height)
        self._ctx=None
        self._resources=[]
        if str(mode).lower() in ('0','off','false','disabled'):
            self.error='GPU desativada por configuração'
            return
        try:
            import moderngl
            self.gl=moderngl
            ctx=None
            last=None
            for backend in (None, 'egl'):
                try:
                    kwargs={'standalone':True,'require':330}
                    if backend: kwargs['backend']=backend
                    ctx=moderngl.create_context(**kwargs)
                    break
                except Exception as exc:
                    last=exc
            if ctx is None: raise RuntimeError('Nenhum contexto OpenGL 3.3: {}'.format(last))
            self._ctx=ctx
            self._create_resources()
            self.enabled=True
        except Exception as exc:
            self.error='{}: {}'.format(type(exc).__name__,str(exc))[:300]
            self._release()

    def _create_resources(self):
        g=self.gl; ctx=self._ctx
        w,h=self.width,self.height
        verts=[-1.,-1.,0.,0., 1.,-1.,1.,0., -1.,1.,0.,1.,
               -1.,1.,0.,1., 1.,-1.,1.,0., 1.,1.,1.,1.]
        import struct
        vbo=ctx.buffer(struct.pack('24f',*verts))
        prog1=ctx.program(vertex_shader=VERTEX,fragment_shader=MATERIAL)
        prog2=ctx.program(vertex_shader=VERTEX,fragment_shader=POST)
        prog_bright=ctx.program(vertex_shader=VERTEX,fragment_shader=BRIGHT_EXTRACT)
        prog_blur=ctx.program(vertex_shader=VERTEX,fragment_shader=GAUSSIAN_BLUR)
        vao1=ctx.vertex_array(prog1,[(vbo,'2f 2f','in_pos','in_uv')])
        vao2=ctx.vertex_array(prog2,[(vbo,'2f 2f','in_pos','in_uv')])
        vao_bright=ctx.vertex_array(prog_bright,[(vbo,'2f 2f','in_pos','in_uv')])
        vao_blur=ctx.vertex_array(prog_blur,[(vbo,'2f 2f','in_pos','in_uv')])
        tx_scene=ctx.texture((w,h),3)
        tx_mask=ctx.texture((w,h),3)
        tx_normal=ctx.texture((w,h),3)
        tx_material=ctx.texture((w,h),3)
        tx_flow=ctx.texture((w,h),3)
        tx_geometry=ctx.texture((w,h),3)
        tx_a=ctx.texture((w,h),3)
        tx_b=ctx.texture((w,h),3)
        tx_bright=ctx.texture((w,h),3,dtype='f2')
        tx_blur_h=ctx.texture((w,h),3,dtype='f2')
        tx_blur_v=ctx.texture((w,h),3,dtype='f2')
        for tx in (tx_scene,tx_mask,tx_normal,tx_material,tx_flow,tx_geometry,tx_a,tx_b,tx_bright,tx_blur_h,tx_blur_v):
            tx.filter=(g.LINEAR,g.LINEAR)
            tx.repeat_x=False; tx.repeat_y=False
        fbo1=ctx.framebuffer(color_attachments=[tx_a])
        fbo2=ctx.framebuffer(color_attachments=[tx_b])
        fbo_bright=ctx.framebuffer(color_attachments=[tx_bright])
        fbo_blur_h=ctx.framebuffer(color_attachments=[tx_blur_h])
        fbo_blur_v=ctx.framebuffer(color_attachments=[tx_blur_v])
        self._resources=[fbo1,fbo2,fbo_bright,fbo_blur_h,fbo_blur_v,tx_b,tx_a,tx_bright,tx_blur_h,tx_blur_v,tx_geometry,tx_flow,tx_material,tx_normal,tx_mask,tx_scene,vao2,vao1,vao_bright,vao_blur,prog2,prog1,prog_bright,prog_blur,vbo]
        self._scene,self._mask,self._normal,self._material,self._flow,self._geometry=tx_scene,tx_mask,tx_normal,tx_material,tx_flow,tx_geometry
        self._mid,self._final=tx_a,tx_b
        self._fbo1,self._fbo2=fbo1,fbo2
        self._p1,self._p2=prog1,prog2
        self._v1,self._v2=vao1,vao2
        self._fbo_bright,self._fbo_blur_h,self._fbo_blur_v=fbo_bright,fbo_blur_h,fbo_blur_v
        self._tex_bright,self._tex_blur_h,self._tex_blur_v=tx_bright,tx_blur_h,tx_blur_v
        self._vbright,self._vblur=vao_bright,vao_blur
        self._pbright,self._pblur=prog_bright,prog_blur
        for p in (prog1,prog2):
            p['scene'].value=0
        prog1['effects'].value=1
        prog1['normals'].value=2
        prog1['materials'].value=3
        prog1['flowmask'].value=4
        prog1['geometry'].value=5
        prog1['threeD'].value=6
        # 2.5D usa depth-test em framebuffer residente da GPU.
        self.mesh25d = None
        self._empty3d = ctx.texture((w,h),4, bytes(w*h*4))
        self._resources.append(self._empty3d)
        if os.environ.get('PIXELRUSH_25D','1').lower() not in ('0','false','off'):
            try:
                from pixelrush_mesh25d_v3109 import MeshParallax25D
                self.mesh25d = MeshParallax25D(ctx,g,w,h,
                    os.path.join(os.path.dirname(__file__),'world_art_v3106'))
            except Exception as exc:
                self.mesh25d = None
                self.mesh_error = str(exc)[:180]
        prog2['texel'].value=(1./w,1./h)
        prog2['bloomTexture'].value=3
        prog_bright['scene'].value=0
        prog_blur['scene'].value=0
        prog_blur['texel'].value=(1./w,1./h)

    @staticmethod
    def _bytes(surf):
        # GL espera a primeira linha de baixo para cima.
        return pygame.image.tobytes(surf,'RGB',True)

    def process(self,surface,mask=None,normal=None,frame=0,night=0.0,biome='cidade',climate='limpo',speed=1.0,material=None,flow=None,geometry=None,travel=0.0):
        if not self.enabled:
            return surface
        if surface.get_size()!=(self.width,self.height):
            return surface
        try:
            self._scene.write(self._bytes(surface))
            if mask is None:
                mask=pygame.Surface(surface.get_size()); mask.fill((0,0,0))
            self._mask.write(self._bytes(mask))
            if normal is None:
                normal=pygame.Surface(surface.get_size());normal.fill((128,128,255))
            self._normal.write(self._bytes(normal))
            if material is None:
                material=pygame.Surface(surface.get_size());material.fill((180,245,90))
            if flow is None:
                flow=pygame.Surface(surface.get_size());flow.fill((0,0,0))
            self._material.write(self._bytes(material))
            self._flow.write(self._bytes(flow))
            if geometry is None:
                geometry=pygame.Surface(surface.get_size());geometry.fill((15,0,5))
            self._geometry.write(self._bytes(geometry))
            self._ctx.viewport=(0,0,self.width,self.height)
            self._ctx.disable(self.gl.BLEND)
            if self.mesh25d is not None:
                layer3d=self.mesh25d.draw(biome,travel,frame,night)
            else:
                layer3d=self._empty3d
            self._fbo1.use()
            self._scene.use(location=0)
            self._mask.use(location=1)
            self._normal.use(location=2)
            self._material.use(location=3)
            self._flow.use(location=4)
            self._geometry.use(location=5)
            layer3d.use(location=6)
            p=self._p1
            p['t'].value=float(frame)/60.
            p['night'].value=max(0.,min(1.,float(night)))
            p['climate'].value=1.0 if climate!='limpo' else 0.0
            p['heat_factor'].value=1.0 if biome in ('vulcao','deserto') else 0.18
            p['wet_factor'].value=1.0 if biome in ('floresta','ilhas_celestes','neve','deserto') else (1.0 if climate in ('chuva','tempestade') else .35)
            p['grading'].value=.45
            p['biome_light'].value={
                'cidade':(.95,.73,.39),'neve':(.9,.8,.53),'deserto':(.99,.78,.43),
                'vulcao':(1.,.35,.16),'floresta':(.33,.9,.39),
                'cidade_futurista':(.22,.79,1.),'ilhas_celestes':(.31,1.,.78)
            }.get(biome,(.85,.85,.85))
            self._v1.render()
            # Extração de altas luzes e desfoque gaussiano separável em texturas f16.
            self._fbo_bright.use()
            self._mid.use(location=0)
            self._vbright.render()
            self._fbo_blur_h.use()
            self._tex_bright.use(location=0)
            self._pblur['direction'].value=(1.0,0.0)
            self._vblur.render()
            self._fbo_blur_v.use()
            self._tex_blur_h.use(location=0)
            self._pblur['direction'].value=(0.0,1.0)
            self._vblur.render()
            self._fbo2.use()
            self._mid.use(location=0)
            self._mask.use(location=1)
            self._tex_blur_v.use(location=3)
            q=self._p2
            q['t'].value=float(frame)/60.
            q['night'].value=max(0.,min(1.,float(night)))
            q['speed'].value=min(1.0,max(0.,(float(speed)-5.)/10.))
            q['bloom_amount'].value=.16 if biome not in ('cidade_futurista','vulcao','ilhas_celestes') else .27
            q['chroma_amount'].value=.36
            q['blur_amount'].value=.10
            self._v2.render()
            raw=self._fbo2.read(components=3,alignment=1)
            result=pygame.image.frombuffer(raw,(self.width,self.height),'RGB')
            return pygame.transform.flip(result,False,True).convert()
        except Exception as exc:
            self.enabled=False
            self.error='Shader desativado por falha: '+repr(exc)[:240]
            return surface

    def _release(self):
        if getattr(self,'mesh25d',None) is not None:
            self.mesh25d.close()
            self.mesh25d=None
        for resource in getattr(self,'_resources',[]):
            try: resource.release()
            except Exception: pass
        if self._ctx is not None:
            try:self._ctx.release()
            except Exception:pass
        self._ctx=None

    def close(self):
        self._release()
        self.enabled=False
