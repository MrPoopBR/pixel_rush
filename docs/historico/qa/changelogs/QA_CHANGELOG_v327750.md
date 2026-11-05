# PIXEL RUSH v3.277.50-QA — pipeline real de apresentação, scroll parcial e pressão RAM

**Branch isolada:** `qa/android-full-performance-v3.277.50`.
**Base:** `qa/android-full-performance-v3.277.49`.
**Versão:** `v3.277.50-QA-ANDROID-RC`; Buildozer `3.277.50` / `327750` (somente metadados; não construir APK).

## Implementação diretamente no jogo QA

- **#4 — pipeline CPU/GPU unificado, parcialmente integrado:** em `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py`, o loop de apresentação chama `pixelrush_qa_unified_post_v327750.finalizar_quadro` por padrão no modo QA. Preserva o gamefeel e o GPU processor antes do estágio, a CameraCinematica e suas condições, a escala final e o `pygame.display.flip` da mesma maneira que o código original. Se `PIXELRUSH_QA_POST_PIPELINE=0` ou execução fora do QA, o bloco legado permanece intacto. O software omite apenas um blit 1:1 na mesma Surface quando RGB opaco, sem cor-chave, pois é estritamente redundante. Isso é uma integração estrutural, não uma promessa de FPS.
- **#5 — scroll incremental, parcialmente integrado com gates ainda OFF:** `pixelrush_qa_incremental_scene_v327750.py` instala wrappers em `CityPilotScene._render_chunk` e `LivingWorld._blit_strip`. Em chunks sem sprites e apenas no canal image, a Surface de base pode ser rolada por pixels, com preenchimento exclusivo da borda exposta. Preserva a ordem da cena (base de cada chunk no mesmo instante, depois os sprites que seguem a função original). Para os clássicos opacos usa a FaixaPersistenteQA preexistente. Limite de duas Surfaces de 450x500 por instância de Cidade e uma faixa por mundo clássico, em WeakKeyDictionary. Flags opt-in `PIXELRUSH_QA_CITY_INCREMENTAL=1` / `PIXELRUSH_QA_CLASSIC_INCREMENTAL=1`; default OFF até verificação RGBA/jitter. Não tocar na política 5:1 de fundo.
- **#7/#10/#24 — geometria sem grandes cópias:** o módulo real `pixelrush_city2_v3124.py` e o módulo real `pixelrush_biomes2_v3128.py` reutilizam `_geometry_view`, fazendo `pygame.transform.scale` 1:1 para cópia bruta exata em buffers já existentes. Evita alocação contínua de cerca de 900 KiB por passagem de geometria quando solicitada. O buffer externo é agora persistente: consumidores que mantiverem referência verão a versão atual, em vez de snapshot antigo; testar possíveis consumidores na homologação.
- **#25/#26 — limpeza RSS de vinhetas noturnas:** `pixelrush_qa_cache_trim_v327748.py` foi estendido para liberar Surfaces antigas `_night_veils` em lotes fora do quinto quadro, só sob pressão RSS, sem remover nível de noite atual nem vizinhos. Preserva no mínimo quatro, e o LRU regenerará texturas por fórmula original se necessário.
- **#1/#3/#29 — correção de integração experimental:** `pixelrush_qa_gles_bridge_v327749.py` cria staging Surface de 32 bits sem depender de `Surface.convert()` da janela SDL_GL. O bridge continua opt-in OFF, não há alegação de paridade ou de aceleração Android.

## Não alterado

Física, velocidades, hitboxes, HUD, entrada, moedas, inimigos, tutorial, replay, modo DEV, pets, saves, audio, efeitos, assets, qualidade visual, 60 Hz de simulação, 30 Hz de renderização QA, período de cache fundo 5:1, `main.py`, produção, AAB e demais workflows de empacotamento. Não houve compilação APK/AAB, nem chamadas ADB/testes Android.

## Evidência e estado

Novos arquivos de gates: `tests/test_qa_pipeline_scroll_v327750.py`, `.github/scripts/qa_benchmark_pipeline_scroll_v327750.py`, `.github/scripts/qa_preflight_v327750.py` e workflow **manual** `.github/workflows/qa-offline-v327750.yml`. Execução da nova suíte/regressões completa fica para a homologação posterior solicitada pelo usuário.

**Status conservador:** 12 frentes anteriormente concluídas offline; 20 com integração parcial ou testes pendentes; nenhuma sem caminho inicial. **Não são 32 melhorias finalizadas**, não há prova do ganho de FPS real e a rolagem incremental permanece desligada até medir. Veja `QA_TRACKER_32_v327750.md`.
