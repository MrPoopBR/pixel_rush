# PIXEL RUSH — notas da v3.277.83-QA (R13)

**Base:** v3.277.82-QA, commit `3c95581b60005953e6c6224221742b82a1453c99`.  
**Branch isolada:** `qa/r13-quatro-backends-v3.277.83`.  
**Entrega:** somente codigo QA, teste offline e documentacao. **Nenhum APK ou AAB sera compilado.**

## Mudancas implementadas

- **GLES/GPU:** importacao opcional de `ctypes.util`, com fallback por SONAME fixo de bibliotecas GLES/EGL; assinatura corrigida de `glTexImage2D` (9 parametros). Quando ativado manualmente em laboratorio QA (OFF por padrao), o modo experimental GL abre fullscreen fisico e usa viewport proporcional sem redimensionar o buffer 450x800. Preflight FBO mantem verificacao RGBA pixel-exata e ganho local; em excecao, reabre SDL `SCALED|FULLSCREEN` com as flags originais e informa modulo/erro. Nao liberar GPU sem gate.
- **Camera C/NEON:** amplia teste fora da corrida para quatro geometrias reais/representativas de zoom e foco, comparando TODOS os canais RGBA, com restauracao de `zoom` e `foco_y`. Mede o recorte junto ao `smoothscale`. Erros de carga nativa identificados. C original e politica de ganho minimo preservados.
- **PBO/GLES3:** corrigido o bloqueio anterior do presenter GLES e adicionada telemetria do erro PBO. Upload direto `glTexSubImage2D` permanece fallback quando o PBO falha, e quadros identicos nao provocam upload duplicado se o PBO estiver ativo. Nada e ativado sem contexto GLES3 real.
- **Cidade 2.5D:** atalho RLE exclusivamente para chunk estatico visivel sem sprites, flip ou canal tecnico foi implementado e testado com RGBA exato, mas **mantido OFF por padrao** porque o microbenchmark pygame-ce/Mesa mostrou empate ou regressao: razoes original/atalho `[0.996, 0.975, 1.003]` no primeiro CI. Sem ganho provado, usar desenho RLE original; nao marcar scroll incremental como resolvido.

## Gatilhos de seguranca / limites

O perfil `PIXELRUSH_QA_ANDROID=1` **NAO habilita o GLES fullscreen**: bancada Mesa comprovou FBO 10/10 RGBA mas pixel fisico divergente no centro da janela; caminho mantido OFF ate gate fisico e ganho. O perfil ainda habilita o codigo opt-in PBO, porem ele depende de GLES3 realmente selecionado e segue 0 uploads quando a ponte GLES recua. `PIXELRUSH_QA_CITY_RLE_FASTPATH` permanece **0** e so pode ser habilitado em bancada manual, sem integracao ao jogo ate ganho medido. Sem Android, permanece opt-in. O mundo Cidade ainda desenha sprites/cobertura parcial por caminho original. **Zero hits no cache incremental RLE pode continuar sendo a decisao correta.**

## Testes e homologacao

- `tests/test_qa_r13_four_backends_v327783.py`: GLES import/signature, queda ao SDL fullscreen, zoom nativo multicenario e paridade RGBA em RLE + microbenchmark.
- Regressao R12: toque, viewport e preflight camera.
- Teste do recorte C do host: Cidade/Neve + RGB/RGBA.
- Mesa/Xvfb: 720 cenas exatas GLES e 6 uploads/repeticoes PBO GLES3, preflight GPU.
- CI de QA: `.github/workflows/qa-r13-four-backends-v327783.yml`, isolado sem build Android.

**Diferenciar claramente:** passagem nos testes Linux/Mesa NAO equivale a FPS, PBO, C/NEON ou Mali homologados no Galaxy A54. R13 fisico continua pendente.

## Escopo preservado

Nenhum arquivo `main.py`, DEV, assets, saves, pets, tutorial, jogabilidade, hitboxes, fisica, temporizacao de simulacao ou workflow de AAB foi alterado. A unica mudanca no arquivo de jogo `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py` e a string `VERSAO`; restante e codigo QA e metadados de `buildozer.spec` sem compilacao.

## Evidencia adicionada (Linux/Python3.13)

- Novo teste `test_qa_r13_four_backends_v327783.py`: 4/4 casos aprovados; blit RLE byte a byte identico, porem sem ganho consistente.
- Biblioteca C compilada para **host**; `test_qa_crop_native_v327741.py`: 3/3 testes aprovados, incluindo Cidade/Neve e centenas de comparacoes RGB/RGBA.
- Teste antigo de viewport QA782 e suites legadas receberam atualizacao **somente das expectativas de versao**, para nao reprovar a QA783 por string antiga. Nomes dos testes historicos e comportamentos permanecem identicos.

## Investigacao adicional da superficie fisica (R13)

O preflight de FBO RGBA (10/10, zero diferencas) **nao** compara automaticamente a superficie final fisica. Uma nova prova Xvfb/Mesa em 1024x1280 encontrou pixel do centro diferente do esperado com o shader antigo em viewport 720x1280 (400+ pixels deslocados por gl_FragCoord fisico). Uma tentativa de remapeamento GLSL no host continuou divergindo para zoom>0 e **NAO foi integrada ao GitHub**. Portanto `PIXELRUSH_QA_GLES_FULLSCREEN_PROBE=1` fica opt-in de laboratorio, OFF por padrao, sem usar esta rota na corrida Android QA.

`tests/test_qa_r13_fullscreen_guard_v327783.py` verifica as diferencas FBO vs superficie fisica e exige que o perfil nao ative o candidato com pixel fisico incorreto. Nao marcar GPU/PBO real como homologados.
