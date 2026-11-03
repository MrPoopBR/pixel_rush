# Auditoria SOMENTE LEITURA da PIXEL RUSH v3.277.51-QA — 20 frentes parciais

**Fonte auditada sem modificações:** `qa/android-full-performance-v3.277.51`; tracker `QA_TRACKER_32_v327751.md`, compositor `pixelrush_world_v3130.py`, Cidade `pixelrush_city2_v3118.py`/`v3124.py`/`v3125.py`, Neve/Deserto `pixelrush_biomes2_v3128.py`/`v3130.py`, render QA `pixelrush_qa_render_v327729.py`, rolagem `pixelrush_qa_incremental_scene_v327750.py`, limpeza de caches `pixelrush_qa_cache_trim_v327748.py` e gate 32 anterior.

**Natureza:** análise estática qualitativa; impacto esperado NÃO é benchmark nem demonstra FPS. A v3.277.51 não foi modificada; este relatório fica somente na branch sucessora isolada v3.277.52. Nenhum Android/CI/APK envolvido nesta auditoria.

**Escala:** impacto potencial **A** (alto), **M** (médio), **B** (baixo); dificuldade de implementação e risco visual/funcional **B/M/A**. O risco considera efeitos em pixels, transparência, UI, RNG, saves ou driver. É estimativa técnica baseada no código, não resultado medido.

| Frente | Melhoria parcial | Impacto | Dificuldade | Risco | Evidência no código v751 / próximo gate |
|---:|---|:---:|:---:|:---:|---|
| 1 | Zoom GPU | A | A | A | Presenter GLES opt-in; shaders GLES/CPU divergem em casos conhecidos; exigir byte-exato e latência física |
| 2 | Compositor 2.5D persistente | A | A | A | Redraw real da Cidade a cada quinto frame; transições, clima, noite e sprites são variáveis de invalidação |
| 3 | CPU/GPU híbrido | A | A | A | Ponte CPU staging -> GLES desativada; uploads podem exceder custo SDL; entrada/HUD precisam paridade |
| 4 | Zoom/pós-processamento unificado | M/A | A | A | Sequência QA v750 unificada na apresentação, mas câmera/GameFeel e GLES têm fases e superfícies próprias |
| 5 | Scroll incremental | A | A | A | `_render_chunk` tem caminho experimental, mas Surface extra 450×500, sobreposição alfa e LRU de 2 entries não foram homologados |
| 7 | Evitar grandes alocações | A | M | M | Geometry e vinhetas Cidade já otimizadas; Neve/Deserto mantêm overlays/cópias de texturas diurnas |
| 8 | SIMD smoothscale | M | A | M/A | Alternativa experimental necessita prova RGB/RGBA e AArch64 real; fallback original correto |
| 10 | Remover cópias/passes | A | M | B/M | Mapa geometry copia 450×500 no caminho GPU e Neve/Deserto blitam overlay meteorológico transparente no tempo limpo |
| 12 | Backend por dispositivo | M/A | A | A | Gate v747 rejeita backend não provado; não selecionar por heurística sem igualdade pixel |
| 16 | Culling | M | M | B/M | Cidade faz clip SDL; modular sempre consulta 2 tiles por camada, mesmo quando segundo invisível em shift=0 |
| 18 | Céu/clima | M | M | M | Cidade usa hoist de coordenadas; modular em clima sem precipitação ainda limpa/blita `_weather` vazio |
| 20 | Pool chuva/neve/partículas | M | M | M | Clima modular desenha em buffer preexistente; otimizar apenas ausência inequívoca, preservar contagem/ordem |
| 22 | Pré-carregamento skins/pets | M | A | A | Caches prévios existem; não tocar sem revalidar saves, inventário, desbloqueios e uso real de pets |
| 23 | Pré-aquecer biomas | M | M/A | M/A | I/O de atlas aquecido, mas próxima cena depende de sorteio; nunca antecipar RNG nem carregar sete biomas |
| 24 | Deduplicar Surfaces | A | M | M | Níveis diurnos modulares copiam o mesmo tile imutável; fonte src já tem pixels finais |
| 25 | Limites globais de cache | M/A | M | M | Trim RSS protege mapas quentes, pode realocar Surface ao mudar bioma; precisa benchmark |
| 26 | Pausas GC | M | A | M | Observador existe, não há evidência de GC como causa principal; reduzir alocação antes de mudar thresholds |
| 28 | Native/Cython seletivo | M/A | A | A | NEON/camera experimento, ABI e pixel-exatidão Android ainda pendentes |
| 29 | Uploads GPU | M/A | A | A | PBO GLES3 experimental, custo e sincronização/driver real não verificados |
| 32 | VSync/driver/Perfetto | M/A | A | A | Instrumentação sem Perfetto de aparelho; alterar cadência sem medição causaria regressão |

## Sequência de menor risco e maior ganho esperado

**Onda 1 (código real, sem premissas de GPU):** #10/#18/#20 ignorar somente overlay meteorológico vazio em Neve/Deserto; #24/#7 compartilhar o tile original no nivel 0, sem cópias RGBA; #2/#10 evitar cache de plano sem hits na corrida SDL; #16 culling onde totalmente invisível. Também corrigir exceções na iteração de tiles, sem mexer em animações.

**Onda 2 (integração condicional com gate):** #7/#10/#24 compartilhar o próprio buffer de geometry apenas quando pertence ao `LivingWorld._city_surfaces`, respeitando _geometry_view/ambient_occlusion e flag OFF até prova; #5 rediscutir scroll por plano de camada, porque cache por variante e blit extra podem perder desempenho.

**Onda 3 (hardware/funcional):** #1/#3/#4/#8/#12/#28/#29/#32 exigem Android real e testes de shader/swap/pacing; #22 precisa fixtures reais pets/saves; #23 exige uma forma de saber o bioma futuro sem alterar aleatoriedade. Não declarar nenhuma dessas como concluída em laboratório.

## Decisão da auditoria
**Placar histórico auditado v751: 12 concluídas offline, 20 parciais; não há FPS Android validado na revisão.** A nova v752 pode avançar somente onde o código preserva a ordem, bytes e funções. Este documento não aprova nenhum gate nem altera a fonte v751.
