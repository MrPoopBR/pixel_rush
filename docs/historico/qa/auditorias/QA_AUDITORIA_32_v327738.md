# PIXEL RUSH v3.277.38-QA — Auditoria tecnica das 32 frentes

**Escopo auditado:** branch base `qa/android-full-performance-v3.277.37` e alteracoes isoladas `qa/android-full-performance-v3.277.38`.
**Origem de desempenho:** telemetria Android real v3.277.30: 2.400 frames, ~4,8 FPS corrida normal vs ~26,28 FPS replay; p95 camera_smoothscale ~187,89 ms, profundidade ~143,97 ms e mundo 2.5D ~95,24 ms. As secoes podem ser inclusivas: nao somar os p95 como se fossem independentes. **Nao existem ainda novos FPS Android v3.277.38.**

## Inventario das 32 frentes — status respaldado pelo codigo ou trabalho anterior

Legenda: **ativo** = existe no codigo QA, nao implica ganho em Android; **parcial** = so parte do caminho implementada; **pendente** = nao habilitar sem equivalencia, benchmark e dispositivo real.

| # | Proposta | Estado / evidencia | Acao v3.277.38 |
|---:|---|---|---|
| 1 | Zoom na GPU | Pendente: `pixelrush_qa_gles_exact_v327736.py` isolado, sem habilitar no main | Nao ativado; benchmark Mesa foi desfavoravel |
| 2 | Compositor 2.5D persistente | Parcial: `pixelrush_world_v3130.py`, surfaces reutilizadas | Lote novo para strips SDF |
| 3 | Pipeline CPU/GPU hibrido | Pendente de EGL Android e pixels identicos | Preservado desligado |
| 4 | Unificar zoom/pos-processamento | Pendente: camera aplica smoothscale com cache destino | Mantido para evitar divergencia |
| 5 | Scroll incremental de pixels | Pendente: cache temporal nao e scroll incremental equivalente | Mantido sem alteracao |
| 6 | Recorte de transparencias | Ativo QA em `pixelrush_qa_alpha_blit_v327731.py` | Lotes por faixa recortada |
| 7 | Evitar grandes alocacoes | Parcial/ampliado: SDF, foreground e buffers | Reaproveita buffer SDF ja existente |
| 8 | SIMD para smoothscale | Autotune conservador em `pixelrush_qa_camera_v327733.py` | NEON Android nao validado |
| 9 | Precomposicao de texturas | Ativo em halos, nuvens, primeiro plano e UI | Sem duplicacao |
| 10 | Remover copias e passes | Parcial: elimina temporarias alfa e limpa redundante | Nao muda ordem de camadas |
| 11 | Cache de menus | Ativo em fundo, labels e previews de skins | Preservado |
| 12 | Backend por dispositivo | Parcial: sondas e autotune; GPU nao homologada | Sem selecao GPU nova |
| 13 | Cache de sprites espelhados | Ativo em props v3.277.32 | Preservado |
| 14 | Reuso de alpha overlays | Ativo em transicoes e props flicker | Preservado |
| 15 | Reuso FABRIK/deformacao | Ativo em buffers v3.277.32 | Preservado |
| 16 | Culling fora da tela | Preexistente em varias camadas | Preservado, auditoria integral pendente |
| 17 | Agrupar blits | Ativo em panorama e strips v3.277.37 | Aumentado para profundidade e SDF |
| 18 | Cache ceu/clima | Preexistente parcialmente; efeitos dinamicos variam por frame | Sem quantizacao visual |
| 19 | Cache vinheta noturna | Preexistente em City v3124 | Sem alteracao |
| 20 | Pool chuva/neve/particulas | Pool fixo em componentes; cobertura nao completa | Auditoria por efeito pendente |
| 21 | Cache de fontes/labels | Ativo, cache limitado no jogo | Preservado |
| 22 | Pre-carregamento skins/pets | Previews skins cacheadas; pets tem caches separados | Sem expandir RAM sem medicao |
| 23 | Pre-aquecer biomas | Existente e limitado por memoria | Preservado |
| 24 | Deduplicar surfaces | Parcial: halos, SDF, foreground | Lotes sem surfaces extras |
| 25 | Limites globais de cache | Parcial: LRUs locais e atlas; orcamento agregado pendente | Nao aumentar caches |
| 26 | GC com perfil de pausas | Gen0 periodico preexistente; p95 de pausas nao isolado | Sem mexer no ciclo de memoria |
| 27 | Telemetria assincrona | Parcial v3.277.37: serializacao/I-O worker, percentis na thread principal | Percentis agora no worker sobre snapshots |
| 28 | Cython/native seletivo | Pendente: nao provado hotspot Python elegivel | Nao introduzir dependencias |
| 29 | Evitar uploads GPU repetidos | Depende de caminho GPU ainda inativo | Nao mexido |
| 30 | Apresentacao final/SDL | Escala, blit e flip medidos separadamente | Preservar medicao |
| 31 | Pre-aquecer atlas | Ativo via buffers/atlas existentes | Nao duplicar |
| 32 | VSync/driver/Perfetto | Sondas SDL parciais; Perfetto Android nao colhido | Pendente hardware real |

