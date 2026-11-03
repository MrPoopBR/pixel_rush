# PIXEL RUSH v3.277.47-QA — pré-aquecimento sem memória e gate de backend

Branch: `qa/android-full-performance-v3.277.47`  
Base: `qa/android-full-performance-v3.277.46`, commit `cefe204e95a218fc17e39616770352cca86c3354`.  
Versão no código QA: `v3.277.47-QA-ANDROID-RC`; Buildozer `3.277.47`, numeric `327747`.  
**Não construir APK/AAB nem executar teste Android.**

## Código entregue
1. `pixelrush_qa_atlas_io_v327747.py`: streaming SHA-256 dos atlas *existentes* de neve/deserto, com blocos de 64 KiB e orçamento máximo de 125 MiB lidos. Pode rodar **antes da corrida** durante a instalação QA, não instancia SDL, não escolhe bioma nem altera RNG. O resultado fica apenas como diagnóstico; as páginas de arquivo são administradas pelo SO e seu reaproveitamento não é garantido. `PIXELRUSH_QA_ATLAS_IO_PREWARM=0` desabilita. Isso não duplica cenas, skins, pets nem limites de RAM.
2. `pixelrush_qa_render_v327729.py`: invoca somente o pré-aquecimento de **I/O** na instalação isolada QA, anterior ao loop. Todo o desenho de mundo e HUD permanece original.
3. `.github/scripts/qa_buffer_stage_v327747.py`: investiga onde os caminhos de fundo direto e offscreen divergem; reporta o **primeiro estágio RGBA** (parallax, profundidade, clima, cenas, HUD) e pixels discrepantes, sem aprovar a alternativa. `tests/test_qa_buffer_full_v327746.py` sincroniza estado RNG antes das atualizações individuais, sem mudar o jogo.
4. `pixelrush_qa_backend_gate_v327747.py`: política conservadora para GLES2/GLES3, PBO, zoom e CPU híbrida. Considera paridade RGBA, compatibilidade de entrada/HUD e desempenho real; rejeita substituir SDL Surface sem esses gates. Integração de GPU na corrida não foi ativada. Testes mockados e SDL cobrem recusa e laboratório.
5. Suites `tests/test_qa_atlas_io_v327747.py`, `tests/test_qa_backend_gate_v327747.py`, novo workflow de QA offline e preflight com hashes, verificações pygame-ce 2.5.8 e relatório JSON de divergência.

## Status das 32 frentes
Consulte `QA_TRACKER_32_v327747.md`. Critério estrito: **não declarar 32/32 concluídas** sem integração real no render e testes de equivalência. O pacote precedente tem 12 frentes concluídas em código/QA offline, 15 parciais, 5 pendentes. A leitura de atlas e a arbitragem GPU são avanços seguros **dentro** de frentes parciais, não certificações de FPS Android.

## Integridade
Nenhuma mudança na frequência 1:5 do cache, sorteio de bioma, física, renderização, câmera real, zoom, partículas, clima, controles, som, menus, pets, saves, assets e shaders. O arquivo principal tem **somente o identificador de versão** modificado; novas rotinas residem em módulos QA separados. GPU experimental off. Main/DEV/produção e AAB intocados. Nenhum novo pacote exigido para Android.
