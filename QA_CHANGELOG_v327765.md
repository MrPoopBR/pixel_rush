# PIXEL RUSH — Changelog v3.277.65-QA

Continuidade na mesma branch qa/fechamento-32-v3.277.57. Partindo de v3.277.64.

#25 RAM: Novo pixelrush_qa_memory_budget_v327765.py contabiliza Surfaces SDL por identidade única em caches de World/Cidade/biomas modulares e fonte compartilhada. Integrado no fluxo de trim parcelado após apresentação, na mesma sondagem do quadro 181 mod 180: pressão de cache aciona evicção fria mesmo antes de atingir limite RSS. Teto aproximado conservador, sem truncar memória ativa. Guardas de cache quente e prebake Neve mantidas, fallback PIXELRUSH_QA_SURFACE_BUDGET=0. Nenhuma alocação adicional de superfície.

#4 pós-processamento: 2 gates de RGBA pixel-exato no finalizador já chamado pelo loop real, comparando câmera ativa/inativa, escalas, LRU, alfa oculto e self-blit com legado. Não unifica GPU/CPU por presunção, só valida implementação CPU.

5 testes adicionados aos 33 existentes, preflight AST/SHA e metadados de versão atualizados. Sem APK/AAB/Android; não alterados main, DEV, pets, saves, física, gameplay, qualidade visual, assets, drivers, shaders ou workflows de produção. Situação pré-gate: 17/32 fechadas offline, 15 parciais.