## Mudancas verificaveis v3.277.38

1. `pixelrush_qa_alpha_blit_v327731.py`: faixas de profundidade repetidas agora usam `Surface.blits(..., doreturn=False)` com **mesmos recortes RGBA, offsets, ordem e blend**, preservando `_blit_visivel` individual para regressao.
2. `pixelrush_world_v3130.py`: somente o ramo de dano SDF agrupa blits dos mesmos strips antes do `damage.apply` original.
3. `pixelrush_qa_android_v327728.py` / `pixelrush_qa_async_export_v327737.py`: resumos por modo/bioma usam snapshots imutaveis das deque; percentis/ordenacao agora executados pelo worker em exportacoes periodicas; `relatorio()` sincronico ainda retorna contrato anterior para consultas e diagnostico. JSON/CSV passam a `v327738`. Flush final ainda bloqueia para nao perder dados.
4. Identificador QA e versionCode: `v3.277.38-QA-ANDROID-RC` e `327738`. Testes pygame dedicados `tests/test_qa_perf_v327738.py`.

**Equivalencia local inicial**: pygame-ce 2.5.8 em SDL dummy, 192 comparacoes RGB/RGBA com alpha e colorkey, mais 300 offsets do strip com byte a byte identico. Isso valida a primitiva de lote; os testes de integracao do CI e o aparelho Android sao gates separados.

## Bloqueios e proximos gates

- **Nao declarar ganho de FPS** antes de comparar os JSON/CSV `v327738` com os da v3.277.37 no mesmo aparelho, temperatura e periodo de corrida; medir p50, p95 e p99 de camera, profundidade, mundo, apresentacao, FPS e RSS.
- Se a camera continuar dominante, realizar experimento GLES em branch separada com equivalencia full-frame em Android, custo upload + composicao + swap e fallback. Nao habilitar pelo resultado Linux.
- Comparar corrida normal, replay e tutorial; validar pixels e ausencia de regressao, e inspecionar integridade ARM64, zip, DT_NEEDED e alinhamento de 16 KiB no APK resultante.
- Nao declarar as 32 frentes concluídas: **1, 3, 4, 5, 8, 12, 20, 25, 26, 28, 29 e 32** ainda tem pendencias materiais (algumas parcialmente executadas).

## Preservacao e limites

Todos os commits desta rodada foram feitos **somente** em `qa/android-full-performance-v3.277.38`. Nao tocar em main, DEV, branch de producao, assets, saves, pets, compras, fisica, controles, colisao, tutorial, shaders habilitados ou workflow AAB. Arquivo `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py` foi modificado na **copia da branch QA**, exclusivamente para mudar a string de versao. Nenhum benchmark Linux autoriza homologacao Android.
