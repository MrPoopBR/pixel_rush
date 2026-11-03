# PIXEL RUSH v3.277.45-QA — Diagnóstico do quinto quadro e pressão de memória

**Base:** v3.277.44-QA @ `49646398ecf58c3f705076ed56f40ac6fa416d27`  
**Branch isolada:** `qa/android-full-performance-v3.277.45`  
**Objetivo:** aprofundar somente o custo de redraw 1:5 e o gerenciamento RSS, com testes pixel-exatos Pygame CE offline. **NENHUM APK/AAB ou teste Android.**

## O que mudou (somente infraestrutura de QA e identificação)
- Novo teste `tests/test_qa_fifth_memory_v327745.py`: 600 quadros da politica de cache 1 redraw/4 hits com HUD mudando a cada quadro; comparacao RGBA, mudancas de clima/bioma, surfaces RGB e SRCALPHA; render em buffer alternativo para cidade, neve e deserto (experimento somente); 360 flips com RSS >limite *simulado*, protecao do LRU ativo e medicao da limpeza 180-flip; trocas repetidas de bioma.
- Novo benchmark `.github/scripts/qa_benchmark_fifth_memory_v327745.py`: mede cidade 1.200, neve 1.200, deserto 360 e cidade com RSS sinteticamente alto 540 frames (3.300 totais). Cronometra cada fase (desenho, cópia de cache, reuso, câmera, HUD simplificado, flip e limpeza a cada 180), p50/p95/p99; coleta RSS real à parte, estado dos caches, transicoes cidade/neve/deserto e flags `memory_pressure_real:false`.
- Novo workflow isolado `.github/workflows/qa-offline-v327745.yml` e preflight `.github/scripts/qa_preflight_v327745.py`, sem Android/Buildozer/Gradle/ADB; mantem suites anteriores e compara RGB byte a byte.
- Na copia de jogo QA, alterada **apenas** a string de identificacao para `v3.277.45-QA-ANDROID-RC`. Buildozer atualizado `version=3.277.45`, `android.numeric_version=327745`, **sem executar** a receita.
- Nome da telemetria QA e testes existentes atualizado para `pixelrush_qa_v327745.json` e `pixelrush_qa_frames_v327745.csv`. Contrato JSON/CSV, campos e lógica sem alterações.
- Documenta resultados e limitações em `QA_AUDITORIA_QUINTO_QUADRO_v327745.md`.

## Hipóteses testadas sem mudar gameplay
1. **Redesenho a cada quinto frame:** custos de mundo e armazenamento RGB separados; o cache original `CacheFundoUltraQA(periodo=5)` permanece imutável.
2. **Redundância de cópia:** `guardar` transfere a Surface inteira para um buffer convertido. Renderizar diretamente no cache pode remover essa transferência, MAS exige validar paridade da pilha inteira de fundos, blends e overlays e pode adicionar blit no sentido oposto.
3. **180 flips e RSS:** 180 é múltiplo de 5; medição distingue a limpeza de caches e o redraw seguinte, sem somar métricas inclusivas.
4. **RAM:** reportar pitch real e 32bpp/24bpp conforme SDL do ambiente; byte-count de imagens lógicas não equivale à RAM residente nem VRAM.
5. **Pressão simulada:** substituir retorno de `_memory_mib` em testes para exercitar código acima do budget; não equivale a provocar memory pressure do Android real.

## Invariantes
**Nenhuma alteração** em câmera, visual, partículas, clima, HUD, física, jogabilidade, IA, colisões, spawns, biomas, saves, pets, qualidade, tempo de animações, FPS, politica 5:1, scene caches, runtime GPU/PBO, main, DEV, AAB ou assets. Alternativas pesquisadas **não** foram habilitadas.

## Limitações deliberadas
O benchmark mede `LivingWorld.update/draw + cache temporal + câmera + apresentação SDL dummy + HUD simplificado` no Linux; não é a corrida completa, não inclui custo integral de ParallaxBackground, profundidade cinematográfica, inimigos/áudio/inputs e GPU Android. p50/p95/p99 não autorizam previsões de FPS Android. Nenhum Android/ADB/APK/AAB.
