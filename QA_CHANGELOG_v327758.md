# PIXEL RUSH — changelog consolidado v3.277.58-QA

**Branch única de integração:** `qa/fechamento-32-v3.277.57` (avança de v757 para v758 na mesma branch, sem merge para main).

## Mudanças efetivas

1. **#25 — RAM e quadro de redraw:** adicionada `pixelrush_qa_cache_policy_v327758.py`, política por instância/bioma/quadro que preserva mapas técnicos ainda quentes e mapas sem marcador confiável. A mesma função passou a orientar tanto `EscalonadorTrimQA._aplicar` quanto `_reclaim_inactive_caches` quando o escalonador falha. O fallback anterior descartava indiscriminadamente todas as Surfaces técnicas, mesmo as usadas no frame atual, causando possível recomposição no quinto quadro. Agora só descarta as comprovadamente frias. Não mantém cópias de Surfaces nem muda pixels ou caches de imagem.
2. **#26 — GC:** coletas de geração 0, 1 e 2 permanecem fora dos frames múltiplos de cinco, mas são exclusivas no mesmo flip: a geração maior já inclui as menores. Nos primeiros 901 flips: 25 gen0, 4 gen1, 1 gen2, em vez de 30 + 5 + 1 chamadas. A destruição imediata por referência continua intacta; a restauração da política antiga permanece disponível.
3. **Gates:** ajustada expectativa legada do GC no `tests/test_qa_fechamento32_v327757.py` e criada suíte `tests/test_qa_cache_gc_v327758.py` para regressões de multi-instância, fallback, trim, RGBA e GC. Nenhuma funcionalidade opcional GPU/PBO/NEON foi forçada.

## Validação executada

- Ambiente local Python 3.13.5 + pygame-ce 2.5.8, `SDL_VIDEODRIVER=dummy`.
- **3/3 testes sintéticos passaram**: regra de frieza multi-instância; preservação de RGBA com 450×500; 901 apresentações pygame com 25/4/1 coletas e restauração de `display.flip` e GC.
- O teste da integração completa `tests/test_qa_cache_gc_v327758.py` foi **preparado e versionado, ainda não executado**, pois os módulos completos da branch não estavam disponíveis no container. Não afirmar FPS ou RSS Android.
- Sem APK, AAB, Buildozer, ADB, testes Android, merge em main ou homologação final. Física, aparência, jogabilidade, efeitos, pets, saves, DEV e produção não foram alterados.

## Placar da operação

**13 de 32 concluídas no critério offline e 19 ainda parciais**, nenhuma homologação Android. A #25 foi reforçada, mas continua parcial até comprovação agregada; #26 já era concluída offline. Consultar `QA_TRACKER_32_v327758.md`.
