# PIXEL RUSH — QA v3.277.80 — Matriz de homologação das 32 frentes

Branch isolada `qa/homologacao-32-v3.277.80`, criada da `qa/fechar-32-runtime-v3.277.79`. Nenhum APK/AAB compilado.

## Critério de contagem — sem maquiagem
- 32/32 possuem módulos ou caminhos de implementação identificados em QA (evidência estática, **não** aprovação automática).
- As 22 frentes já concluídas offline nas versões anteriores permanecem classificadas como concluídas **offline**, sujeitas aos testes de regressão QA780.
- As frentes #1, #3, #5, #7, #8, #10, #12, #28, #29 e #32 permanecem **parciais** até comprovarem funcionalidade, equivalência, segurança e ganho do caminho **real** no A54.
- Linux/Mesa GLES, Xvfb, testes mockados, compilação ou presença da `.so` **não homologam** driver Mali nem FPS físico.
- O valor 32/32 **homologadas** está BLOQUEADO enquanto faltar ao menos um gate real exigido.

## GATES OBJETIVOS por frente
| # | Melhoria | Prova offline possível | Evidência final ainda necessária |
| --- | --- | --- | --- |
| 1 | Zoom GPU | shaders ES2/ES3, RGBA 720 cenas, evolução câmera 120 frames | shader real Mali + frame completo / p95 |
| 3 | Pipeline CPU/GPU | ponte staging/HUD/input e retorno SDL | funcionamento EGL no Android, sem perda de entrada/saves/FPS |
| 5 | Scroll incremental | 108+ offsets RGB/RGBA inclusive RGB oculto, fallback SDL-RLE | ganho constante no scroll real e RAM A54 |
| 7 | Memória/alocações | orçamento RSS, GC 30k+2, trim anti-redraw | RSS/GC/perf de todos biomas no A54 |
| 8 | SIMD | comparação RGBA e autotune fora do frame | NEON efetivo e ganho no A54 |
| 10 | Passes/cópias | instrumentação R11 e RGBA frame real | pós-sprites + 2.5D p50/p95 A54 |
| 12 | Backend adaptativo | gate de drivers, sem ativação insegura | plataforma GLES/version, RAM, fallback real |
| 28 | C/NEON | biblioteca ARM64 no CI, paridade/crop C | SONAME instalado e ganho/pixels no A54 |
| 29 | GLES3 PBO | seis uploads RGBA e ring triplo GLES3 Mesa | uso real, latência e sem stall GPU Mali |
| 32 | VSync/Perfetto | contadores EGL e teste de pacing, sem falsificar Android | tracing ATrace/Perfetto do A54, jank real |

## Mudanças QA780 e segurança
- **Preflight corrigido**: pin exato do módulo GLES que mudou na QA779, asserções de versão e GC atualizadas; mantidas verificações por SHA do main.py e módulos originais que não deveriam mudar.
- **Regressão temporal real pygame-ce**: sequência de 120 frames da câmera, saltos/retrocessos do scroll incremental, transparências e RGBA oculto, cache 2.5D e medidas de p50/p95 CPU offline.
- **Cadência visual original restaurada**: o default do mundo 2.5D volta ao período 5. O período 8 continua opt-in de laboratório por `PIXELRUSH_QA_FUNDO_PERIODO=8`. Queda de número de reconstruções (37,5%) NÃO prova manutenção visual temporal, por isso não pode ser padrão antes do gate A54.
- **Observabilidade**: os artefatos `qa-preflight-v327780.json` e `qa-temporal-rgba-v327780.json` provam execução offline. Relatórios A54 ficam pendentes.
- Física, hitbox, sorteio, sprites, saves, pets, tutorial, menu, branch main, DEV e workflow AAB não foram intencionalmente alterados. O perfil GLES permanece somente QA.

## Estado do processo
O ponto de partida QA779 falhou no CI offline #41910343167 pelo PIN antigo do bridge. QA780 pretende resolver esta falha e prosseguir com as etapas restantes; incluir run ID, contagens e aprovações **somente após inspecionar logs reais**.
