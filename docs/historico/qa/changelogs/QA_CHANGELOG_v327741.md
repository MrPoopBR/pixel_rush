# PIXEL RUSH v3.277.41-QA — Investigação e implementação de câmera C/ARM NEON e GLES

**Branch isolada:** `qa/android-full-performance-v3.277.41`  
**Base verificada:** v3.277.40-QA, commit `73643e41e098459645e8f035757c8aeeb99ed654`; GitHub Actions #41545216616 aprovado (debug APK + QA).
**Versão QA:** `v3.277.41-QA-ANDROID-RC`, `version = 3.277.41`, `android.numeric_version = 327741`.

## Conclusões técnicas que alteraram o plano

- `CameraCinematica.aplicar` em `pixelrush_cinema_v3172.py` já reutiliza o destino de `smoothscale` e retorna um subsurface. Portanto, não duplicamos o cache.
- O pygame-ce 2.5.8, em `src_c/simd_transform_sse2.c` e `src_c/simd_shared.h`, já usa funções SSE2 traduzidas para NEON no AArch64; `src_c/simd_shared.h` habilita `PG_ENABLE_ARM_NEON` automaticamente em `__aarch64__`. A receita Android em `p4a-recipes/pygame-ce/__init__.py` já compila `src_c/simd_transform_sse2.c` via o Setup Android oficial. **Logo, forçar simplesmente NEON por flag não é melhoria e pode ser redundante.** A confirmação em execução exige coletar `pygame.transform.get_smoothscale_backend()` do JSON real Android.
- O resampler pygame-ce possui **duas famílias de arredondamento distintas**: GENERIC interpola com pesos 16 bits, SSE2/NEON com pesos de 8 bits. Trocar GENERIC por NEON altera pixels de cenas reais; não fazê-lo sem gate de igualdade.
- O SDK Android ainda apresenta `pygame.display.flip()` via SDL Surface, incompatível com substituição inocente por contexto GLES. GPU fica experimental.

## Implementações novas (nenhuma habilitada na corrida)

### 1. C nativo: recorte diretamente no tamanho da tela

- **Fonte:** `qa_native/camera_crop_native_v327741.c`. Em vez de produzir uma Surface ampliada 472×840 e depois tirar `subsurface(450×800)`, a função `pixelrush_crop_camera32` gera diretamente o recorte 450×800, pré-calculando pesos X. Mantém **ordem horizontal→vertical**, interpolação inteira e truncamento intermediário de cada estágio. Usa buffer de duas linhas e reutiliza a linha anterior; sem gerar Surface intermediária ampliada.
- No AArch64, a fase vertical de **8 bits** usa intrínsecos `arm_neon.h` para processar 16 bytes por vetor; o modo GENERIC de 16 bits mantém aritmética escalar de 32 bits para evitar overflow e diferença de arredondamento.
- Limitações: apenas superfícies de 32 bits com máscaras compatíveis, somente expansão e recorte dentro do alvo. Não substitui efeitos, HUD, jogo ou o backend nativo sem homologação.
- **Adaptador `pixelrush_qa_crop_native_v327741.py`:** chamada `ctypes` com `Surface.get_view('0')` enquanto buffers estão vivos. A biblioteca precisa ser informada explicitamente pela bancada. Nenhum `import` no `main.py`, câmera ativa ou jogo. A função `gate_android` exige pixels reais, FPS, p95, RSS, segurança física/saves e aprovação; sem evidência, continua OFF.

### 2. Testes pygame com pixels exatos

- `tests/test_qa_crop_native_v327741.py`: pelo menos 240 casos sintéticos em RGBA e RGB, quatro padrões, 5 zooms e três focos, comparando C 8/16 bits contra `pygame.transform.smoothscale` real, e fontes **dos módulos reais** `CityPilotScene` e `ModularBiomeScene('neve')` incluindo dia/noite, chuva, HUD. Verifica proteção contra superfícies 16 bpp e geometria inválida.
- **Resultado local Linux Python 3.13.5/pygame-ce 2.5.8:** 140 casos extras de zoom/foco/formato foram idênticos ao SSE2/GENERIC; o teste de regressão sintético também passou localmente. As cenas reais da branch são executadas no CI, porque os demais arquivos do jogo estão no GitHub, não no container local.
- `.github/scripts/qa_benchmark_neon_gles_v327741.py`: mede p50/p95 de pygame original (com destino reutilizado) contra C nativo, tanto GENERIC quanto SSE2, três zooms e RGB/RGBA; retorna `qa-benchmark-neon-gles-v327741.json`. Velocidade Linux, **não prova ganho ARM Android**.

### 3. Laboratório GLES2/GLES3 em cenas reais

- `tests/test_qa_gles_real_v327741.py`: gera imagens do renderizador **real** da cidade e da neve, dia/noite, chuva, opacidades RGB/RGBA; compara o resultado pixel por pixel (incluindo alfa) entre o `smoothscale` do pygame e os shaders GLES2/3 existentes nos backends GENERIC e SSE2. `glReadPixels` só ocorre na bancada de teste; nunca no jogo ou no caminho de apresentação.
- Workflow separado `.github/workflows/qa-gles-real-v327741.yml`: roda em Mesa/Xvfb e gera `qa-gles-real-scenes-v327741.json`, com flag explícita `android_medido=false`.
- A equivalência de **720 cenas sintéticas** nos shaders do v3.277.36 já havia passado no GitHub Actions #41515859981. Estes novos casos exigem **arte procedimental real**; não confundir um teste Linux Mesa com prova Android GLES.

### 4. Compilação ARM64 sem risco ao APK

- `.github/workflows/qa-apk-debug-v327741.yml` roda pygame, paridade C e benchmarks, depois compila SOMENTE APK debug ARM64 usual. Após esse build, usa o **compilador Android NDK aarch64** para compilar `qa_native/camera_crop_native_v327741.c` com `-fPIC -shared` e `-Wl,-z,max-page-size=16384`. Exige ELF AArch64 e alinhamento dos segmentos LOAD 16 KiB, e publica `qa-arm64/libpixelrush_camera_crop_v327741.so` como artefato diagnóstico **não embarcado**.
- **Atenção:** compilação cruzada é prova de construção, não execução com NEON no smartphone. Não afirmar FPS antes do ADB com relatórios reais.
- Preflight `.github/scripts/qa_preflight_v327741.py` protege fontes, assets, física, saves, AAB, configuração Android, versão, e impede qualquer ligação do C ou do GLES ao jogo.

## Decisão de desempenho

No benchmark Linux inicial, o protótipo de recorte exato **não superou SSE2 nativo**, mas em algumas rodadas foi mais rápido que o GENERIC; variação de frequência/concorrência impede atribuir ganho estável. Portanto **não ativado**, inclusive em Android. O potencial de alto impacto depende do uso real da GPU e da medição de NEON no ARM64, pois no aparelho o pygame-ce provavelmente já escolhe NEON. 

**Próximos gates:** instalar APK debug sem desinstalar, inspecionar `smoothscale` no relatório QA, capturar p50/p95/p99 de câmera, FPS, RSS, temperatura e quadros com/sem zoom, comparar CRC/diff visual de imagens reais no próprio telefone. Somente integrar binário se superar o NEON original e produzir pixels idênticos, com fail-safe.

**Preservados:** main, DEV, publicação, física, obstáculos, tutorial, jogabilidade, dificuldade, assets, skins, pets, saves, compras, HUD, AAB e GPU de produção. `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py` no QA: apenas string `VERSAO`.
