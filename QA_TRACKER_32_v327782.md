# Tracker PIXEL RUSH v3.277.82-QA — R12 Android real + correções

## Situação comprovada
- **22/32 frentes** com testes offline historicamente concluídos na candidata v781 (revalidar na v782 CI).
- **10/32 frentes** com homologação Android pendente: #1, #3, #5, #7, #8, #10, #12, #28, #29, #32.
- **0 provas R13 v782 A54** disponíveis. Não marcar 32/32, nem afirmar novos FPS.
- Baseline R12 de v781 comprova 3,56 FPS Cidade, 3,17 FPS Neve, 215 ms de smoothscale e backend GPU/NEON não utilizados.
- v782 corrige **caminho de seleção** C/NEON e viewport; somente instalação + R13 validará ganho.

## Gates por frente crítica
| Frente | Prova R12 v781 | Requisito R13 |
|---|---|---|
| #1 GPU zoom | 0 quadros GPU; falha import | Sem regressão RGBA se algum dia habilitar GLES |
| #3 CPU/GPU | Fallback SDL nos 2.594 quadros | FPS/qualidade e HUD/input intactos |
| #5 Scroll | 0 hits de scroll Cidade | Contadores positivos + ganho pixel-exato |
| #7 RAM/GC | RSS até 474,23 MiB, GC executado | Memória segura e menor jank |
| #8 SIMD | NEON pygame original, 215ms camera | Paridade RGBA e custo camera p95 |
| #10 Passes | Mundo 2.5D p50 116ms quando chamado | Otimizar apenas com RGBA temporal comprovado |
| #12 Backend | Criacao ModuleNotFoundError | SDL fullscreen, sem tela pequena |
| #28 Nativo C/NEON | 0 quadros, preflight ignorou zoom | `teste_real=true`, `pixels_exatos=true`, `frames_native>0`, redução camera |
| #29 GLES3 PBO | 0 uploads | Prova real A54 antes de ativação |
| #32 VSync | nenhum EGL interval reportado | frame timeline/perfetto externo em hardware |

**Não compilar AAB nem modificar DEV/main.** Ver `QA_R12_A54_DIAGNOSTICO_v327782.md` e `QA_CHANGELOG_v327782.md`.
