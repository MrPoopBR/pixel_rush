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
