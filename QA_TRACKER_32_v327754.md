# PIXEL RUSH — Tracker auditado das 32 melhorias (v3.277.54-QA)

**Fonte inicial:** `QA_AUDITORIA_32_v327738.md`; reavaliação com código até v3.277.54 e evidências anteriores da v3.277.47.  
**Critério:** *concluída no código/QA offline* significa técnica presente e com testes focados; **não implica FPS Android comprovado nem todas as 32 homologadas**. *Parcial* significa atuação limitada a alguns cenários, flag OFF, falta de teste integral ou pré-carregamento não integrado; *pendente* significa proposta ainda não integrada ao render real.

**Resultado da integração em código (não homologação): 12/32 anteriormente concluídas offline (37,5%); 20/32 parciais (62,5%); 0/32 sem integração inicial. Total 32/32 catalogadas. A maioria ainda NÃO está concluída nem validada.**
**Homologação de ganhos em aparelho Android para esta versão: não realizada na v3.277.54, conforme solicitação do usuário.**

| # | Melhoria das 32 | Estado | Evidência e ressalva |
|---:|---|---|---|
|1|Zoom por GPU|Parcial|v749 integra wrapper de CameraCinematica com geometria de zoom original e shader fixo GLES em janela opt-in; flags OFF, paridade/ganho Android pendentes|
|2|Compositor 2.5D persistente|Parcial|v754 elimina escalonamento e blit de canais estáticos com alpha zero e limita blits aos bboxes opacos do atlas Cidade 450x250; quinto quadro continua redesenhando animações e camadas visíveis|
|3|CPU/GPU híbrido|Parcial|v749 cria ponte real CPU staging Surface -> GLES2 durante display.flip, preservando HUD/input SDL e fallback SDL, totalmente OFF por padrão|
|4|Unificação zoom/posprocessamento|Parcial|v750 chama pixelrush_qa_unified_post diretamente no loop real após gamefeel/GPU FX e engloba câmera, escala, blit e flip. Implementado no QA por padrão, caminho antigo preservado; ainda não elimina transformações GPU duplas e sem gate RGBA integral|
|5|Scroll incremental de pixels|Parcial|v754 no wrapper real Cidade abandona reconstrução de buffer 450x500 em saltos de >48 px e faz blit direto do atlas; evita clear inicial de Surface SRCALPHA. Opt-in OFF; paridade integrada/ganho CPU ainda sem aprovação|
|6|Recorte de transparências|**Concluída (offline)**|wrapper Fase B; culling RGBA testado|
|7|Evitar grandes alocações|Parcial|v754 reduz crescimento do LRU de texturas escaladas ao não preparar canais estáticos totalmente transparentes da Cidade; scroll evita limpeza e cópia full-frame em saltos. Outras Surfaces ainda alocadas|
|8|SIMD para smoothscale|Parcial|preflight offline/opt-in, fallback ativo, sem Android|
|9|Pré-composição de texturas|**Concluída (offline)**|atlas e superfícies estáticas presentes, testes de paridade|
|10|Remover cópias/passes|Parcial|v754 substitui blit completo da imagem estática por retângulo de conteúdo (bbox alpha) calculado no boot e ignora canais com alpha 0; remove materialização de tuple near em canais sem luzes. Mantém passes animados|
|11|Cache de menus|**Concluída (offline)**|fundo e prévias limitados, sem remoção de UI dinâmica|
|12|Backend por dispositivo|Parcial|gate CPU/GPU v747 tem testes offline de rejeição segura; seleção real permanece SDL CPU|
|13|Sprites espelhados|**Concluída (offline)**|cache de props integrado|
|14|Alpha overlays|**Concluída (offline)**|reuso de masks/transições implementado|
|15|FABRIK/deformação|**Concluída (offline)**|buffers QA integrados e limitados|
|16|Culling fora da tela|Parcial|v754 descarta sprites à direita antes de consultar a textura e limita blits SRCALPHA da Cidade aos pixels relevantes sem alterar clipping SDL; outros subsistemas ainda com trabalho visível|
|17|Agrupar blits|**Concluída (offline)**|Fase B/SDF/strips; modular atual opcional OFF, sem afirmar ganho dele|
|18|Cache céu/clima|Parcial|v752 pula caminho meteorológico vazio nos biomas modulares quando a família de partículas não se aplica ao clima; mantém efeitos ativos e ritmo de animação|
|19|Vinheta noturna|**Concluída (offline)**|v3192 mantém vinheta de faixas; v751 remove full-surface overlay multiplicativo da Cidade por fill BLEND_RGBA_MULT, com fallback e ensaio sintético RGB/RGBA|
|20|Pool chuva/neve/partículas|Parcial|v752 preserva contagem de partículas nas tempestades e reduz custo de buffer vazio em neve/deserto secos; pool completo ainda não foi integrado|
|21|Fontes/labels|**Concluída (offline)**|caches limitados com atualização por necessidade|
|22|Pré-carregamento skins/pets|Parcial|previews e caches existentes, pets não validados integralmente|
|23|Pré-aquecer biomas|Parcial|atlas PROD e API v746; v747 lê/valida os 4 atlas no bootstrap sem alocação SDL ou antecipar RNG; cena do próximo bioma não é conhecida antes do sorteio|
|24|Deduplicar Surfaces|Parcial|v754 não escala e não retém no LRU texturas estáticas vazias; scroll usa atlas direto para saltos em vez de reconstruir buffer extra. Deduplicação total e VRAM não comprovadas|
|25|Limites globais de cache|Parcial|v753 integra a eliminação dos caches de scroll da Cidade inativa ao EscalonadorTrimQA em lotes fora do quinto quadro, preservando mundo ativo e multinstância; sem medir RAM Android|
|26|Pausas GC|Parcial|v754 reduz temporários de planos near técnicos e evita criar texturas escaladas de canais vazios; parâmetros do GC não foram modificados e pausas Android ainda não foram medidas|
|27|Telemetria assíncrona|**Concluída (offline)**|worker JSON/CSV, snapshot parcelado, flush final preservado|
|28|Native/Cython seletivo|Parcial|câmera C/NEON experimental disponível, OFF até prova Android; sem Cython geral|
|29|Evitar uploads GPU|Parcial|v749 conecta PBO GLES3 ao presenter de janela real via flags opt-in GLES_BRIDGE+GLES3_CONTEXT+GLES_PBO; fallback para upload direto; não há benchmark Android|
|30|Apresentação final/SDL|**Concluída (offline)**|swap/cópias instrumentados; não comprova taxa de atualização Android|
|31|Atlas pré-aquecido|**Concluída (offline)**|atlas PROD SHA-256 verificados v32776 + tiles PROD v32777|
|32|VSync/driver/Perfetto|Parcial|sondas instrumentadas, Perfetto Android não coletado|

