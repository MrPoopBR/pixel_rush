# PIXEL RUSH v3.277.80-QA-ANDROID-RC — Homologação integral (em andamento)

Branch `qa/homologacao-32-v3.277.80` a partir de `qa/fechar-32-runtime-v3.277.79`.

## Alterações
1. Atualizadas VERSAO `v3.277.80-QA-ANDROID-RC`, versão Buildozer `3.277.80` e Android numeric version `327780`; arquivos de teste e workflows QA ajustados à nova branch.
2. Corrigido preflight bloqueante herdado da QA779: validava SHA de bridge anterior às correções, código GC antigo (1 mod5), e `version = 3.277.77`. Os novos asserts verificam o SHA correto e a coleta em fase 2; `main.py` e `pixelrush_biomes2_v3130.py` permanecem protegidos por SHA.
3. Adicionada suíte `tests/test_qa_temporal_rgba_v327780.py`: 120 quadros de câmera, 108+ posições de scroll, alfa oculto, mudanças de fundo do mundo, benchmark CPU e teste de fallback da biblioteca nativa.
4. Revertido **somente** o default experimental de cadência 8:1 do mundo 2.5D, voltando ao visual anterior 5:1; 8:1 permanece opção opt-in de laboratório. Nenhuma alteração de física, RNG, jogador ou saves.
5. Changelog e matriz separam execução de códigos, testes offline, benchmarks e certificação hardware real. Nenhum APK compilado.

## Status
- Não atribuir `32/32 homologadas` sem execução real e gates completos. As 22 frentes historicamente concluídas offline continuam separadas das 10 dependentes da integração/hardware Android.
- CI offline/Mesa reexecutado ao enviar mudanças para a branch; resultados concretos devem ser reportados sem antecipação.

## GPU / EGL / PBO — segunda etapa QA780
6. Adicionado `pixelrush_qa_gpu_preflight_v327780.py`: antes do primeiro frame de uma **execução Android QA**, a ponte GPU verifica 10 combinações de RGB/RGBA em framebuffer RGBA8, incluindo RGB oculto com alfa zero e recortes de zoom. A comparação é byte a byte com a câmera pygame-ce. O código mede o tempo da rota CPU e do upload+shader+sincronização de GPU sobre quadros diferentes; rejeita o backend se não houver ao menos 15% e 0,15 ms de ganho de microbenchmark, se houver falha de driver ou divergência RGBA, voltando ao SDL. Esse gate local **não é** aprovação final de FPS do A54.
7. Diagnóstico do presenter distingue agora `integrado_ao_jogo`, `equivalencia_visual_aprovada` e `homologado_fps_android`. Flags só passam a verdadeiras depois do teste local. Nenhum readback é feito no loop de corrida.
8. CI Mesa GLES recebe `tests/test_qa_gpu_preflight_v327780.py` e publica `qa-gpu-preflight-v327780.json` com casos e custo de CPU/GPU; CI offline publica `qa-temporal-rgba-v327780.json`.
9. Suite offline e Mesa no commit `8ea6f8b0` passaram: offline [#41914146215](https://github.com/MrPoopBR/pixel_rush/actions/runs/41914146215); GPU/Mesa [#41914146128](https://github.com/MrPoopBR/pixel_rush/actions/runs/41914146128). Estas execuções cobrem os arquivos anteriores à inclusão dos JSONs publicados.

**Homologação Galaxy A54 continua pendente**: não há APK QA780 nem R12 com GPU Mali, telemetria de FPS/jank e saves pós-instalação. Não aprovar 32/32 com base apenas nos testes em PC.

10. **Backend selector reconciliado com o runtime QA**: `pixelrush_qa_backend_gate_v327747.selecionar(..., qa_candidato=True)` agora exige contexto OpenGL, contrato SDL/HUD, paridade RGBA, ganho local da câmera, ausência de readback no frame e medição no Android QA. A ponte chama o seletor **somente após** seu preflight real; se o seletor recusar, restaura SDL. O seletor informa explicitamente `homologado_fps_android=False` e mantém `pronto_para_trocar_entrada_real=False`: autorizar experimento QA não significa aprovar produção.
11. Adicionada regressão do seletor para ambiente desktop, Android simulado, ausência de ganho e impossibilidade de marcar FPS final.
