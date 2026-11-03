/* PIXEL RUSH QA v3.277.41: recorte da camera nativo 32bpp.
 * Coeficientes e truncamentos identicos a pygame-ce 2.5.8:
 * SSE2/NEON: 8 bits; GENERIC: 16 bits. X ANTES de Y.
 * NAO importado no jogo, sem lib Android homologada nem JNI.
 */
#include <stdint.h>
#include <stdlib.h>
#ifdef __aarch64__
#include <arm_neon.h>
#endif

typedef struct { int ix; uint32_t a,b; } XWeight;

static void horizontal(const uint8_t *src, uint8_t *out,
        int pitch, int row, int width, const XWeight *coef, int shift) {
    const uint8_t *line = src + (size_t)row * pitch;
    for (int x=0; x<width; ++x) {
        const uint8_t *p=line+(size_t)coef[x].ix*4;
        uint8_t *dst=out+(size_t)x*4;
        for (int c=0;c<4;c++) {
            dst[c]=(uint8_t)(((uint32_t)p[c]*coef[x].a+
                               (uint32_t)p[c+4]*coef[x].b)>>shift);
        }
    }
}

static void vertical(const uint8_t *a,const uint8_t *b,
                     uint8_t *out,int bytes,int wy,int shift) {
    int w0=(1<<shift)-wy;
#ifdef __aarch64__
    if (shift==8) {
        int k=0;
        for (; k+16<=bytes; k+=16) {
            uint8x16_t p=vld1q_u8(a+k),q=vld1q_u8(b+k);
            uint16x8_t lo=vaddq_u16(
                vmulq_n_u16(vmovl_u8(vget_low_u8(p)),w0),
                vmulq_n_u16(vmovl_u8(vget_low_u8(q)),wy));
            uint16x8_t hi=vaddq_u16(
                vmulq_n_u16(vmovl_u8(vget_high_u8(p)),w0),
                vmulq_n_u16(vmovl_u8(vget_high_u8(q)),wy));
            vst1q_u8(out+k,vcombine_u8(vshrn_n_u16(lo,8),
                                       vshrn_n_u16(hi,8)));
        }
        for (;k<bytes;++k)
            out[k]=(uint8_t)(((uint32_t)a[k]*w0+(uint32_t)b[k]*wy)>>8);
        return;
    }
#endif
    for (int k=0;k<bytes;k++)
        out[k]=(uint8_t)(((uint32_t)a[k]*w0+(uint32_t)b[k]*wy)>>shift);
}

/* -1: geometria; -2: memoria; >=0: linhas.
 * Caller must hold source/dest pixel buffers until function returns.
 * Only packed 4-byte RGB(A) with corresponding mask/order is supported.
 * This function never changes the source.
 */
int pixelrush_crop_camera32(const uint8_t *src,int sw,int sh,int spitch,
                            uint8_t *dst,int dw,int dh,int dpitch,
                            int fw,int fh,int left,int top,int shift) {
    if(!src||!dst||src==dst||(shift!=8&&shift!=16)||
       sw<2||sh<2||dw<1||dh<1||
       fw<sw||fh<sh||fw>65535||fh>65535||
       left<0||top<0||left+dw>fw||top+dh>fh||
       spitch<sw*4||dpitch<dw*4) return -1;
    XWeight *weight=(XWeight*)malloc((size_t)dw*sizeof(*weight));
    uint8_t *r0=(uint8_t*)malloc((size_t)dw*4);
    uint8_t *r1=(uint8_t*)malloc((size_t)dw*4);
    if(!weight||!r0||!r1) {free(weight);free(r0);free(r1);return -2;}
    for(int x=0;x<dw;x++) {
        int64_t n=(int64_t)(x+left)*(sw-1);
        weight[x].ix=(int)(n/fw);
        weight[x].b=(uint32_t)(((int64_t)(1<<shift)*(n%fw))/fw);
        weight[x].a=(uint32_t)((1<<shift)-weight[x].b);
    }
    int previous=-1;
    for(int y=0;y<dh;y++) {
        int64_t n=(int64_t)(y+top)*(sh-1);
        int iy=(int)(n/fh);
        int wy=(int)(((int64_t)(1<<shift)*(n%fh))/fh);
        if(previous>=0&&iy==previous+1) {
            uint8_t *tmp=r0;r0=r1;r1=tmp;
            horizontal(src,r1,spitch,iy+1,dw,weight,shift);
        } else if(iy!=previous) {
            horizontal(src,r0,spitch,iy,dw,weight,shift);
            horizontal(src,r1,spitch,iy+1,dw,weight,shift);
        }
        vertical(r0,r1,dst+(size_t)y*dpitch,dw*4,wy,shift);
        previous=iy;
    }
    free(weight);free(r0);free(r1);
    return dh;
}
