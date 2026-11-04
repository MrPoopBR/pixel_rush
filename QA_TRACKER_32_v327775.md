# PIXEL RUSH — Tracker QA A54 v3.277.75

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

**22/32 concluídas com provas offline; 10 parciais; 0 Android físico homologadas**, até novas medições. Ver `QA_CHANGELOG_v327775.md` para critérios e escopo. Não inferir 32/32 de CI Linux.
