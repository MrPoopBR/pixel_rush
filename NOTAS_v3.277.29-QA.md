# PIXEL RUSH v3.277.29-QA — Auditoria de renderizacao pixel-equivalente

## Base e isolamento
- Base: v3.277.28-QA, SHA `81b62b107c7ff7b3cb969ec3fee34d0c5f4b6f35`.
- Branch unica: `qa/android-render-v3.277.29`.
- Buildozer: version `3.277.29`, numeric version `327729`.
- Somente APK debug ARM64; sem release, sem AAB, sem mudanca em main/DEV/producao remotos.

## Dados reais que motivaram a alteracao
- Corrida normal, Cidade: 1300 quadros, 6,88 FPS estimados, trabalho mediano 178,253 ms, renderizacao_e_ui media 122,753 ms; mundo_2_5d media 84,338 ms nas chamadas medidas.
- Replay, Cidade: 832 quadros, 28,02 FPS estimados, trabalho mediano 33,425 ms.
- Outros estados: 868 quadros, 26,65 FPS estimados, picos ocasionais ate 1384 ms.
- Posprocessamento teve picos de cerca de 184 ms. Ainda nao comprovado que foram exclusivamente `smoothscale`.

## Modificacoes estritamente QA
1. `pixelrush_qa_render_v327729.py`: elimina a limpeza duplicada do buffer intermediario 2.5D nos canais nao-foreground; cada `render_scene` limpa integralmente o destino antes de desenhar. Preserva ordem, mapas, RGB, alfa, sprite e scroll. Passes foreground usam a implementacao original.
2. `main.py`: instala o modulo de otimizacao somente no APK QA, apos a abertura; `main` remoto original permanece intacto.
3. `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py`: somente versao QA, rotulo separado de tutorial e quatro pontos adicionais de observacao visual. Nao muda a implementacao do `smoothscale` nem a frequencia de redesenho do tutorial, pois nenhuma dessas alternativas e comprovadamente pixel-identica.
4. `pixelrush_qa_android_v327728.py`: suporte a canais internos adicionais, grupo tutorial e nomes de exportacao v327729; nenhuma mudanca de dados pessoais/saves.
5. `.github/scripts/test_qa_render_v327729.py`: comparacao em pygame-ce REAL de buffers RGBA em seis canais e tres estados (Cidade), incluindo foreground; benchmark informativo. Nao assume desempenho Android a partir de SDL dummy.
6. `.github/scripts/qa_preflight_v327729.py`: prova restauracao byte a byte dos tres arquivos QA modificados para os blobs da v327728, e a integridade dos assets, hashes e build debug.
7. `.github/workflows/qa-apk-debug-v327729.yml`: workflow isolado com preflight, testes reais SDL, receita Android e auditoria ELF/ZIP 16 KiB; nao chama AAB.
8. Atualizacoes textuais de testes para versao e nomes novos dos relatorios; Buildozer e VERSAO_ATUAL.

## Cache tutorial, menu e camera
O tutorial possui pausa congelada com `cache_tutorial_congelado`; o cache alternado de fundo e desativado enquanto o tutorial esta ativo. Ativar quadros alternados alteraria a imagem e violaria o requisito pixel-exato. A versao QA nao introduz esse desvio.
A camera `CameraCinematica.aplicar` permanece em `smoothscale` e buffer reutilizavel, preservando pixels. Instrumentacao separada agora mede seu custo.
Menus permanecem renderizados sem congelamento arbitrario; a nova telemetria possibilita diferencia-los posteriormente de tutorial/replay.
O custo reduzido pela limpeza redundante deve ser mensurado: nao ha ganho de FPS real garantido.

## Arquivos exportados no dispositivo
Pasta: `/sdcard/Android/data/com.bigheadmobile_pixelrush/files/pixelrush_qa/`
- `pixelrush_qa_v327729.json` — FPS, percentis, travamentos, tempo de processo, RSS e fases detalhadas.
- `pixelrush_qa_frames_v327729.csv` — ultimos 4000 frames.
A cada 600 frames ou saida normal.
GPU real permanece indisponivel: exigiria Perfetto.
