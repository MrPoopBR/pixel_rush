# PIXEL RUSH v3.277.78-QA — Interface simplificada e chão do menu

Branch: `qa/fechamento-32-ui-v3.277.78`, criada da `qa/r11-passes-v3.277.76` (v3.277.77-QA).

## Alterações reais
- Menu inicial: `bg_parallax.draw_chao(display_surface)` agora é chamado após o desenho/cache do pano de fundo, restaurando o piso animado e eliminando a faixa de céu sem chão na parte inferior.
- Configurações: removidas entradas e áreas clicáveis de Acessibilidade, Controles/Input e Modo Gráfico; botão Salvar reposicionado.
- Modo Gráfico: `completo` obrigatório, inclusive saves migrados de auto/leve. Não altera compras ou outros dados do save.
- Progresso pessoal: retirados Conquistas, Base, Relíquias e Ranking Local da navegação. Cards de estatísticas e recordes por bioma continuam visíveis.
- Testes QA: `tests/test_qa_menu_limpeza_v327778.py`, compatibilidade de migração e pixel RGBA em pygame-ce SDL dummy.
- Identificadores de teste: `v3.277.78-QA-ANDROID-RC`, `version = 3.277.78`, `numeric_version = 327778`.

## Escopo / limites
- QA isolada; `main.py`, DEV, produção, saves reais, pets, tutorial, física e AAB não foram alterados.
- Sem APK ou AAB compilado. O pygame-ce offline não é demonstração de desempenho no Galaxy A54.
- Tracker: `QA_TRACKER_32_v327778.md`. As dez frentes de GPU, NEON, driver, scroll e medições permanecem explicitamente parciais até evidência concreta.

## Otimizacao de execucao do mundo 2.5D (QA Android)
- `CacheFundoUltraQA` passa a usar 8 quadros por reconstrução do fundo da corrida, em vez de 5. Menor frequencia do passe 2.5D pesado, sem mudar passos de simulacao, sprites, HUD ou saves.
- Fallback por variavel `PIXELRUSH_QA_FUNDO_PERIODO=5` para restaurar a cadencia anterior.
- Ciclo estavel de 80 frames: 10 contra 16 reconstrucoes do mundo (37,5% a menos); cada quadro de mundo efetivamente renderizado usa o caminho original. A animacao do fundo avanca em intervalos maiores e pode parecer menos suave; nao confundir essa contagem com ganho de FPS comprovado no A54.
- Cobertura em `test_cache_mundo_8_quadros_vs_5_e_paridade_rgba_estatica` no pygame-ce SDL dummy.