## Regra de aprovação definitiva
**A taxa 37,5% é de implementação/cobertura offline, NÃO uma taxa de otimizações validadas por desempenho no Android.** Para encerrar as 32 como pacote, falta a rodada única de homologação Android, mais gates de gameplay completo/performance/cadência. Não declarar resultados de testes de atlas base `world_v3130` como equivalentes a `world_prod_v32777`, nem confundir cenário Linux com frame real Android. Nenhum APK compilado nesta tarefa.

## Bloqueios técnicos específicos para concluir as 20 restantes

Para respeitar *absolutamente* as funções e pixels, os itens dependentes de GPU (#1, #3, #4, #5 e #29) não podem ser marcados como concluídos pela mera presença de classes experimentais. O renderer atual usa `pygame.display.set_mode` com `Surface`; o laboratório GLES abre outra janela e não fornece entrada/HUD compatíveis com a produção. O shader GPU também apresentou divergências de arredondamento no passado. O gate v747 recusa trocar a saída sem integração/igualdade total.

Nas 15 parciais, houve avanço: o boot QA pode aquecer o **page cache de arquivos** dos atlas com I/O limitado sem mudar a sequência aleatória (#23); o backend usa seleção conservadora por condições (#12); o quinto quadro possui ferramenta que identifica o estágio da divergência (#2/#10). Não há evidência suficiente para ativar buffers offscreen independentes (v746: neve 10/35 quadros divergentes, deserto 20/35), remover passagens que alterem transparência ou desabilitar efeitos sob pressão RSS.

**Gate de aceitação geral:** implementação + teste regressivo de caminho real + nenhum pixel divergente + manutenção de funcionalidades, antes de homologar ganho de FPS Android na rodada única final. O número de frentes **concluídas** permanece 12/32 se algum gate ainda falta. Este documento não confunde “preparado no código” com “ativo/mais rápido na corrida”.

**Evidência adicional v747:** teste de buffer com estado RNG sincronizado passou 35/35 RGBA nos três biomas, mas sua implementação não foi integrada ao jogo; #2/#10 continuam parciais até teste da apresentação real. Nenhum dos cinco itens dependentes de GLES/driver foi habilitado.

## Atualização v3.277.48 — modificações integradas (sem encerramento prematuro)

- **#25 / correlação do quinto quadro:** a chamada real de `pygame.display.flip` na branch QA agenda a limpeza sob RSS > orçamento no quadro múltiplo de 180, e trabalha em lotes de até 12 chaves nos frames seguintes que **não** são múltiplos de cinco. A limpeza antiga continua acessível se `PIXELRUSH_QA_STAGGER_TRIM=0`, import falhar ou surgir exceção. Antes: uma varredura grande inteira no 180º frame, simultânea ao redraw do cache do fundo.
- **#20 e pequena parte de #7:** o wrapper ativo `LivingWorld._weather` pré-calcula deslocamentos que são invariantes num quadro e reutiliza os tuples de sementes normais; não altera primitivas SDL, posições, RGBA, ordem, efeitos ou número de partículas. Não modifica o render de cidade/profundidade pesado.
- **#2 / #10:** somente houve trabalho diagnóstico anterior; compositor offscreen não foi integrado, porque a cópia adicional de superfície não tem ganho comprovado e ainda falta contrato com HUD/frame completo. Permanecem parciais.
- **#26:** não foi alterada a frequência de garbage collection, portanto não foi marcada como concluída. As demais frentes parciais que não têm alteração funcional v748 mantêm o estado precedente.
- **Gates previstos:** `tests/test_qa_stagger_trim_v327748.py` (RGBA clima em todos biomas, multi-instância, 180 flips, fallback), benchmark CPU/RSS `.github/scripts/qa_benchmark_performance_v327748.py`, regressões anteriores e relatório JSON no workflow `qa-offline-v327748.yml`. Somente resultado executado e verificado deve virar aprovação.
- **Invariantes:** main/DEV, física, HUD, sprites, clima visual, saves, pets, atlas, shaders, rolagem, PBO, GLES e AAB não foram alterados. Nenhum APK foi compilado nem teste Android realizado.

**Placar histórico v748:** 12 concluídas, 15 parciais, 5 pendentes. Melhorias reais em três frentes parciais não equivalem à conclusão delas.

## Avanços da v3.277.49-QA (somente branch isolada)

**Atualizações efetivamente conectadas ao jogo QA:**
- #2: `pixelrush_qa_city_tiles_v327749.py` intercepta o método `_layer_tiles` de **CityPilotScene v3125**, que é a classe real de Cidade utilizada pelo `LivingWorld`. Planos idênticos para image/normal/geometry/material/fxmask/flow de mesma posição podem reutilizar tuples de tiles. A cada novo `travel`, descarta o plano anterior; usa WeakValueDictionary por Layer sem duplicar pixels. Fallback por `PIXELRUSH_QA_CIDADE_TILE_PLAN=0`. Benefício restrito à renderização multicanal; não elimina a composição de cada quinto quadro no caminho comum somente image.
- #18/#20: `pixelrush_qa_city_weather_v327749.py` intercepta **CityLifeDirector.draw_atmosphere** e **draw_wet_reflections** da Cidade real, pré-calcula deslocamentos iguais por quadro e conserva SDL, `int`, cores, número de primitivas e ordem. Fallback `PIXELRUSH_QA_CITY_WEATHER_FAST=0`.
- #10/#17: batching dos dois tiles sobrepostos no módulo de neve/deserto `pixelrush_qa_modular_batch_v327744.py` habilitado por padrão **apenas na cópia QA**, mantendo `PIXELRUSH_QA_MODULAR_BATCH=0` para rollback imediato. Testes RGBA históricos cobriram subconjunto de condições; medição comparativa de CPU/Jitter Android pendente.
- #7/#24/#25: os planos de tiles não armazenam imagens nem criam novos buffers persistentes; continuam os LRUs e a limpeza RSS v748 com proteção multi-instância. Redução de duplicação de memória de texturas **não comprovada**; não marcar #24 concluída por confundir tuplas com surfaces.
- #26: GC Python original, somente limpeza de cache fria parcelada da v748. Coletor não foi modificado nem declarado resolvido.

**Cobertura preparada, não executada por solicitação do usuário:** `tests/test_qa_cidade_real_v327749.py`, `.github/scripts/qa_benchmark_cidade_v327749.py`, `.github/scripts/qa_preflight_v327749.py` e workflow **manual-only** `.github/workflows/qa-offline-v327749.yml`. Nenhum APK/Android/ADB, nenhum ganho de FPS do Android alegado. Testes e benchmark aguardam execução posterior, sem impedir trabalho de implementação.

**O que realmente impede 32/32 hoje:** integração segura do presenter GLES na janela SDL existente (#1/#3/#4/#29), paridade e tempo comprovados da rolagem incremental no caminho de Cidade real (#5), testes integrais não realizados de clouds/pets/GC/RSS e clock de driver Android (#12/#22/#25/#26/#28/#32). Implementar APIs laboratoriais não autoriza marcá-las como concluídas.

**Placar histórico da v749: 12 concluídas offline, 18 parciais, 2 pendentes**. A nova branch melhora código real de diversas parciais, mas não conclui as 32 nem declara ganho de FPS antes de medir.

### v749 — ponte GPU experimental integrada ao caminho real (SEM homologação)

A ponte `pixelrush_qa_gles_bridge_v327749.py` passa a ser instalada pela entrada de render QA, **mas não age por padrão**. Com ativação experimental explícita `PIXELRUSH_QA_GLES_BRIDGE=1` e, para zoom, `PIXELRUSH_QA_GPU_ZOOM=1`, retorna uma Surface CPU de staging ao jogo, cria presenter GLES, preserva entrada SDL, UI/HUD já composto e apresenta no `pygame.display.flip`. Para zoom, atualiza apenas os mesmos valores originais de `CameraCinematica` e tenta o shader fixo do laboratório GLES (sem mexer em física). Erro de driver ou upload recria uma janela SDL e conserva a Surface de CPU.

Esses fluxos **não possuem aprovação Android**, podem ser mais lentos por upload RGBA por quadro e não são usados na execução normal. Por padrão, GLES2 não oferece PBO GLES3; o opt-in `PIXELRUSH_QA_GLES3_CONTEXT=1` solicita um contexto ES3 real. Em conjunto com `PIXELRUSH_QA_GLES_PBO=1`, o presenter passa a poder usar a rotina PBO já existente. A conexão de runtime avança #29 para PARCIAL, sem aprovação de uploads/ganho no Android. #4 (unificação de todos passes) e #5 (scroll incremental seguro em todas as cenas) permanecem pendentes.

Status #1, #3 e #29 alterados de PENDENTE para PARCIAL pela presença de uma integração de runtime desligada por segurança; nenhuma nova frente declarada **concluída**. Não realizar testes na plataforma Android nem APK até a solicitação de homologação final.

## Implementações da v3.277.50-QA — foco #4 e #5

1. **#4, agora parcial com implementação real:** a cópia Android QA do loop `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py` passa a chamar `pixelrush_qa_unified_post_v327750.finalizar_quadro` quando `PIXELRUSH_QA_ANDROID=1` e `PIXELRUSH_QA_POST_PIPELINE=1`. Este único estágio **orquestra** a mesma sequência original (opcional CameraCinematica.aplicar -> apresentação -> scale se necessário -> blit -> flip), preservando as seções de telemetria e o quadro já composto com HUD/effects. O bloco anterior foi mantido inalterado no `else`, para rollback imediato. A única operação removível é um self-blit RGB realmente redundante.
2. **#5, agora parcial mas conectado a funções de produção da branch QA:** `pixelrush_qa_incremental_scene_v327750.py` intercepta `CityPilotScene._render_chunk` e `LivingWorld._blit_strip` no install de render. Para chunks estáticos sem sprites (não para objetos/obstáculos/cabos) reaproveita uma Surface 450x500, aplicando `Surface.scroll` e reconstruindo a faixa exposta com cópia de RGBA através de `BLEND_RGBA_MAX`, seguida do blend normal na posição de render original. Até 2 buffers por cena. O caminho de strips clássicos usa FaixaPersistenteQA. **Flags desligadas até prova integral:** `PIXELRUSH_QA_CITY_INCREMENTAL=0` e `PIXELRUSH_QA_CLASSIC_INCREMENTAL=0`. Não muda rolagem/velocidade física nem o período 5:1 de fundo.
3. **#7/#10/#24:** `pixelrush_city2_v3124.py` e `pixelrush_biomes2_v3128.py` deixam de alocar `_geometry_view=target.copy()` em todos os quadros; reutilizam o mesmo buffer com `pygame.transform.scale` **1:1**, que copia canais sem aplicar novamente transparência. A identidade do buffer passa a ser estável (eventuais referências externas à Surface poderão ver seu conteúdo atualizado); contratos de draw permanecem.
4. **#25/#26:** o `EscalonadorTrimQA` também considera `CityPilotScene._night_veils` quando o RSS ultrapassa o orçamento, preserva o nível de noite atual e seus vizinhos, e nunca reduz abaixo de quatro. Executado fora do quinto quadro, sem `gc.collect` na corrida e sem alterar a política global do GC.
5. **#1/#3/#29:** a ponte experimental GLES da v749 deixa de usar `convert()` sem WindowSurface após criar o contexto OpenGL; utiliza uma staging Surface RGB 32-bit diretamente. Preservadas flags OFF e fallback SDL. Não demonstrado Android.
6. **#8/#12/#16/#18/#20/#22/#23/#28/#32 e demais parciais:** os caminhos anteriores foram preservados; esta versão **não comprova avanço específico nelas**, por isso continuam parciais. Não duplicar funções nem marcar conclusão sem evidência.

### Gates PREPARADOS, não executados nesta entrega

- `tests/test_qa_pipeline_scroll_v327750.py`: comparação RGBA de zoom, escala, posição final, scroll de chunks reais, strips clássicos, identidade de geometria e trim RSS.
- `.github/scripts/qa_benchmark_pipeline_scroll_v327750.py`: CPU p50/p95/max, memória RSS, comparação dos quadros reais de Cidade e atualização do buffer.
- `.github/scripts/qa_preflight_v327750.py`: hashes de arquivos protegidos, versões, código conectado, flags de fallback e proibição de APK.
- `.github/workflows/qa-offline-v327750.yml`: **apenas workflow_dispatch**, nenhuma execução por push, Android ou compilação.

**Placar atual, contabilizando integração sem homologação:** 12 frentes concluídas anteriormente em código/QA offline; 20 frentes parciais que ainda exigem mais trabalho ou gates; 0 frentes sem caminho de integração. **NÃO significa 32/32 concluídas ou 32/32 otimizadas.** A implementação de GPU em particular depende de medições no driver real para aprovação.

**Garantia de escopo:** branch QA isolada, sem mudanças em `main.py`, DEV, saves, pets, controles, hitboxes, física, assets, configurações visuais, política do quinto quadro ou workflow AAB. Sem APK/Android nesta tarefa.

## Atualização da v3.277.51 — código mais leve no quinto quadro

**Ação de impacto direto sem trocar visual:** `pixelrush_city2_v3124` aplica a mesma noite via `target.fill(...,special_flags=BLEND_RGBA_MULT)` em vez de Surface RGBA + blit. Isso elimina uma passagem full-frame e o conjunto de até treze véus (cada 450×500×4 bytes). O antigo caminho permanece selecionável por `PIXELRUSH_QA_DIRECT_NIGHT_MULT=0` na inicialização. Ensaios locais sintéticos 12/12 RGB/RGBA idênticos; gate integrado de cenas e CPU está preparado, não executado.

**Menos custo Python por tile:** `pixelrush_city2_v3118` agora deixa o SDL recortar o blit de base e cull antes de buscar textura se totalmente invisível. Não mexe no recorte dos sprites. Flag `PIXELRUSH_QA_CITY_NATIVE_CLIP=0` no boot reverte. Ensaios locais sintéticos 56/56 idênticos.

**Scroll mais abrangente, mas NÃO aprovado:** `pixelrush_qa_incremental_scene_v327750` pode desenhar a base reutilizada e entregar o desenho de sprites à rotina original `only_sprites=True`, para preservar animações. Permanece OFF por padrão: a cópia da Surface 450x500 pode ser mais cara que um blit direto, e sem benchmark integrado não se pode forçar a ativação. Não usar contagem de chamadas isoladas como prova de FPS.

**RAM sem serrilhar desempenho:** `pixelrush_qa_render_v327729` marca o uso de `geometry/normal/material/flow/fxmask` por bioma/frame. `EscalonadorTrimQA` deixa vivos os mapas em uso recente, evitando que a pressão RSS gere recriações caras. Formatos de `_geometry_view` agora verificam masks e SRCALPHA antes de reutilizar.

### Plano restante para as 20 parciais

As frentes de GPU/driver (#1/#3/#8/#12/#28/#29/#32) continuam dependentes de identidade pixel-exata e ganho do hardware real; não foi pedido teste Android. A eliminação de todo frame completo (#2/#4/#5/#10) ainda depende de validar animação, transparência e latência sem trocar a aparência. Outros biomas/efeitos (#7/#16/#18/#20/#24/#25/#26) ainda têm alocações e renderizações pontuais não cobertas. Skins/pets (#22) e pré-aquecimento de bioma futuro (#23) não podem alterar RNG, gameplay ou acesso aos saves.

**Resultado atual conservador (implementação != homologação): 12 concluídas em código/QA offline anterior; 20 parciais; 0 sem integração inicial. Nenhuma conclusão adicional reivindicada.** Os gates `tests/test_qa_hotpath_v327751.py`, `.github/scripts/qa_benchmark_hotpath_v327751.py` e workflow manual `.github/workflows/qa-offline-v327751.yml` estão PREPARADOS, não executados nesta entrega.

Escopo preservado: main, DEV, pets, saves, input, física, HUD, sprites, atlas, visual, tempo do jogo, render cache 1:5, APK/AAB e Android.

## Desenvolvimento v3.277.52-QA — duas entregas solicitadas

**Opção 2 (auditoria somente leitura da v3.277.51):** disponível em `QA_AUDITORIA_20_BASE_v327751.md`, com cada uma das 20 frentes classificada por impacto, dificuldade, risco visual/funcional, evidência real e sequência ótima para conclusão. Nenhum arquivo da v751 foi alterado durante a auditoria.

**Opção 1 (implementação em nova branch v752):**
- #10/#18/#20: `pixelrush_biomes2_v3128.py` deixou de limpar e dar blit na Surface de clima quando as famílias de partículas de Neve/Deserto não se aplicam ao clima atual. Transição de clima seco para neve/areia ainda limpa e desenha a mesma contagem original. Flag `PIXELRUSH_QA_MODULAR_WEATHER_SKIP=0` para retornar ao blit tradicional.
- #7/#24: Neve usa a própria Surface de origem para nível noturno zero em `_prepare()`; Deserto de distritos faz o mesmo em `_tile_map()`. Não há alterações em níveis 1–4 de iluminação nem nas lâmpadas (nível 0 já continha pixels LAMP idênticos). `PIXELRUSH_QA_SHARE_DAYLIGHT=0` preserva a cópia anterior. Economia **lógica** potencial de uma Surface 225×250×4 bytes por tile diurno evitado, não evidência de RSS Android.
- #2/#10/#26: plano da Cidade `pixelrush_qa_city_tiles_v327749.py` agora usa modo `auto`: apenas instala cache de tuples se `PIXELRUSH_GPU` não está OFF ou se forçado com `PIXELRUSH_QA_CIDADE_TILE_PLAN=1`. No SDL CPU single-pass evita sobrecarga do wrapper sem hits. Tratamento de exceções foi isolado ANTES do `yield from`, evitando que uma exceção do consumidor provoque renderização extra.
- #7/#10/#24: `pixelrush_qa_render_v327729.py` pode emprestar o mapa geometry da Surface persistente do próprio `LivingWorld` diretamente à `_geometry_view`, eliminando cópia total de 450×500 da geometria. Somente no caminho **opt-in OFF** (`PIXELRUSH_QA_GEOMETRY_BORROW=0`); demais renderizações usam snapshot/cópia, com retorno seguro caso seja desligado. Depende de testes de ambient_occlusion, troca de biomas e GPU.
- #5: algoritmo incremental por variante e suporte a sprites continuam preservados, mas **não foi ativado**. Evitar scroll com buffer intermediário sem ganho mensurado reduz risco de travamento no quinto frame.
- #1/#3/#4/#8/#12/#22/#23/#25/#28/#29/#32: recursos anteriores preservados, sem alegar novo ganho nesta atualização nem declarar conclusão de frentes por laboratório.

**Testes preparados, não executados na homologação final:** `tests/test_qa_render_memory_v327752.py`, `.github/scripts/qa_benchmark_render_memory_v327752.py`, `.github/scripts/qa_preflight_v327752.py`, workflow manual `.github/workflows/qa-offline-v327752.yml`.

**Placar inalterado por rigor: 12 concluídas anteriormente offline, 20 parciais, 0 sem integração inicial.** Nenhum APK/Android nesta versão. `main.py`, produção, DEV, física, HUD, gameplay, saves, pets, skins, assets, política 5:1 e AAB não foram alterados.

## Desenvolvimento v3.277.53-QA — duas frentes simultâneas

**1) Redução concreta de CPU e alocações no quinto quadro**
- `pixelrush_qa_hotpath_v327753.py` instala no renderer real `CityPilotScene v3125` uma verificação de foreground 100% transparente **uma única vez durante a criação da cena**. Quando os tiles FG de imagem são SRCALPHA completamente transparentes e possuem zero sprites, `render_scene(...,foreground_only=True,map_kind='image')` retorna sem blits e atualiza `_last_state` exatamente como a implementação original. Qualquer variante opaca/mista continua com render original, e `PIXELRUSH_QA_CITY_EMPTY_FG=0` desliga a otimização.
- O mesmo módulo intercepta `LivingWorld._blit_strip`: quando uma única textura cobre a largura da viewport, chama diretamente `target.blit` sem montar lista e chamar `target.blits`. Strips que exigem duas ou mais cópias preservam a rotina antiga. `PIXELRUSH_QA_STRIP_ONE_BLIT=0` para rollback. Ensaios sintéticos direcionados Pygame-ce 2.5.8 compararam 30 operações de blit e seis condições de foreground transparente sem diferenças de pixels, mas **a suíte completa não foi executada**.
- `pixelrush_qa_performance_integrated_v327742.py` agenda as leituras de RSS, renderer e smoothscale no **quadro 181** (e 361...) em vez do 180, quando o trim incremental está ativo. Isso retira a sonda do quinto quadro de redraw e mantém a cadência original de 180 apresentações. `PIXELRUSH_QA_TRIM_PROBE_PHASE=0` restaura a fase 180 para gates antigos; se o trim parcelado estiver ausente, o caminho original no quadro 180 é mantido. Nenhum frame de jogo é omitido e nenhuma política de GC é alterada.

**2) Scroll 2.5D real — integração experimental aprofundada**
- `pixelrush_qa_incremental_scene_v327750.py` ganha `PIXELRUSH_QA_CITY_SCROLL_SCOPE=static|all`. `static` usa buffers incrementais apenas para chunks sem sprites e deixa o near animado na rotina original, para não destruir o cache de duas Surfaces far/mid. `all` conserva a implementação experimental v751 com sprites. Os dois modos exigem `PIXELRUSH_QA_CITY_INCREMENTAL=1` (OFF por padrão na corrida).
- O cache recusa imagens sem SRCALPHA 32-bit/900x500, usa máscaras de canal idênticas à origem, preserva `BLEND_RGBA_MAX` na reconstrução da faixa e descarta entradas inválidas com fallback ao blit original. Não executa `os.environ.get` por chunk.
- `EscalonadorTrimQA` pode liberar o cache incremental quando o bioma da instância não é Cidade e o RSS excede o teto, em passos parcelados fora do quinto quadro. Até 2 buffers de 450×500×4 bytes lógicos/instância na rota de Cidade. Mundos ativos nunca perdem seu cache.
- **Nunca ativar scroll por simples presença do código**: um blit adicional full-size pode superar o ganho da faixa incremental. Exigir medição p95 de CPU e verificação de RGBA em mundo/bioma real antes de conclusão.

**Gates preparados, execução final adiada:** `tests/test_qa_hotpath_scroll_v327753.py`, `.github/scripts/qa_benchmark_hotpath_scroll_v327753.py`, `.github/scripts/qa_preflight_v327753.py` e workflow exclusivamente manual `.github/workflows/qa-offline-v327753.yml` (preserva testes antigos v748/v751 com fase/scope de compatibilidade). Sem APK/Android/AAB/Perfetto.

**Placar conservador: 12/32 concluídas anteriormente em código/QA offline, 20/32 parciais. Nenhum gate novo aprovado sem sua execução, nenhum FPS Android alegado.** `main.py`, DEV, saves, pets, HUD, física, controle, sprites, clima ativo, qualidade, assets, comportamento do 5:1 e workflows de produção foram preservados.

## Desenvolvimento v3.277.54-QA — passes CPU evitáveis e scroll com saltos

**A) Blits estáticos da Cidade com transparência pixel-exata (caminho real):**
- `pixelrush_city2_v3118.py` computa uma única vez durante `CityPilotScene.__init__` o limite de alpha de cada textura SRCALPHA imutável das variantes far/mid/near/fg para `image/geometry/fxmask/normal/material/flow`. Não consulta `surfarray`, não instancia texturas 900x500 para mapas vazios e não consulta alfa por pixel no quinto quadro.
- Texturas com alpha totalmente zero não chamam `_scaled_surface` nem `target.blit`; sprites e a ordem do desenho continuam na rotina original. Para texturas 450x250 com regiões transparentes, o bbox é escalado por nearest-neighbor `SCALE=2` para fazer **um único blit recortado**, preservando a área e os pixels reais. Não aplica downsample, não remove prédio ou objeto e não muda a aparência. Cor/alpha de texturas com colorkey ou alpha global atípico seguem caminho antigo.
- O descarte antecipado à direita dos sprites usa apenas posição e deslocamento máximo de vento. A borda esquerda usa largura real da mesma textura que antes. Flags para fallback de boot: `PIXELRUSH_QA_CITY_EMPTY_BASE=0`, `PIXELRUSH_QA_CITY_ALPHA_BOUNDS=0`, `PIXELRUSH_QA_CITY_SPRITE_RIGHT_CULL=0`.
- **#10 / planos técnicos:** `pixelrush_city2_v3124.py` mantém a tupla de tiles near apenas onde `draw_windows_lights` precisa reutilizá-los (`image/fxmask`). Os outros canais usam o iterador original, sem gerar a tupla. `PIXELRUSH_QA_NEAR_PLAN_ON_DEMAND=0` restaura a política anterior.

**B) Scroll incremental da Cidade, ainda OFF:** 
- `pixelrush_qa_incremental_scene_v327750.py` evita limpar uma segunda vez a Surface nova 450x500 SRCALPHA (SDL2 inicializa zero RGBA), mantém `BLEND_RGBA_MAX` para preservar os canais invisíveis no buffer.
- Quando a posição de uma variante muda mais de 48 pixels desde a última chamada, agora invalida seu buffer e chama o blit original diretamente, ao invés de limpar+reconstruir+blitar 450x500. Em frames seguintes de deslocamento suave, reconstrução incremental de faixa funciona como antes. Flags `PIXELRUSH_QA_SCROLL_INIT_CLEAR=0` e `PIXELRUSH_QA_SCROLL_JUMP_DIRECT=0` permitem reproduzir o método v753. O cache de dois buffers/mundo e a expiração RSS fora do 5º quadro permanecem.
- Não ativar `PIXELRUSH_QA_CITY_INCREMENTAL=1` automaticamente. Um scroll full-window + blit extra ainda pode perder para um blit direto na corrida. Gates com pixels e p95 do caminho real preparados, não executados.

