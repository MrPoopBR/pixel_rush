# PIXEL RUSH v3.277.77-QA — diagnosticos R11 aprofundados, SEM APK

**Branch isolada inalterada:** `qa/r11-passes-v3.277.76`; nome historico da branch continua v776, codigo QA atual v3.277.77-QA-ANDROID-RC, buildozer.spec 3.277.77 numericVersion 327777.

## Evidencias e decisao de gate
- R11 Galaxy A54 SM-A546E: corrida normal ~8,3 FPS; pos-sprites p50 64,668 ms; mundo 2.5D p50 88,631 ms por execucao. Valores do APK anterior, **nao** da v777.
- Perfil pygame-ce Linux de 42 renderizacoes City (5 updates/1 desenho): world.draw p50 ~0,390 ms; tempo agregado chunk ~0,1966 ms por desenho, scale/cache ~0,0279 ms por desenho. Tempos inclusivos, nao somar.
- Experimento views da vinheta GameFeel, 750 repeticões e byte-RGBA em RGB16/24/32/SRCALPHA: 0,9994x; 0,9990x; 0,9938x; 1,0001x no CI #41901724627. **Sem ganho provado. Rejeitado e NAO integrado.**
- NOVO: dentro de `pixelrush_city2_v3118._render_chunk`, medir `r11_city_chunk_base` (blit do atlas) e `r11_city_chunk_sprites` (sprites decorativos). `try/finally` preserva o fechamento do marcador em excecoes. Apenas QA Android. Rollback: `PIXELRUSH_QA_R11_CHUNK_PASSES=0` no boot.
- Telemetria QA `pixelrush_qa_android_v327728.SECOES` ampliada com os dois marcadores. Teste de City real e RGB oculto `tests/test_qa_r11_chunk_trace_v327777.py` + suites anteriores.
- Otimizacoes v776 (4 faixas da vinheta, bbox City apenas RGB16 opaco) permanecem SEM alteracao; nao introduzir atalhos sem ganho comprovado. O gargalo no A54 depende da GPU/CPU reais, aguardando R12.

## Escopo
Somente QA nesta mesma branch, medidores e textos de versao. Nenhuma alteracao fisica, gameplay, visual, ordem de sprites, efeitos, tutorial, pets, skins, saves, main.py, DEV, branch main ou AAB. Nenhum APK compilado. 22/32 melhorias concluidas offline e 10 parciais, sem homologacao das dez no A54.
