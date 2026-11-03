# PIXEL RUSH v3.277.44-QA — Auditoria combinada: memoria, render e cobertura real

**Branch:** `qa/android-full-performance-v3.277.44`  
**Base exata:** v3.277.43-QA @ `9a6fc79b3faa4945c3fa0e4cae21de30d6795edc`  
**Versao na copia QA:** `v3.277.44-QA-ANDROID-RC` · Buildozer `3.277.44` · `android.numeric_version=327744`  
**Execucao permitida:** testes offline pygame-ce/SDL dummy + biblioteca C de teste Linux. **Nenhum APK, AAB ou teste fisico Android**.

## 1. Corrigido: limpeza RSS que provocava reconstrucoes no bioma ativo
`pixelrush_qa_performance_integrated_v327742.py` mantem as entradas do LRU `city2._scaled` enquanto `world.biome == 'cidade'` (maximo original 14), em vez de reduzir sempre para 8 a cada 180 flips quando o RSS passa do orcamento. Em qualquer bioma diferente de cidade, continua liberando as entradas frias acima de 8. Protecao da uniao de biomas ativos em `_SOURCE` preservada.
A mesma limpeza e medida separadamente por `cache_cleanup_last_ms` e `cache_cleanup_p95_ms`, evitando confundir seu custo com o swap da GPU.

## 2. Corrigido: testes atingem as classes realmente instanciadas
Novo `tests/test_qa_render_real_v327744.py` exige que `LivingWorld` importe CityPilotScene de `pixelrush_city2_v3125` e ModularBiomeScene de `pixelrush_biomes2_v3130`, testa material/normal/flow/geometry/fxmask/image, dia/noite/clima, perfis de buffers e paridade de pixels do compositor original frente ao wrapper QA.
Os testes anteriores de City v3118 e modular v3126 permanecem como testes historicos da primitiva, **nao** como prova de caminho real.
A cidade atual usa `render_scene` herdado de v3124 (ceu do ParallaxBackground): nao liga o antigo cache `_qa_cloud_sprite_cache` do metodo legado da v3118.

## 3. Batching de neve/deserto no CAMINHO REAL
Novo modulo experimental `pixelrush_qa_modular_batch_v327744.py` agrupa os dois blits por camada nas classes v3128/v3130, sem alterar qualquer tile, coordenada, pose, selecao, blend ou ordenacao de desenho. Tem flag `PIXELRUSH_QA_MODULAR_BATCH=1`, **OFF por padrao**, ate ganho ser validado no Android real e pixels comparados na cena final. A chamada de instalacao QA faz retorno imediato sem monkeypatch quando OFF. Testes offline comparam pixel RGBA em diversos frames e mapas. Nao afeta as outras formas de batching em subsistemas antigos.

## 4. Investigacao aprofundada de RAM sem mudar o visual
Novo `pixelrush_qa_audit_offline_v327744.py` inventaria `pygame.Surface` por identidade, bytes de pitch*altura, arrays NumPy e RSS (`/proc/self/status`). Documenta os limites: subsurfaces podem compartilhar buffers; total logico nao equivale ao tamanho fisico nem a VRAM.
Acompanham-se caches por mundo (cidade `_scaled`, `_night_veils`, `_flips`, canais, biomas modulares e mapas), sem mudar limites de qualidade, estacoes, efeitos ou assets.
Preparo de neve/deserto v3130 e LRU de 24 imagens/40 mapas do deserto sao medidos mas **nao alterados** por falta de prova de equivalencia e economia de RSS no aparelho.

## 5. Investigacao dos stutters: periodo 5 preservado
`CacheFundoUltraQA(periodo=5)` continua igual. Novo teste garante o padrao exato 1 redraw + 4 cache hits, invalidacao por clima, sem modificar animacao de fundo, jogabilidade ou taxa de fisica.
Novo `.github/scripts/qa_benchmark_world_real_v327744.py` acompanha **1200 frames Cidade + 1200 frames Neve + 240 frames Deserto** no subpipeline real `LivingWorld.update/draw`, camera Cinematica, HUD simplificado, cache temporal e apresentacao SDL. Calcula p50/p95/p99 TOTAL, redraw/hit e por fase, RSS amostrado a cada 60 frames e custos de limpeza, sem provocar ADB/GPU Android.
A bancada **nao reproduz o loop completo** (jogador real, inimigos, colisoes, audio, HUD real, tela fisica). Nenhum FPS Android é inferido.

## 6. Validacao e governanca
CI isolado `.github/workflows/qa-offline-v327744.yml` executa todas as suites pygame-ce legadas da v43, os novos testes, benchmark real e preflight pinado por hash; produz relatorio JSON offline. `.github/scripts/qa_preflight_v327744.py` protege assets, main, workflows APK/AAB, physics/DEV/saves/pets, versao e GPU OFF.
Versoes de testes legados e nome de relatórios QA sincronizados para `pixelrush_qa_v327744.json` e `pixelrush_qa_frames_v327744.csv`; contrato de dados/JSON/CSV mantido.

**Preservado:** visual pixel a pixel, personagens, colisao, animacao, tutorial, poderes, compras, pets, skins, save, placar, efeitos, shader, audio, tela, fisica, main e branches de producao/DEV. Nenhuma nova biblioteca no APK. Flags experimentais continuam desativadas.