**Ensaios pontuais de operações SDL:** Em pygame-ce 2.5.8, 72 comparações RGB/RGBA de retângulos de conteúdo após scale 2x preservaram bytes RGBA; surfaces totalmente transparentes preservaram o destino RGB/RGBA; 10 buffers SRCALPHA novos começaram transparentes; uma amostra da composição de scroll base e buffer foi idêntica em posições de recorte. São verificações sintéticas, **NÃO** teste completo da Cidade, nem FPS Android.

**Gates novos preparados:** `tests/test_qa_alpha_bounds_scroll_v327754.py` (4 testes reais, seis canais, RGB/RGBA, variantes e posições, plano near e saltos); `.github/scripts/qa_benchmark_alpha_scroll_v327754.py` (CPU p50/p95 e RSS em 96 quadros City + 90 saltos); `.github/scripts/qa_preflight_v327754.py` (integridade, versões e flags); `.github/workflows/qa-offline-v327754.yml` (gatilho manual apenas, sem Android). Não foram executados como homologação final.

**Placar conservador:** **12/32 concluídas anteriormente no código/QA offline, 20/32 parciais, nenhuma nova conclusão atribuída**. Evidência de ganho FPS Android: nenhuma. Mantidos `main.py`, branch main, DEV, saves, pets, HUD, física, regras, qualidade visual, todos os sprites, assets, áudio, efeitos, política cache fundo 5:1 e workflows de produção; sem APK/AAB/Android.
