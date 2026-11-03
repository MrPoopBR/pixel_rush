# PIXEL RUSH — Changelog consolidado de fechamento v3.277.57-QA

**Branch de integração única:** `qa/fechamento-32-v3.277.57`  
**Base:** `qa/android-full-performance-v3.277.56`  
**Versão registrada:** `v3.277.57-QA-ANDROID-RC`, Buildozer `3.277.57`, numeric_version `327757`.  
**Sem homologação final, APK/AAB, ADB, Gradle, Buildozer ou Android.**

## Mudanças nesta branch, em vez de mais versões intermediárias

1. **#2/#7/#10/#24 — CPU/RAM do quinto quadro:** `pixelrush_qa_render_v327729.py` reutiliza a Surface técnica `geometry/normal/material/flow/fxmask` já renderizada quando estado completo, mesma World, mesma cena, mesmo objeto Surface e mesmo frame coincidem. Usa weakrefs para não prolongar recursos de biomas antigos. Não toca `image` nem `foreground_only`; se qualquer campo ou instância mudar, renderiza de novo. Flag `PIXELRUSH_QA_TECH_SAME_FRAME=0` restaura a chamada anterior.
2. **#16/#10 — recorte modular real:** tanto o renderizador original de Neve `pixelrush_biomes2_v3128.py` quanto o de Deserto `pixelrush_biomes2_v3130.py` deixam de preparar o segundo tile que inicia exatamente em x=225 fora da Surface de 225px. `pixelrush_qa_modular_batch_v327744.py` recebeu a mesma guarda, com contadores. Todos os demais deslocamentos usam a mesma composição original. O ganho é pontual e pixel-exato, não remoção das camadas.
3. **#26 — GC cooperativo integrado:** novo `pixelrush_qa_gc_cooperativo_v327757.py` instalado pelo render QA após outros wrappers de flip, exclusivamente com `PIXELRUSH_QA_ANDROID=1`. O GC cíclico roda em quadros 1 mod 5, com intervalos 30/180/900. Não executa `gc.collect()` no redraw 5:1. A retirada do módulo restaura `pygame.display.flip` e modo automático de GC; rollback `PIXELRUSH_QA_GC_COOPERATIVO=0`. A implementação não modifica o GC de referência/refcount. **Sem comprovação de ganho de FPS/RSS Android.**
4. **#22 — pré-carga de skins/pets sem mexer na corrida:** novo `pixelrush_qa_precarregamento_visual_v327757.py` conectado à engine Android QA. Prepara arte das skins ativas e tenta pré-carregar o pet equipado durante telas de menu, um item por oito quadros, sem RNG alterado, compras antecipadas ou saves. A classe de pets atual `PetStudioPlayer` é placeholder e não renderiza pets; portanto #22 continua parcial em arte real de pets.
5. **#23 — atlas e tiles PROD:** `pixelrush_qa_atlas_io_v327747.py` estende a leitura streaming SHA já presente para os três arquivos de tiles PROD, respeitando o orçamento total e não gerando Surfaces/pickle/cena antecipada nem sorteando bioma. `PIXELRUSH_QA_TILES_IO_PREWARM=0` reverte a adição.
6. **Metadados:** `VERSAO_ATUAL.txt`, `buildozer.spec` e somente `VERSAO`/gancho de pré-carga na engine QA. Nenhuma alteração ao entrypoint `main.py`, ao driver de produção/DEV ou ao fluxo AAB.

## Testes direcionados realmente executados nesta operação

- `pygame-ce 2.5.8`, SDL dummy, Python 3.13: **3/3 testes locais aprovados**, testando (a) pré-carga apenas no menu com estado RNG preservado, (b) 901 flips de GC cooperativo sem coleta programada no quinto frame, e (c) equivalência RGB/RGBA sintética quando se omite um tile completamente fora da superfície. Ambos os módulos de GC/pré-carga locais passaram por `ast.parse`.
- Foram criados **gates novos de código real**, mas **não executados** nesta operação: `tests/test_qa_fechamento32_v327757.py` (multi-instância, RNG/precarga, GC, page-cache/sha) e `tests/test_qa_fechamento_modular_v327757.py` (funções reais de Neve/Deserto). O script `.github/scripts/qa_preflight_v327757.py` verifica AST/SHA, versão e integração. Workflow `.github/workflows/qa-offline-v327757.yml` somente `workflow_dispatch`, sem construir binário Android.
- Sem medir FPS Android, sem comparar todo frame do jogo e sem concluir gates dependentes de GLES/NEON/PBO/VSync.

## Estado objetivo das 32

Todas as **32 frentes foram revisitadas** e estão discriminadas no `QA_TRACKER_32_v327757.md`. Na avaliação conservadora desta integração: **13/32 concluídas em implementação/QA offline (12 anteriores + GC #26)**; **19/32 ainda exigem conclusão real ou gates adicionais**. O objetivo 32/32 **ainda não foi alcançado**; não reclassificar código opt-in incompatível ou sem prova como uma implementação pronta.

**Preservado:** física e ticks, movimentos/obstáculos, visuais e RGB oculto, shader/iluminação, política 5:1, HUD, tutorial, pets e saves, gameplay, DEV/produção, áudio, recursos e workflows APK/AAB. Todo o trabalho está apenas na branch QA isolada, sem merge em main.
