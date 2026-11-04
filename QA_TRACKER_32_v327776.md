# PIXEL RUSH — Tracker QA A54 v3.277.76

Base comprovada: v3.277.74-QA, CI #41873834682 (84/84 pygame-ce). Hardware ainda não homologado.

| Frente | Status | Critério faltante |
| --- | --- | --- |
| #1 Zoom GPU | Parcial | GLES real A54, pixels e frame integral |
| #3 CPU/GPU | Parcial | Input/HUD/fallback e FPS A54 |
| #5 Scroll incremental | Parcial | SDL-RLE pixel-exato e ganho consistente |
| #7 Alocações grandes | Parcial | RSS/GC + FPS A54, todos biomas |
| #8 SIMD smoothscale | Parcial | NEON real e ganho/pixels A54 |
| #10 Passes e cópias | Parcial | Custo residual R10/R11 e frame completo |
| #12 Backend por aparelho | Parcial | GLES/driver real A54 e seleção segura |
| #28 C/NEON | Parcial | ELF ARM64, carga/ABI/pixels A54 |
| #29 PBO GLES3 | Parcial | GLES3 real A54, upload RGBA e latência |
| #32 VSync e Perfetto | Parcial | Trace real A54, jank/pacing e driver |

**22/32 concluídas com provas offline; 10 parciais; 0 Android físico homologadas**, até novas medições. Ver `QA_CHANGELOG_v327776.md` para critérios e escopo. Não inferir 32/32 de CI Linux.

## Nota R11 v3.277.76
- #10 (passes): continua **parcial**. O R11 A54 confirmou custo pós-sprites p50 **64,668ms** e novo código QA habilita subpasses por seção; não há medição pós-implementação no A54.
- Mundo 2.5D: **88,631ms p50 por execução** no R11 anterior, ainda não autorizado eliminar efeitos nem mudar cadência 5:1. Há 13 marcadores no ramo 2.5D, sem substituição especulativa.
- GameFeel vinheta: otimização local RGB32 com gate RGBA, rollback automático em destinos SRCALPHA e teste SDL dummy. Apenas ganho de microbenchmark, não FPS real.
- **Placar permanece 22/32 concluídas offline, 10/32 parciais. Nenhuma das 10 novas frentes declarada homologada no A54 sem R12 comparativo.**
