# PIXEL RUSH — QA v3.277.79 — Integração de 32 frentes (implementação versus homologação)

Branch isolada: `qa/fechar-32-runtime-v3.277.79`.
Base: `qa/fechamento-32-ui-v3.277.78`.

## Situação verificada
- **22/32**: frentes previamente concluídas em testes offline.
- **10/32**: frentes com implementações integradas no caminho QA, mas ainda condicionais ou não homologadas no Android físico. Não inventar 32/32 homologadas.
- **0/10 novas homologações em A54** nesta entrega: não foi produzido APK 779, não há medição R12 779.

## As dez frentes — caminho em QA 779
| # | Frente | Implementação no runtime QA | Condição pendente |
|---|---|---|---|
| 1 | Zoom GPU | Ponte GLES3 + shader de zoom da câmera habilitados no perfil Android QA agressivo | GPU real, pixels e melhoria de FPS |
| 3 | CPU/GPU híbrido | Apresentação GLES com staging CPU, HUD/input preservados e fallback SDL | Medida frame inteiro na Mali |
| 5 | Scroll incremental | Caminhos Cidade/clássico habilitados no perfil, com gates por cobertura/SRCALPHA e fallback | ganho de hotpath versus blit direto A54 |
| 7 | Alocações/memória | Pool, limite de cache, trim parcelado e nova fase de coleta (30k+2) | RSS/jank no aparelho |
| 8 | SIMD smoothscale | Autotune pygame-ce existente ativado na inicialização QA | backend real NEON e ganho |
| 10 | Passes/cópias | Cache de fundo 8:1 com rollback, instrumentação R11, cópias técnicas evitadas | correlação p50/p95 total |
| 12 | Seleção por aparelho | Contexto GLES3 real exigido; fracasso volta SDL, override por flags | driver/queda/seleção A54 |
| 28 | C/NEON | Wrapper nativo existente ligado ao preflight no boot com frame de cores variáveis; sem biblioteca usa CPU | presença do SONAME ARM64 + ganho real |
| 29 | PBO GLES3 | Ring triplo PBO ligado ao presenter quando contexto GLES3; erro desativa PBO | upload real e latência |
| 32 | VSync/Perfetto | ATrace habilitada no QA Android, swap instrumentado; coleta fora da fase do world | tracing de driver / cadência A54 |

### Correção de travamento comprovada na revisão de código
Em `pixelrush_qa_gc_cooperativo_v327757.py`, o agendamento antigo `frame % 5 == 1` coincidia com um redraw 5:1; na v778 o período mudou para 8:1 e o GC não foi atualizado. Na v779 coletas são agendadas em `frame = 30k+2` com prioridade de gerações 2/1/0; a limpeza parcelada recusa `frame % 5 == 1` e `frame % 8 == 1`. A sonda RSS mudou da fase 181 para 182.

### Limitações e rollback
- Perfil Android QA `agressivo` por padrão, **exclusivamente** quando `PIXELRUSH_QA_ANDROID=1` e Android real; ambiente desktop, main e DEV não recebem este perfil.
- Cada flag prevalece sobre o perfil (`PIXELRUSH_QA_GLES_BRIDGE=0`, `PIXELRUSH_QA_GPU_ZOOM=0`, `PIXELRUSH_QA_GLES_PBO=0`, `PIXELRUSH_QA_NATIVE_AUTO=0`, `PIXELRUSH_QA_CITY_INCREMENTAL=0` etc.).
- `PIXELRUSH_QA_ACCEL_PROFILE=estavel` desliga a ativação agressiva; o caminho CPU legado continua disponível.
- PBO, GLES, SIMD e NEON podem automaticamente cair para caminhos originais. Disponibilidade de código **não é** aprovação de hardware.
- Não compilado APK/AAB. Main, branch principal, DEV, compras, física, tutorial e saves não editados.

## Fechamento de implementação de código — status separado
As 10 frentes que ainda exigiam **integração** agora possuem um caminho ligado ou tentado pelo perfil Android QA agressivo; somadas às 22 anteriores, são **32/32 frentes com implementação localizada no código QA**. Isso **não** quer dizer 32/32 otimizadas com ganhos reais: cada fallback pode escolher SDL, blit direto, smoothscale ou câmera CPU. O número de frentes com aprovação offline/hardware não muda automaticamente.

No backend GLES, `Surface.convert()` é checado antes de assumir a janela de jogo; em incompatibilidade, usa SDL. `eglSwapInterval` é aplicado quando permitido. Novos relatórios do apresentador incluem p50/p95 e jank por intervalo, além de PBO/VSync.
