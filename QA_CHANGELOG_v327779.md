# PIXEL RUSH v3.277.79-QA — Fechamento de integração runtime (sem APK)

Branch: `qa/fechar-32-runtime-v3.277.79` sobre v3.277.78-QA.

## Mudanças aplicadas
1. **Correção de GC periódica:** coletas antes coincidiam com redraw pesado a cada cinco quadros; agora ocorrem em 30k+2, fora da fase pesada tanto 5:1 quanto 8:1. Janela com 902 flips preserva 25 GC0, 4 GC1 e 1 GC2, sem acumular duas coletas no mesmo flip.
2. **Gerenciamento de memória:** passos de trim nunca acontecem nas fases 1 mod5 / 1 mod8, e a sonda RSS vai para quadro 182 (antes 181).
3. **GLES/EGL:** corrigido acesso `ctypes.util` a partir de alias não importado no presenter, que causaria `NameError` ao inicializar.
4. **Perfil agressivo Android QA:** conecta ao runtime os backends já criados (GLES3 zoom, CPU/GPU, PBO, City/classic incremental, SIMD e ATrace), com tentativas de fallback e flags individuais de rollback. Não altera seleção em produção, DEV ou desktop.
5. **C/NEON:** preflight da câmera nativa real no boot agora é chamado uma vez fora do loop, com cena sintética colorida. Seleção somente se .so carregar, pixels forem iguais e mediana indicar ganho. Falha mantém o pygame original.
6. **Versão e provas:** `v3.277.79-QA-ANDROID-RC` / `version = 3.277.79` / `numeric_version = 327779`; regressões `tests/test_qa_runtime_v327779.py` e `tests/test_qa_cache_gc_v327758.py` atualizadas; workflows QA isolados.

## Garantias e limitações
A integração do backend não equivale a comprovação dos FPS/latência na Mali-G68. A rota GPU é experimental; seu uso depende de contexto GLES3, upload válido, shaders e frame completo sem erro. Nenhum APK foi compilado. Sem alteração intencional de física, colisões, jogador, saves, pets, tutorial, main, DEV, produção ou workflow AAB.

Ver tracker: `QA_TRACKER_32_v327779.md`. Estado conservador: **22 concluídas offline, 10 com integração ou alternativa experimental ainda não homologadas**.
