# PIXEL RUSH v3.277.54-QA — render CPU/RAM, alpha bounds e scroll incremental

**Base:** `qa/android-full-performance-v3.277.53`  
**Nova branch isolada:** `qa/android-full-performance-v3.277.54`  
**Versão engine QA:** `v3.277.54-QA-ANDROID-RC`; `buildozer.spec`: `3.277.54`, `327754` (**somente metadados; sem APK/Android/AAB**).

## Mudanças implementadas NO código real

### 1. Culling do conteúdo RGBA estático da Cidade (frentes #2/#7/#10/#16/#24)

Em `pixelrush_city2_v3118.CityPilotScene`, durante a criação da cena, cada textura base SRCALPHA imutável das variantes de camada é classificada uma única vez por canal, incluindo o identificador da Surface na chave. Nenhum cálculo de bounding box ocorre no quinto quadro. A classificação só acontece em imagens sem colorkey e sem alpha global parcial:
- Alfa zero em toda a imagem: nenhum scale `450x250 -> 900x500`, nenhuma textura escalada no LRU e nenhum blit dessa base. A parte dinâmica de sprites continua desenhada na ordem histórica.
- Alfa parcial em regiões limitadas: SDL compõe exclusivamente o retângulo que contém os pixels com alfa maior que zero. O retângulo do atlas 450x250 recebe a mesma escala inteira 2x (nearest-neighbor); toda coordenada de desenho e sobreposição mantém a geometria antiga.
- Texturas não enquadradas nas condições continuam com o blit inteiro de antes. O recorte/clipping SDL e os caminhos técnicos RGB/normal/flow permanecem.

As flags `PIXELRUSH_QA_CITY_EMPTY_BASE=0`, `PIXELRUSH_QA_CITY_ALPHA_BOUNDS=0` e `PIXELRUSH_QA_CITY_SPRITE_RIGHT_CULL=0` restauram de forma independente o desenho de bases invisíveis, o blit não recortado e o culling original de sprites. Na borda direita, a checagem de posição do sprite é feita antes de buscar sua textura, quando comprovadamente não pode cobrir pixels da viewport; do lado esquerdo continua a verificação baseada na largura real.

### 2. Evitar criação de tuplas sem consumidores em canais técnicos (#10/#26)

Em `pixelrush_city2_v3124.render_scene`, a camada `near` gera uma tupla de tiles apenas nos canais `image` e `fxmask`, nos quais `draw_windows_lights` a utiliza. `normal/geometry/material/flow` percorrem diretamente o gerador, sem materializar a lista intermediária. Não muda a sequência, ordenação, vento, sombreamento ou uma única operação visual. `PIXELRUSH_QA_NEAR_PLAN_ON_DEMAND=0` restaura o método antigo.

### 3. Scroll experimental com fallback direto em saltos (#5/#7/#10/#24)

`pixelrush_qa_incremental_scene_v327750`, conectado a `CityPilotScene._render_chunk` pela instalação QA, evita duas passagens redundantes:
- Uma Surface `pygame.SRCALPHA` nova já começa zerada; não faz mais um `fill` de 450x500 para limpar pixels que já são (0,0,0,0). Usa `PIXELRUSH_QA_SCROLL_INIT_CLEAR=0` para retornar à limpeza explícita.
- Se uma variante muda mais de 48 pixels entre renders, reconstruir seu cache com `fill` + cópia RGBA + blit final 450x500 desperdiçaria CPU. A v754 descarta a entrada e chama o mesmo blit do atlas de origem, sem mover a camada ou seus sprites. `PIXELRUSH_QA_SCROLL_JUMP_DIRECT=0` permite testar a reconstrução antiga.
- Para deslocamentos pequenos, a cópia exata de faixas e a composição SRCALPHA permanecem intactas, com `BLEND_RGBA_MAX`; até dois buffers por instância, escalonador RSS v753 e escopos `static/all` intactos.

**Scroll NÃO ativado por padrão:** `PIXELRUSH_QA_CITY_INCREMENTAL=0` e `PIXELRUSH_QA_CLASSIC_INCREMENTAL=0`. Sem benchmark final de custo completo e igualdade RGBA na corrida, não declarar acelerado nem concluído.

## Verificações Pygame-ce 2.5.8 pontuais (sem homologação final)

Executadas como ensaios de primitivas SDL locais, não como teste do jogo inteiro:
- 72 comparações de blit completo versus `bbox` escalado 2x, em targets RGB e RGBA com diferentes deslocamentos: bytes RGBA idênticos.
- Blit de atlas com alfa completamente zero não modificou os pixels de destino RGB/RGBA nas amostras.
- Dez novas Surfaces `SRCALPHA` 450x500 com máscaras SDL normais iniciaram transparentes.
- Buffer RGBA intermediário com cópia `BLEND_RGBA_MAX` e blit final coincidiu com o blit direto nas posições de borda examinadas.

São evidências restritas à equivalência de operações SDL: **não comprovam paridade do jogo real em todos os climas/efeitos**, não medem FPS do smartphone, não garantem economia RSS/CPU final. O algoritmo de scroll continua opt-in OFF.

## Gates criados, não executados nesta entrega

- `tests/test_qa_alpha_bounds_scroll_v327754.py`: compara Cidade v3125 real com e sem culling de bases, alpha bounds, sprite culling e tupla near em RGB/RGBA e seis canais; testa saltos do scroll e fallback histórico.
- `.github/scripts/qa_benchmark_alpha_scroll_v327754.py`: 96 quadros de canais reais Cidade + 90 comparações de scroll com saltos; p50/p95/max CPU, RSS e hashes de pixel equivalentes. Sem inferir FPS Android.
- `.github/scripts/qa_preflight_v327754.py`: versionamento, hashes Git de código protegido, sintaxe, flags de retorno, CI exclusivo/manual e ausência de tarefas de APK/Android.
- `.github/workflows/qa-offline-v327754.yml`: **somente `workflow_dispatch`**, prepara regressões v748–v753 e nova v754; nenhum gatilho por push e nenhum passo de Gradle, ADB ou Buildozer.

## Integridade e progresso das 32 frentes

**Placar continua 12 concluídas anteriormente offline, 20 parciais.** As mudanças v754 avançam especialmente #2, #5, #7, #10, #16, #24 e #26. #1/#3/#4/#8/#12/#28/#29/#32 não podem ser aprovadas pela mera presença de módulos GPU/driver laboratoriais. Sem FPS Android alegado.

Modificações isoladas à branch QA nos módulos de render solicitados `pixelrush_city2_v3118.py`, `pixelrush_city2_v3124.py`, `pixelrush_qa_incremental_scene_v327750.py`, em metadados da versão e em novos scripts/testes/documentos. Sem alteração em `main.py`, DEV, física, gameplay, HUD, controles, tutorial, pets, skins, saves, áudio, sprites, assets, política 5:1, trabalho de produção ou workflows de APK/AAB. Nenhum APK, AAB, teste Android ou homologação final.
