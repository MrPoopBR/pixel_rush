# PIXEL RUSH — Tracker das 32 melhorias — QA v3.277.81 R12

## Resumo: implementação não é homologação
- **32/32** frentes com caminhos de código identificados e integrados na branch QA, incluindo fallbacks seletivos.
- **22/32** anteriormente concluídas por evidência offline, ainda sujeitas a regressão na candidata v3.277.81.
- **10/32** com critérios Android ainda pendentes: #1, #3, #5, #7, #8, #10, #12, #28, #29 e #32.
- **Não declarar 32/32 homologadas** por aprovação de CI, compilação APK, ausência de crashes ou benchmark Mesa.
- Situação de build: atualizar **somente** de acordo com resultado real da execução do GitHub Actions da QA781.

## Matriz de dados que a R12 vai fornecer

| Frente pendente | Evidência de execução R12 / gate | Aprovação final |
|---|---|---|
| #1 Zoom GPU | `r12_runtime.modulos.gpu_preflight`, presenter e `gles_frames`; RGBA boot | GPU Mali real + FPS/qualidade sem queda |
| #3 CPU/GPU | `gpu_bridge`, `gles_fallback_frames`, estado do HUD/inputs, tempos do frame | R12 na corrida normal sem regressões |
| #5 Scroll incremental | `scroll_cidade_hits`, rebuilds, fallback, memória do cache | ganho completo consistente A54 |
| #7 Memória | RSS atual/pico, `gc_coletas_* `, cache budget/trim, jank | RSS seguro e sem pausas adicionais |
| #8 SIMD | `camera_simd`, backend e tempos câmera | otimização realmente selecionada em ARM64 com RGBA idêntico |
| #10 Passes e cópias | `mundo_2_5d`, `qa_render_apos_sprites` e R11 subpasses por bioma | p50/p95/p99 e visual na corrida |
| #12 Backend por aparelho | `gpu_preflight`, seletor e drivers EGL/SDL | escolha correta e fallback seguro A54 |
| #28 C/NEON | `camera_neon.frames_native`, teste RGBA, carga ELF ARM64 | chamada real e ganho de custo |
| #29 PBO GLES3 | `gles_pbo_uploads`, GL version, ring PBO, swap | upload real no Mali sem stalls |
| #32 VSync/Perfetto | `egl_vsync_aplicado`, `egl_swap_p99_ms`, contadores de jank + Perfetto externo | trace real de driver/FrameTimeline |

## Gates de APK
1. VERSAO `3.277.81`, `327781`, alvo `arm64-v8a`, `minapi 26`, API 36.
2. Python 3.12.12 CPython, receita pygame-ce 2.5.8, NumPy nativo.
3. Biblioteca `libpixelrush_camera_crop_v327741.so` C/NEON AArch64 presente no APK, ELF 16 KiB.
4. ZIP_STORED, DT_NEEDED em extensões stdlib, alinhamento ZIP/ELF 16 KiB e `zipalign -P 16`.
5. Testes pygame-ce SDL headless e regressão R12; não executar nenhum passo release/AAB.
6. Relatório de APK contendo evidências reais; se falhar, registrar erro, não declarar build concluído.

## Baseline A54 disponível
R11: corrida normal Cidade, p50 pós-sprites **64,668 ms**, mundo 2.5D p50 por execução **88,631 ms**, base com **1.380 quadros CSV**. Comparação R12 deve usar o mesmo contexto de medição e verificar p95/p99, não comparar tempo de Linux contra A54.

**Saves:** nunca desinstalar o app A54 para contornar `INSTALL_FAILED_UPDATE_INCOMPATIBLE`; a assinatura debug do GitHub Actions pode variar entre compilações.
