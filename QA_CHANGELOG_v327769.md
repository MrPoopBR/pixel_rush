# PIXEL RUSH QA v3.277.69 — integração única de memória visual de pets inativos

**Branch:** `qa/fechamento-32-v3.277.57` — não mesclada com `main`.

## Implementação nova (somente QA)

- O `PetStudioPlayer` original ainda não carrega atlas: pets estão indisponíveis/COMING SOON e seu `preload()` é um no-op. Não trocar essa política.
- `pixelrush_qa_pet_preload_v327769.py` é chamado apenas pelo preloader existente, durante `INICIO/LOJA/CONFIG/UPGRADES`; faz primeiro `pet5_precarregar` e depois pede `_quadros_pet_estado` para `ESPERA` em 52×46 (corrida) e 210×170 (popup). O Studio produz e retém suas próprias Surfaces transparentes, sem duplicá-las entre IDs.
- A fila continua com a skin equipada primeiro, as demais três skins ativas e um eventual pet equipado. Taxa de um item por oito quadros de menu; nada disso acontece no estado `JOGANDO`. `random` global é preservado pelo scheduler já existente.
- Fallback para execução lazy após falha, sem mexer em save ou resetar compra/estado. Nenhum visual, movimento, efeito, progressão ou input alterado.

## Evidência e limites

- CI precedente v768 **48/48** gates aprovados, inclusive intern de atlas de Cidade. Isto permite fechar **#24 offline**, não Android.
- Teste novo `tests/test_qa_pet_preload_v327769.py`: extração AST do `PetStudioPlayer` real, PNG inexistente sem fingir atlas real, comparação bytes RGBA, identidade Surface, política menu e RNG. Submetido à CI da branch; resultado a consultar no Actions.
- Pré-publicação: **21/32 completas offline; 11/32 parciais; 0 Android homologadas**. Pendente gate #22; #1/#3/#8/#12/#28/#29/#32 ainda precisam prova de GPU/driver no aparelho. Não fabricar resultados.
- Escopo de mudanças: engine exclusivamente no callback QA e versão, `buildozer.spec` versão, dois arquivos QA novos, preflight/CI offline e documentos. Preservados `main.py`, `main`, DEV, física, HUD, sprites, pets ativos/desativados, saves, assets, câmera, efeitos e workflows APK/AAB. APK/AAB não compilados.
