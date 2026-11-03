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

## Complemento na mesma v3.277.69 — atlas base `image`

- A deduplicação weak da Cidade agora inclui `image` **apenas** se o atlas do chunk já foi finalizado no construtor, é 32 bits SRCALPHA sem colorkey e possui formato/bytes identicamente comprovados (hash e comparação completa, inclusive canais RGB com alfa zero). Sprites que balançam continuam renderizados separadamente.
- Gates estendidos em `tests/test_qa_city_intern_v327768.py` com igualdade de `image` sintético e canal `image` real de duas cidades; RGBA e fallback originais continuam no teste. Ativação reversível com a mesma flag anterior, sem afetar física/saves/arte/DEV/AAB.

## CI final de v3.277.69

GitHub Actions #41730115687 **success**, commit e1f0154af749e3e383c74745af6e81e018684f3e, **51/51** casos pygame-ce offline + preflight. O 6º atlas estático `image` da Cidade entrou no interning global com bytes completos e rollback. O prewarm de superfícies transparentes de compatibilidade dos pets (não atlas de pet real) foi provado na classe real e menu; para o escopo atual da produção, fecha #22 offline. Final: **22/32 offline, 10/32 parciais, 0/32 Android homologadas**. Nenhum teste manual, APK/AAB ou Android.
