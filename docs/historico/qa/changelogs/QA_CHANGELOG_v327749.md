# PIXEL RUSH v3.277.49-QA — integração real do compositor, RAM e ponte GLES experimental

Base exata: `qa/android-full-performance-v3.277.48` (branch isolada).
Nova branch: `qa/android-full-performance-v3.277.49`.
Versão interna da cópia QA: `v3.277.49-QA-ANDROID-RC`.
`buildozer.spec`: `version = 3.277.49`, `android.numeric_version = 327749`.
Nenhum APK/AAB/ADB/Android.

## Implementação adicional real no caminho do jogo QA

1. `pixelrush_qa_city_tiles_v327749.py`: planos de tiles (sem pixels duplicados) limitados à posição atual de cada Layer da Cidade v3125 realmente usado pelo `LivingWorld`, preservando as coordenadas, a ordem, o tempo, a transparência e os objetos de textura originais. Reutilizáveis entre image/normal/geometry/fxmask/flow/material. Opt-out imediato `PIXELRUSH_QA_CIDADE_TILE_PLAN=0`. A corrida normal só usa um subconjunto de passes; não prometer melhoria grande do quinto quadro só por isso.
2. `pixelrush_qa_city_weather_v327749.py`: reduz recálculos invariantes dentro de `CityLifeDirector.draw_atmosphere` e `draw_wet_reflections` na Cidade **real**. Mantém a ordem de todos os draw calls e as condições de clima/noite/qualidade; opt-out `PIXELRUSH_QA_CITY_WEATHER_FAST=0`.
3. `pixelrush_qa_modular_batch_v327744.py`: batching de tiles de Neve e Deserto já coberto por testes RGBA históricos fica habilitado por padrão apenas nesta branch QA. Mantém `PIXELRUSH_QA_MODULAR_BATCH=0` para fallback imediato. Ainda precisa ser medido se é mais rápido.
4. `pixelrush_qa_gles_bridge_v327749.py`: integração experimental (não mais só janela de laboratório) do compositor CPU do jogo com presenter GLES2: intercepta set_mode, devolve uma Surface CPU para a lógica existente, mantém o caminho de input/HUD e apresenta via GLES no flip. Erro de shader, GL ou upload reabre SDL e blita a staging CPU. Somente se `PIXELRUSH_QA_GLES_BRIDGE=1` e QA Android for explícito; desligado por padrão.
5. No mesmo módulo, `PIXELRUSH_QA_GPU_ZOOM=1` também habilita o wrapper de `CameraCinematica.aplicar`, com suavização original de zoom/foco, e envia os parâmetros ao shader fixo do protótipo em vez do smoothscale CPU. Em caso de falha, pode reconstituir o enquadramento via smoothscale no fallback. Não passou pelo gate de paridade Android, permanece OFF. PBO GLES3 possui caminho experimental opt-in com solicitação explícita de contexto `PIXELRUSH_QA_GLES3_CONTEXT=1` e flag `PIXELRUSH_QA_GLES_PBO=1`; sem homologação real Android.
6. Herdado da v748: `pixelrush_qa_cache_trim_v327748.py` distribui limpeza de caches sob RSS alto fora do quinto quadro, com segurança multi-instância e fallback para o método antigo. `pixelrush_qa_performance_integrated_v327742.py` mantém os cálculos do clima clássico otimizados.

## Gates preparados para serem executados posteriormente

`tests/test_qa_cidade_real_v327749.py`: RGBA nos diferentes mapas/qualidades, mudanças de posição, multi-instância, retrocompatibilidade e RNG.
`tests/test_qa_gles_bridge_v327749.py`: presenter mockado sem GPU real, preservação de staging, apresentação, input e fallback SDL.
`.github/scripts/qa_benchmark_cidade_v327749.py`: CPU/RSS do compositor e clima reais, com checagem RGBA, sem extrapolar FPS Android.
`.github/scripts/qa_preflight_v327749.py`: versões, hashes, contrato de integração e proibição de ações APK no workflow manual.
`.github/workflows/qa-offline-v327749.yml`: gatilho `workflow_dispatch` **manual**, sem push automático, builds ou testes Android.

**Os novos gates não foram executados nesta etapa**, conforme solicitação de adiar os testes. Evidência de implementação != evidência de performance, muito menos comprovação no aparelho.

## Placar estrito do tracker

- 12/32 anteriormente concluídas em código/QA offline.
- 18/32 parciais (agora inclui o zoom GPU e o híbrido CPU/GPU integrados em opt-in, mas sem homologação).
- 2/32 pendentes de integração integral (#4, #5 e #29); não declarar 32/32 implementadas.
- Sem homologação Android nesta versão.

## Integridade

Somente branch QA isolada foi modificada. A cópia principal da corrida Android tem **somente o identificador VERSAO** alterado. `buildozer.spec` teve apenas dois números incrementados. main, produção, DEV, pets, tutoriais, saves, física 60Hz, shaders de produção, controles, assets, AAB, política visual, zoom original e frequência do cache 1:5 preservados por padrão. Todo recurso novo possui fallback desligável por variável de ambiente.
