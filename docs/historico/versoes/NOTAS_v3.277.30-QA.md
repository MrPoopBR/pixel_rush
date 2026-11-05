# PIXEL RUSH — v3.277.30-QA Android ultraleve

## Motivação / evidência
A amostra real anterior `v3.277.28-QA` no aparelho mostrou corrida normal ~6,88 FPS, 1.300 quadros observados, trabalho mediano ~178,253 ms, renderização média ~122,75 ms, mundo 2.5D ~84,34 ms nas chamadas medidas e replay ~28,02 FPS. Esses valores **não** são medições da v3.277.30. Após a pequena otimização da v3.277.29, o usuário relatou persistência de travamentos, mas ainda não anexou logs Android da v3.277.29.

## Mudanças desta branch QA
1. Novo módulo `pixelrush_qa_ultraleve_v327730.py`: cache temporal RGB do FUNDO do mundo 2.5D, até cinco quadros por composição; limita recriações pesadas quando bioma/clima/cenário e outras chaves relevantes permanecem iguais. Compõe imagem em resolução integral 450×800; não altera conteúdo de assets.
2. Cache agora habilitado também no tutorial e no modo gráfico normal em Android; invalidado por mudança de contexto e desativado em portais. O cache de instrução congelada do tutorial foi preservado.
3. `bg_parallax.draw_chao()` e `desenhar_clima_premium()` executam em **todos** os quadros mesmo quando o cenário 2.5D é reutilizado. Objetos, inimigos, animação do jogador, controles, HUD e partículas sobrepostos permanecem fora do cache.
4. Cache do fundo de telas de menu, mantendo toda a UI/redesenho de botões animada, com invalidação por estado, biome, clima, condições de luz e tamanho.
5. Versões Buildozer `3.277.30`, numeric `327730`, VERSAO_ATUAL; JSON e CSV v327730, evitando sobrescrever coletas anteriores.
6. Testes pygame-ce `.github/scripts/test_qa_ultraleve_v327730.py`: taxa de chamadas economizadas, pixel de referência nos quadros redesenhados, movimento do piso e dos sprites/HUD em todos os quadros, transições bioma/clima/tela, invariantes da física e flags desativadas.
7. Preflight `.github/scripts/qa_preflight_v327730.py`, novo workflow **somente APK debug** Android ARM64 isolado `.github/workflows/qa-apk-debug-v327730.yml` com auditoria ELF/DT_NEEDED/ZIP_STORED/alinhamento de 16 KiB; AAB/release não executado.

## Compromisso visual e limites
O objetivo é manter **a mesma resolução, sprites, cores, texturas, shaders, HUD e física**. A composição do cenário é atualizada em menor frequência; isso altera a **cadência temporal do parallax de fundo**, mas não apaga efeitos ou muda o estilo dos pixels de um fundo recém-renderizado. Não afirmar equivalência pixel a pixel *entre todos os quadros* durante o reuso. A meta de economizar aproximadamente 4 em 5 chamadas caras por chave estável (80%) vem da lógica do cache e dos testes SDL; o ganho de FPS real depende de clima, transições, CPU/GPU do aparelho e ainda precisa de nova coleta Android. Não há resultado de FPS 327730 homologado até a execução de novos testes em dispositivo.

## Preservações
Não modificar produção, DEV, main remoto, arquivos de saves, compras, pet, física 60 Hz, hitboxes, spawn, controles, recursos desligados, atlas, imagens, sons, workflow AAB ou assinatura Play Store. A branch v3.277.29 continua referência isolada para comparação.

## Coleta Android
Pasta `/sdcard/Android/data/com.bigheadmobile_pixelrush/files/pixelrush_qa/`:
- `pixelrush_qa_v327730.json`
- `pixelrush_qa_frames_v327730.csv`

No Windows com Platform Tools: `./adb.exe pull "/sdcard/Android/data/com.bigheadmobile_pixelrush/files/pixelrush_qa/" "./pixelrush_qa_coleta_v327730"`. Coletar após menu, tutorial, corrida e replay (pelo menos 600 frames) e comparar na mesma condição, sem inferir GPU real a partir do flip pygame.

**Status:** QA Android experimental; só disponibilizar APK após gates finalizados. Nenhum ganho medido no celular afirmado.
