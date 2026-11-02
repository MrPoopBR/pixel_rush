# PIXEL RUSH v3.277.37-QA — Pacote consolidado de desempenho

**Branch isolada:** `qa/android-full-performance-v3.277.37`  
**Base:** `qa/android-gles-pixel-exact-v3.277.36`  
**Status:** candidato de teste; **não homologado em Android**. Não publicar como produção.

## Evidências de origem (Android real v3.277.30-QA)

2.400 frames: corrida normal ~4,8 FPS (665 quadros), replay ~26,28 FPS (415).
p95 `camera_smoothscale` 187,89 ms, profundidade 143,97 ms,
mundo 2.5D 95,24 ms, física do jogador 0,15 ms; RSS pico 474,36 MB.
Submedidas podem se sobrepor, não somar percentis. Ainda não há FPS da
v3.277.37 medido no aparelho nem métricas de GPU real.

## Modificações concretas aplicadas (somente branch QA)

1. `pixelrush_world_v3130.py`: `Surface.blits` sequencial para strips,
   cache LRU de halos RGBA pixel-identificáveis, restauração de alfa
   dos props flicker sem copy, reutilização de Surface SDF, cache de
   duas texturas de primeiro plano por bioma. A física e a ordem visual não mudam.
2. `pixelrush_cenarios_v398.py`: panorama composto por um batch de blits
   ordenados com os mesmos recortes e parallax.
3. `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py` (cópia QA):
   previews de skins escaladas em cache LRU 96; telemetria separada de
   `apresentacao_escala_final`, `apresentacao_blit_final` e
   `apresentacao_swap`. Identificador `v3.277.37-QA-ANDROID-RC`.
4. `pixelrush_qa_async_export_v327737.py`,
   `pixelrush_qa_android_v327728.py`, `pixelrush_profiler_v3204.py`:
   gravação JSON/CSV fora do frame (thread única), arquivo temporário
   e substituição atômica, flush de encerramento obrigatório. Relatórios
   `pixelrush_qa_v327737.json` e `pixelrush_qa_frames_v327737.csv`.
   Cálculo dos percentis ainda é sincronizado na thread principal.
5. `buildozer.spec`: versão 3.277.37, versionCode 327737,
   APK debug ARM64 isolado; testes de versão corrigidos.
6. `tests/test_qa_full_performance_v327737.py`: 8 testes de imagem
   RGB/RGBA, panorama, halos, primeiro plano, skins, telemetria e física.
   `.github/scripts/qa_preflight_v327737.py` fixa hashes de 18 fontes
   e protege ativos; workflow `.github/workflows/qa-apk-debug-v327737.yml`
   executa pygame/stdlib/DT_NEEDED antes de compilar apenas APK debug.

## Inventário das 32 propostas — estado real

| Nº | Melhoria | Estado |
|---:|---|---|
| 1 | Zoom GPU | Shader GLES2/GLES3 isolado; **não integrado** sem ganho Android |
| 2 | Compositor 2.5D persistente | Parcial: caches e batches, reconstrução total pendente |
| 3 | Pipeline CPU/GPU híbrido | Protótipo isolado; fallback ativo, integração pendente |
| 4 | Unificar zoom/pós-processamento | Pendente, precisa preservar pixels |
| 5 | Rolagem incremental | Pendente; cache temporal existente não é rolagem pixel-exata |
| 6 | Recorte de transparência | Implementado na v3.277.31-QA |
| 7 | Evitar alocações grandes | Ampliado em halos, SDF, foreground, FABRIK, transições |
| 8 | SIMD smoothscale | Detecção/autotune conservador; NEON no Android pendente |
| 9 | Pré-compor texturas | Ampliado em nuvens, avisos, halos e foreground |
| 10 | Evitar cópias/passes | Parcial: transições, flicker e batches |
| 11 | Cache de menus | Fundo e texto anteriores + previews de skins agora cacheadas |
| 12 | Backend por dispositivo | Só sondagem; GPU requer homologação |
| 13 | Cache de sprites espelhados | Implementado na v3.277.32-QA |
| 14 | Reutilizar efeitos de alfa | Expandido: flicker sem cópia; overlays anteriores |
| 15 | Reuso FABRIK | Implementado na v3.277.32-QA |
| 16 | Culling fora da tela | Já existia |
| 17 | Agrupar blits | Implementado em panorama e strips |
| 18 | Cache céu/clima | Já existia parcialmente |
| 19 | Cache vinheta noturna | Já existia na City v3124 |
| 20 | Pool chuva/neve/partículas | Pool fixo 64 existente; auditoria por efeito pendente |
| 21 | Cache fontes/labels | Já existia, ampliado v3.277.32 |
| 22 | Pré-carregamento de skins/pets | Previews skins novas; caches pets existentes |
| 23 | Pré-aquecimento de biomas | Já existia com orçamento de RAM |
| 24 | Deduplicar superfícies | Ampliada para SDF, halos e foreground |
| 25 | Limites de cache | LRUs locais e quota atlas já existentes; política total pendente |
| 26 | Pausas do GC | Gen0 a cada 150 frames já existia; profiling de pausas pendente |
| 27 | Telemetria assíncrona | Implementada para serialização e I/O; percentis ainda síncronos |
| 28 | Cython/native seletivo | Pendente: sem prova de hot spot Python apropriado |
| 29 | Evitar uploads GPU repetidos | Depende do pipeline GPU não homologado |
| 30 | Escala final / apresentação | Cache existente, agora escala/blit/swap medidos separadamente |
| 31 | Pré-aquecer atlas | Já existia via `buffers_prod_v327710` |
| 32 | VSync/driver/Perfetto | Observação SDL parcial; medição Android real pendente |

**Não declarar 32/32 concluídas:** alteração da janela GPU, upload,
EGL real, rolagem incremental e profiling Android não podem ser
homologados com benchmark Linux. Os shaders GLES da v3.277.36
produziram 720 casos locais equivalentes, mas foram **mais lentos**
no benchmark de apresentação Mesa. Permanecem desativados no jogo.

## Testes e gates
- CI `#41519542435`: preflight de integridade e bateria pygame
  (incluindo 8 novos testes) passaram; compilação APK debug iniciada.
  Estado final do APK, ARM64, ZIP_STORED, 16 KiB e NumPy só pode ser
  aprovado após a auditoria do artefato.
- Android real e emuladores: **pendentes de medição** com arquivos JSON/CSV
  novos, comparação corrida normal vs replay, p95/p99, memória e temperatura.

## Preservação
Não houve alteração direta nas branches main, DEV, produção/release,
assets, tutorial, física 60 Hz, saves, compras, pets, colisões,
obstáculos, movimentos, idiomas, shaders de produção ou workflow AAB.
