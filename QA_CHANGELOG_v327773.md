# PIXEL RUSH v3.277.73-QA — R10: instrumentação fina e reuso RGB/RGBA de replay

**Base SHA:** `af1b62bf2151281a61a972d5240bf86c6ce61fc7`, v3.277.72. **Branch exclusiva:** `qa/r10-performance-v3.277.73`. Não há compilação APK ou AAB; o workflow Android só dispara e executa na branch QA anterior, que permaneceu intocada.

## Base de evidências
A telemetria real R10 v3.277.72 mediu ~928 quadros de corrida normal, FPS de cadência ~6,14, quadro p50 136,1ms, render/UI p50 92,9ms, residual estimado p50 86,1ms, mundo 2.5D p50 95,0ms nos ~199 quadros redesenhados (5:1), simulação p50 25,4ms, física do jogador p50 0,67ms. As submedidas são inclusivas e NÃO devem ser somadas.

## Atualizações
- Separação da renderização em `qa_ceu_2d`, `qa_world_draw`, `qa_particulas_mundo`, `qa_fundo_cache_chao`, `qa_render_antes_sprites`, `qa_render_apos_sprites`, `qa_hud_corrida`, `qa_replay_captura`; e `qa_simulacao_ticks` para o loop de ticks originais. Mantém todas as chamadas, superfícies, argumentos, ordem e estados; só registra tempos pela telemetria QA existente. Novo `render_restante_qa773` evita dupla subtração de `mundo_2_5d` e `clima_render`.
- Hotpath de replay QA isolado: no `ReplayCinematografico.capturar` real a Surface 225x400 descartada após 72 amostras é reciclada como destino do mesmo `pygame.transform.scale`. Os primeiros frames, cadência de 5 ticks, congelamento, índices e replay continuam idênticos. Só ativa se formato/máscaras, alpha, colorkey compatíveis; fallback original; `PIXELRUSH_QA_REPLAY_REUSE=0` desativa. Nenhuma mudança ao módulo base.
- Testes pygame-ce: verificação pixel-exata RGB e RGBA com canais ocultos, 499 ticks, replay completo, opt-out e formato divergente, benchmark alternado; gates AST e perfis; regressões da branch herdada.

## Limites
Benchmark de captura local pygame-ce 2.5.8 Linux: ganho de mediana ~8% *na captura*, não no frame. Nada comprova que os 86/95/25 ms Android foram reduzidos; o detalhamento R10 serve para apontar um algoritmo de maior impacto na próxima medição. Nenhum APK, testes Android, alterações de jogabilidade, física, zoom, visual, HUD, pets, saves, main, DEV ou workflows AAB/APK.

**Placar:** 22/32 frentes concluídas offline, 10 parciais, 0 homologadas em ARM64 físico.
