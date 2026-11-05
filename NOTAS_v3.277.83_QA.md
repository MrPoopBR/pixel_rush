# PIXEL RUSH — notas da v3.277.83-QA (R13)

**Base:** v3.277.82-QA, commit `3c95581b60005953e6c6224221742b82a1453c99`.  
**Branch isolada:** `qa/r13-quatro-backends-v3.277.83`.  
**Entrega:** somente codigo QA, teste offline e documentacao. **Nenhum APK ou AAB sera compilado.**

## Mudancas implementadas

- **GLES/GPU:** importacao opcional de `ctypes.util`, com fallback por SONAME fixo de bibliotecas GLES/EGL; assinatura corrigida de `glTexImage2D` (9 parametros). Quando ativado no perfil Android QA, o modo experimental GL abre fullscreen fisico e usa viewport proporcional sem redimensionar o buffer 450x800. Preflight FBO mantem verificacao RGBA pixel-exata e ganho local; em excecao, reabre SDL `SCALED|FULLSCREEN` com as flags originais e informa modulo/erro. Nao liberar GPU sem gate.
- **Camera C/NEON:** amplia teste fora da corrida para quatro geometrias reais/representativas de zoom e foco, comparando TODOS os canais RGBA, com restauracao de `zoom` e `foco_y`. Mede o recorte junto ao `smoothscale`. Erros de carga nativa identificados. C original e politica de ganho minimo preservados.
- **PBO/GLES3:** corrigido o bloqueio anterior do presenter GLES e adicionada telemetria do erro PBO. Upload direto `glTexSubImage2D` permanece fallback quando o PBO falha, e quadros identicos nao provocam upload duplicado se o PBO estiver ativo. Nada e ativado sem contexto GLES3 real.
- **Cidade 2.5D:** atalho RLE exclusivamente para chunk estatico visivel sem sprites, flip ou canal tecnico. Ele usa `target.blit(source)` com exatamente a mesma Surface do caminho original. Nao reutiliza pixéis intermediarios translucidos; o cache incremential anterior permanece desligado para fontes RLE quando houver risco de mudar RGB oculto. Um contador separado distingue esse caminho de verdadeiros acertos de cache.

## Gatilhos de seguranca / limites

O perfil `PIXELRUSH_QA_ANDROID=1` deve conter as flags de laboratorio `PIXELRUSH_QA_GLES_FULLSCREEN_PROBE=1`, `PIXELRUSH_QA_GLES_PBO=1` e `PIXELRUSH_QA_CITY_RLE_FASTPATH=1`; cada alternativa tem fallback. Sem Android, permanece opt-in. O mundo Cidade ainda desenha sprites/cobertura parcial por caminho original. **Zero hits no cache incremental RLE pode continuar sendo a decisao correta.**

## Testes e homologacao

- `tests/test_qa_r13_four_backends_v327783.py`: GLES import/signature, queda ao SDL fullscreen, zoom nativo multicenario e paridade RGBA em RLE + microbenchmark.
- Regressao R12: toque, viewport e preflight camera.
- Teste do recorte C do host: Cidade/Neve + RGB/RGBA.
- Mesa/Xvfb: 720 cenas exatas GLES e 6 uploads/repeticoes PBO GLES3, preflight GPU.
- CI de QA: `.github/workflows/qa-r13-four-backends-v327783.yml`, isolado sem build Android.

**Diferenciar claramente:** passagem nos testes Linux/Mesa NAO equivale a FPS, PBO, C/NEON ou Mali homologados no Galaxy A54. R13 fisico continua pendente.

## Escopo preservado

Nenhum arquivo `main.py`, DEV, assets, saves, pets, tutorial, jogabilidade, hitboxes, fisica, temporizacao de simulacao ou workflow de AAB foi alterado. A unica mudanca no arquivo de jogo `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py` e a string `VERSAO`; restante e codigo QA e metadados de `buildozer.spec` sem compilacao.
