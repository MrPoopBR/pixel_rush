# PIXEL RUSH v3.277.28-QA-ANDROID-RC — Telemetria de travamentos

Base imutavel para a jogabilidade: v3.277.27 (branch correcao/android-normal-rle-v3.277.27).
Branch isolada: qa/android-profiler-v3.277.28.
Buildozer: version 3.277.28 / android.numeric_version 327728.
Workflow isolado: .github/workflows/qa-apk-debug-v327728.yml, SOMENTE android debug. Nenhuma chamada a android release e nenhum AAB.

## Alteracoes exclusivamente QA
- main.py: ativa PIXELRUSH_QA_ANDROID=1 somente no entrypoint desta branch.
- PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py: altera etiqueta VERSAO e fornece ao profiler um rotulo separado para frames de replay verdadeiro (GAMEOVER_REPLAY_QA); o estado real GAMEOVER e todas as chamadas de simulacao/render permanecem inalterados.
- pixelrush_profiler_v3204.py: conecta o observador novo aos hooks existentes de inicio/marcar/sub_inicio/sub_fim/fim; o profiler antigo permanece disponivel.
- pixelrush_qa_android_v327728.py: mede frame total, tempo de trabalho sem limitador, cadencia de FPS, CPU do processo, memoria RSS, tempos das fases e subsistemas, e quadros acima de 33.333/50/100 ms.
- .github/scripts/test_qa_android_v327728.py: testes com pygame-ce REAL via SDL dummy para coleta de corrida, replay, Game Over, grafico de pixels e exportacao JSON/CSV.
- .github/scripts/qa_preflight_v327728.py: valida Android 36 / NDK 28c / arm64-v8a / pygame-ce, hashes dos assets protegidos e reconstrucoes da fonte de jogo original, bloqueando divergencias externas ao QA.
- .github/scripts/test_android_fundo_cache_v327726.py: somente expectativa textual da nova versao QA, sem mudar verificacoes visuais.
- VERSAO_ATUAL.txt e buildozer.spec: identificacao QA e numero de versao.
- Novo workflow isolado para preflight, sintaxe, pygame e build APK debug.

## Como exportar relatorios do celular
1. Instale e abra o APK QA. Complete o tutorial, se for a primeira partida.
2. Jogue em modo NORMAL por alguns minutos, morra e assista o replay completo; repita em diferentes biomas.
3. O programa grava automaticamente a cada 600 quadros e na saida normal (nao grava a cada frame).
4. Os arquivos sao pixelrush_qa_v327728.json e pixelrush_qa_frames_v327728.csv.
5. Local preferido: pasta privada externa do proprio aplicativo:
   /sdcard/Android/data/com.bigheadmobile_pixelrush/files/pixelrush_qa/
   Uma alternativa, quando o Android bloqueia acesso externo, e a pasta privada definida por ANDROID_PRIVATE.
6. Com ADB no computador, tente:
   adb pull /sdcard/Android/data/com.bigheadmobile_pixelrush/files/pixelrush_qa/ .
   Acesso pode variar com o dispositivo e as politicas de armazenamento Android.

## Como interpretar
- Agrupamento no JSON: corrida_normal|bioma, replay|bioma e outros|bioma.
- trabalho_sem_limitador_ms: custo que exclui o tick intencional de FPS; recomendavel comparar p95 e p99.
- quadro_total_ms: inclui limitador; fps_cadencia_estimado usa intervalo entre inicios.
- CPU_processo_ms: CPU do processo inteiro, nao % do nucleo.
- RSS observado a cada 120 quadros; mede RAM do processo, nao VRAM/GPU.
- apresentacao inclui blit/scale/flip, podendo haver espera do driver. NAO equivale a GPU-ms.
- GPU REAL exige Perfetto / Android GPU profiler; o JSON exporta explicitamente null nesse campo.
- Os primeiros quadros do tutorial podem entrar em corrida_normal (estado JOGANDO).
- Eventos de I/O do proprio QA (a cada 600 quadros) podem adicionar pequenas pausas artificiais no quadro seguinte.

## Preservacao
Sem alteracoes de fisica 60Hz, colisao, RNG, movimentos, sprites, paleta, camera, shader, replay, tutorial, pets, saves, recursos, itens, gamefeel, som, efeitos, flags OFF ou DEV.
O arquivo .github/workflows/build-aab.yml, main e branch de producao remotos nao foram alterados.
O APK QA nao equivale a homologacao de FPS nem comprova desempenho no aparelho sem relatorio real.
