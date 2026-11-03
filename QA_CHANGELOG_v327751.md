# PIXEL RUSH — QA v3.277.51 (CPU/RAM compositor, scroll 2.5D)

Origem: `qa/android-full-performance-v3.277.50`.
Nova branch isolada: `qa/android-full-performance-v3.277.51`.
Metadados QA: `v3.277.51-QA-ANDROID-RC`, Buildozer `3.277.51` / `327751` (nenhum build Android feito).

## Código de execução realmente alterado (sem mexer em gameplay)

1. **Cidade noturna (#2/#7/#10/#18/#24/#26):** em `pixelrush_city2_v3124.py`, o filtro noturno deixou de criar uma Surface RGBA 450x500 por nível de noite e fazer um blit intermediário. Agora `target.fill((255-8*k,255-7*k,255-4*k,255),special_flags=pygame.BLEND_RGBA_MULT)` executa a mesma multiplicação sobre o destino em C/SDL. Isso elimina o buffer grande e o blit de overlay; no caminho anterior havia até **13 × 450 × 500 × 4 = 11.700.000 bytes lógicos** de Surfaces de véus por instância. O cálculo de `k`, ordem do efeito, iluminação, RGBA, clima e sprites não mudaram. Se `PIXELRUSH_QA_DIRECT_NIGHT_MULT=0` **antes do import**, o algoritmo antigo permanece acessível. Flag lida somente no boot, sem getenv no quinto quadro.
2. **Tiles da Cidade (#5/#16):** `pixelrush_city2_v3118.py` substitui o recorte manual por `target.blit(tex,(x,0))` com clip nativo SDL e rejeição de tiles invisíveis antes de criar/buscar a textura. Não muda quantização, camada, material, clima nem sprites. `PIXELRUSH_QA_CITY_NATIVE_CLIP=0` (configuração de boot) mantém o método original. Menos `pygame.Rect` temporários e custo Python no quinto frame.
3. **Scroll 2.5D (#5):** `pixelrush_qa_incremental_scene_v327750.py` agora abrange chunks **com sprites**, reaproveitando a base de textura e chamando o `_render_chunk(...,only_sprites=True)` original para desenhar cada sprite com animação, transformações, vento, cor e ordem intactos. A atualização incremental permanece **OFF por padrão** (`PIXELRUSH_QA_CITY_INCREMENTAL=0` e `PIXELRUSH_QA_CLASSIC_INCREMENTAL=0`). Não seria responsável declarar ganho de FPS sem medir custo da Surface extra, scroll e blit completo.
4. **Memória e 5º quadro (#25/#26):** `pixelrush_qa_render_v327729.py` registra último frame/bioma de uso de cada mapa de pós-processamento (normal/geometry/flow/material/fxmask), sem guardar Surface nova. `pixelrush_qa_cache_trim_v327748.py` deixa de descartar mapas ainda usados no compositor; mapa frio continua elegível para limpeza parcelada por RSS. Evita ciclos caros de desalocar/recriar texturas de 450×500 em períodos de alta pressão. Preserva multi-instância, política de GC e escalonamento de limpeza fora do quinto quadro.
5. **Segurança de máscaras de geometria (#7/#24):** `pixelrush_city2_v3124.py` e `pixelrush_biomes2_v3128.py` validam bits, máscaras RGB e SRCALPHA antes de reciclar `_geometry_view`, copiando na troca de formato para preservar bytes.

## Ensaios pontuais de desenvolvimento (NÃO homologação final)

Em pygame-ce **2.5.8**, SDL dummy local:
- **12 casos** de multiplicação da vinheta (RGB/RGBA, seis níveis de noite): `Surface.fill(BLEND_RGBA_MULT)` e `blit` do overlay uniforme renderizaram bytes RGBA idênticos.
- **56 casos** de recorte de tile (Surface/target RGB ou RGBA, posições internas e fora do viewport): `blit` direto com clipping SDL e blit com `pygame.Rect` deram RGBA idêntico.

Não foi executada a nova suíte do repositório nem benchmark com corrida completa. Não há resultado de FPS Android nem prova de melhoria p95 de CPU no smartphone.

## Gates preparados, sem execução final

- `tests/test_qa_hotpath_v327751.py`: compara render noturno real do bioma, recorte nas bordas, chunks com sprites e proteção de mapas FX ativos; verifica paridade RGBA.
- `.github/scripts/qa_benchmark_hotpath_v327751.py`: p50/p95 de CPU, RSS, RGBA de cenas, estimativa de buffers evitados (sem afirmar ganho Android).
- `.github/scripts/qa_preflight_v327751.py`: fonte protegida, versões, hashes, API de rollback, workflow manual.
- `.github/workflows/qa-offline-v327751.yml`: gatilho `workflow_dispatch` apenas, mantendo regressões anteriores e sem build Android/ADB.

## Preservado

`main.py`, branch `main`, DEV, física, controles, HUD, tutorial, moedas, obstáculos, gameplay, saves, pets, assets, audio, política 5:1 do cache de fundo, shaders de produção e todos os workflows APK/AAB. Nenhum APK/AAB/Android nesta versão.

**Placar honesto:** continuam 12 frentes concluídas anteriormente offline e 20 parciais; v751 melhora caminhos reais de várias parciais mas NÃO as declara prontas sem regressão integrada e medição Android.
