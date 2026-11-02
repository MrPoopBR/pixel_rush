# PIXEL RUSH — v3.277.36-QA: shader GLES2/GLES3 com interpolação exata

**Branch isolada:** `qa/android-gles-pixel-exact-v3.277.36`
**Base:** `qa/android-gles-direct-v3.277.35`
**Status:** PESQUISA EXPERIMENTAL. **NÃO integrar GPU ao jogo nem publicar APK/AAB.**

## Evidência utilizada
- Telemetria real Android v3.277.30-QA: corrida ~4,8 FPS, replay ~26,28 FPS;
  `camera_smoothscale` p95 ~187,89 ms. GPU real NÃO medida.
- Código-fonte exato **pygame-ce 2.5.8** (tag `2.5.8`):
  `src_c/simd_transform_sse2.c` linhas ~275-424: expansão horizontal e
  vertical com coeficientes fixed-point de **8 bits** e truncamento.
  `src_c/transform.c` linhas ~1210-1295: GENERIC fixed-point de
  **16 bits**, arredondamento/truncamento por eixo.
- A ordem correta é X e depois Y; filtrar as quatro amostras de uma vez
  por interpolação linear normal de OpenGL dá pixels diferentes.
- `CameraCinematica.aplicar` usa zoom calculado, `int(w*zoom)`,
  `int(h*zoom)` e recorte `sy=clamp(ey+int(foco_y),0,2*ey)`.

## Implementação isolada
1. `pixelrush_qa_gles_exact_v327736.py`: dois shaders reais:
   **GLSL ES 1.00** (GLES2, `texture2D`, `highp`) e **GLSL ES 3.00**
   (GLES3, `texelFetch` e operações com inteiros).
   Ambos geram variantes SSE2/NEON (pesos 256) ou GENERIC
   (pesos 65.536), truncam após X e Y, reproduzem a posição
   vertical invertida da textura, recorte do foco e canal alfa.
   Em zoom zero usam cópia direta; não aplicam pseudo-zoom.
   Tamanho da imagem fixado na compilação do shader (450x800 no jogo).
   Não aceita backends desconhecidos.
2. Mesmo módulo registra `gate_integracao()`, que não libera
   substituição da câmera sem **igualdade de pixels, ganho de FPS
   estável no aparelho, apresentação EGL Android aprovada e
   regressões de física/saves**.
3. `tests/test_qa_gles_exact_v327736.py`: mede 720 comparações
   completas (6 padrões × 10 zooms × 3 focos × 4 combinações
   API/backend) em **framebuffer RGBA8**, incluindo transparência.
   `glReadPixels` exclusivamente na bancada de comparação,
   NUNCA no renderizador usado para apresentar o jogo.
4. `.github/scripts/qa_benchmark_gles_exact_v327736.py`: mede 200
   quadros por método após aquecimento (CPU smoothscale+blit+flip vs
   GLES2 upload+shader+swap), reportando mediana/p95.
5. `.github/scripts/qa_preflight_v327736.py`: hashes de fontes
   reais, identidade main, compositor QA, assets de Android
   e invariantes de física; proíbe importar shader no jogo.
6. `.github/workflows/qa-gles-exact-v327736.yml`: só pesquisa
   GLES2/GLES3 com pygame-ce 2.5.8 e Mesa Xvfb, publica JSON;
   **NÃO compila APK, release ou AAB**.
7. Identificador e metadados atualizados APENAS nesta branch para
   `v3.277.36-QA-ANDROID-RC` (`buildozer.spec` 3.277.36,
   `android.numeric_version = 327736`). Testes QA antigos com
   asserção de versão foram ajustados. Nada mais alterado no jogo.

## Testes locais executados — Linux, pygame-ce 2.5.8, Mesa llvmpipe
GLSL ES 1.00 + SSE2: **180/180** quadros RGBA idênticos.
GLSL ES 1.00 + GENERIC: **180/180** quadros RGBA idênticos.
GLSL ES 3.00 + SSE2: **180/180** quadros RGBA idênticos.
GLSL ES 3.00 + GENERIC: **180/180** quadros RGBA idênticos.
**Total 720/720**, sem divergências RGB ou alfa.
A saída é calculada sobre framebuffer RGBA8 separado porque o
framebuffer de apresentação SDL pode descartar alfa.
Zooms: 0, .002, .003, .008, .012, .024, .025, .034, .05, .08;
focos: -10, 0, 10. Imagens: RGB aleatória, RGBA aleatória,
gradientes horizontais e verticais, checker e linhas transparentes.

## Benchmark completo local — 200 quadros + aquecimento
Mediana observada na última rodada:
- CPU SSE2 `smoothscale+blit+flip`: **1,689 ms**, p95 **3,499 ms**.
- GLES2 `RGBA upload+shader fixed-point+swap`: **5,616 ms**,
  p95 **6,616 ms**.
- Parte upload/draw isolada: mediana **0,195 ms**.
**O novo GLES não demonstrou ganho no Linux Mesa software;
não aprovar desempenho e NÃO alegar ganho de FPS Android.**
Esses números são do host Linux, **NÃO** de um celular ou emulador.
O driver Xvfb usa GLX, portanto swap EGL Android ainda não foi
comprovado. Somente a bancada pode usar readback de pixels.

## Gates pendentes / proibições
- [x] 720 testes RGBA locais pixel a pixel idênticos.
- [x] Benchmark real do caminho completo no Linux, mais lento.
- [x] Nenhuma chamada do shader em `main.py` ou na câmera ativa.
- [x] Controle por backend SSE2/NEON vs GENERIC e geometria de foco.
- [ ] Execução confirmada dos testes/benchmark no GitHub Actions
      sobre os arquivos finais da branch.
- [ ] GPU Android/NEON: drivers fragment highp, swap EGL,
      precisão GLSL, medição Perfetto e estabilidade.
- [ ] Benchmark de FPS/p95/p99 no aparelho fraco e emuladores,
      com o mesmo cenário, mesma qualidade e saves preservados.
- [ ] Regressão visual nos sete biomas, tutorial, replay, menus.
- [ ] Só integrar GPU com equivalência pixel a pixel no Android,
      ganho estável comprovado e fallback CPU reversível.

**Decisão:** shader de pesquisa visualmente equivalente em Linux,
mas integração à PIXEL RUSH **NÃO APROVADA** por desempenho local
e falta de testes de GPU real Android. A câmera existente permanece.

## Preservação confirmada
Não alterei diretamente os branches main, DEV, publicação ou seus
workflows AAB. Sem alterações de física 60 Hz, colisões, câmera
existente, saves, pets, moedas, compras, tutoriais, shaders originais,
assets, HUD, resolução, replay ou recursos desativados.
Nenhum APK v3.277.36 foi compilado ou distribuído nesta etapa.
