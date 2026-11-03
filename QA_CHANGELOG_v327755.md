# PIXEL RUSH v3.277.55-QA — SRCALPHA e scroll 2.5D byte-exatos

**Branch:** `qa/android-full-performance-v3.277.55`  
**Base:** `qa/android-full-performance-v3.277.54`  
**Versão QA:** `v3.277.55-QA-ANDROID-RC`  
**Metadados Buildozer:** `3.277.55` e `327755` (sem execução do empacotador).

## 1. Otimizações efetivas no compositor SRCALPHA da Cidade

### Clipping seguro em normal/flow
- `pixelrush_city2_v3124.render_scene` estabelece contexto temporário apenas para `normal` e `flow`, pois nesses passes um `target.fill(...,alpha=255)` preenche toda a tela técnica antes da primeira camada. O escopo é restaurado em `finally`, inclusive se o SDL levantar erro; nenhuma marcação sobrevive à renderização.
- `pixelrush_city2_v3118._render_chunk` usa os bounding boxes de alfa calculados no boot para essas duas rotas SRCALPHA **somente quando o contexto opaco é garantido**. Em `image`, `geometry`, `fxmask` e demais mapas SRCALPHA não garantidamente opacos, continua com todos os pixels e blits legados, inclusive RGB com alfa zero.
- No quinto quadro normal da Cidade, o renderizador deixa de construir metadados e tuplas para um clipping por alfa que nunca seria permitido no `image` SRCALPHA. Os frames preservam a resolução, sprites, composição, câmera e efeitos.
- Rollback individual via `PIXELRUSH_QA_TECH_OPAQUE_BOUNDS=0`.

### Escalas 900×500 deduplicadas por bytes exatos
- `pixelrush_city2_v3118` agrupa fontes imutáveis de `geometry`, `fxmask`, `normal`, `material` e `flow` por formato, dimensões, máscaras, flags SDL, alpha global e hash BLAKE2b da memória crua. O hash **não** autoriza compartilhamento sozinho: compara o buffer inteiro em seguida, byte por byte, inclusive RGB oculto.
- Somente fontes confirmadamente iguais usam a mesma chave canônica no cache LRU de texturas escaladas. Uma substituição da Surface por outra identidade desativa o alias daquele mapa. A imagem principal e os sprites não são deduplicados.
- A análise acontece no boot, não no quinto quadro, e não mantém cópias de pixels de 450×250 na memória. Medição de RSS e ganhos na corrida real ficam pendentes.
- Rollback via `PIXELRUSH_QA_CITY_DEDUP_TECH_SCALED=0`.

## 2. Scroll incremental 2.5D — integridade antes de velocidade

**Descoberta SDL-RLE:** em teste direcionado pygame-ce 2.5.8, uma origem com `RLEACCELOK/RLEACCEL` não preserva necessariamente RGB oculto ao passar por um buffer `BLEND_RGBA_MAX`. O blit original pode deixar o RGB do destino com alfa zero intocado, ao contrário do buffer intermediário. Esse caso precisa ser tratado como **incompatível**, não como melhoria concluída.

- `pixelrush_qa_incremental_scene_v327750` agora detecta as flags RLE **antes de criar o cache de scroll** e retorna ao `CityPilotScene._render_chunk` original. A função mantém um contador `cidade_rle_direto`. Esta é a rota segura para os atlas de imagem que usam a aceleração SDL-RLE já existente.
- Fontes não-RLE compatíveis continuam podendo usar scroll + reconstrução de faixa. O blit do buffer já não cobre indiscriminadamente todos os 450×500: respeita exatamente a largura visível do chunk, preservando RGB invisível do alvo fora dos limites originais da imagem.
- Para menos de 192 pixels de cobertura, usa o blit do atlas diretamente em vez de preencher/compor um buffer extra. Limite `PIXELRUSH_QA_SCROLL_MIN_COVER` configurável entre 0 e 450, padrão seguro 192 inclusive se o valor de ambiente for inválido. Saltos grandes, fallback de formato/alpha, limite de dois buffers por cena e trim RSS continuam preservados.
- **Scroll continua desativado por padrão:** `PIXELRUSH_QA_CITY_INCREMENTAL=0` e `PIXELRUSH_QA_CLASSIC_INCREMENTAL=0`. O caminho cacheado não foi promovido à corrida real sem o gate de custo final.

## 3. Evidências direcionadas, sem homologação final

Executados apenas ensaios isolados de primitivas pygame-ce 2.5.8, sem rodar o jogo completo:
- 20 comparações de recorte de regiões de origem sobre canais SRCALPHA previamente preenchidos com alfa 255: RGBA idêntico.
- 512 composições de scroll com cobertura original, incluindo fundos com alfa zero e RGB oculto, em origens **sem RLE**, com bytes RGBA iguais.
- Detectada divergência de RGB oculto em teste propositalmente adversarial de SDL-RLE; o código foi protegido com fallback obrigatório, sem tentativa de aproximar os pixels.

**Gates adicionados para execução manual futura (não executados agora):**
- `tests/test_qa_srcalpha_scroll_v327755.py`: casos reais da Cidade, valores alpha 0/1/127/255, normal/flow, exceções que não podem vazar contexto, aliases de atlas, fallback RLE e scroll não-RLE com cobertura parcial.
- `.github/scripts/qa_benchmark_srcalpha_scroll_v327755.py`: CPU p50/p95, RSS, 96 quadros do mundo técnico e comparações independentes de scroll sem RLE e fallback RLE.
- `.github/scripts/qa_preflight_v327755.py`: integridade dos SHAs e sintaxe AST, políticas de clip/scroll, versão, arquivos protegidos e CI manual.
- `.github/workflows/qa-offline-v327755.yml`: apenas `workflow_dispatch`, sem Android, Gradle, Buildozer, ADB ou AAB. Testes legados v751/v753/v754 agora separam expectativas da rota SDL-RLE da rota experimental compatível, mantendo os próprios gates significativos.

## 4. Escopo e estado

**Frentes avançadas:** #2, #5, #7, #10, #16, #24, #25 e #26; **12/32 concluídas anteriormente offline, 20/32 ainda parciais**, sem aprovar novas frentes por presunção de FPS. Nenhuma medição Android, nenhuma homologação final, nenhum APK/AAB.

Alterações restritas à branch QA e aos módulos de composição/scroll, testes, scripts e metadados correspondentes. Preservados `main.py`, branch main, DEV, lógica do jogador, física 60 Hz, hitboxes, moedas, tutorial, HUD, pets, saves, skins, áudio, texturas, ordem dos sprites, clima, sombras, recursos 2.5D, zoom, política de cache 5:1 e workflows de produção.
