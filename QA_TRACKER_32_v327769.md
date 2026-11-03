# PIXEL RUSH — Fechamento consolidado das 32 frentes (v3.277.69-QA)

**Branch única:** `qa/fechamento-32-v3.277.57`  
**Base exata:** `qa/android-full-performance-v3.277.56`  
**Objetivo do usuário:** todas as melhorias implementadas antes de realizar testes finais em Android; não criar versões intermediárias e não alterar física, arte, saves, DEV nem fluxo de APK/AAB.

## Resultados discriminados

- **32 de 32 frentes auditadas no código**, incluindo os módulos QA, integração no `main.py` e engine Android.
- **22 de 32 concluídas em nível de implementação/testes offline direcionados** (12 anteriores + #26 GC cooperativo + #16 culling modular validado no código real); esta categoria **não significa homologação Android**. O gate de #26 passou em teste local sintético de 901 flips pygame-ce, não em corrida Android.
- **10 de 32 possuem integração ou componentes, mas ainda não cumprem TODOS os critérios de conclusão.** Avanços reais nesta operação nas #2, #7, #10, #16, #22, #23, #24, #25 e #26. Algumas ficam parciais por escopo dos algoritmos, outras exigem hardware.
- **0 de 32 homologadas como pacote Android completo** nesta tarefa, porque não foi solicitado nem executado APK, Android, Perfetto ou teste final do aparelho.
- **Não converter as 10 frentes parciais em concluídas artificialmente**: GPU/GLES/PBO/NEON/driver precisam do gate no hardware, e scroll incremental não comprovou desempenho superior para atlas SDL-RLE usados no caminho real.

| # | Melhoria | Estado de implementação | Evidência / pendência |
|---:|---|---|---|
|1|Zoom GPU|Integrada, não aprovada|Ponte shader com opt-in e fallback SDL; igualdade de pixels e latência Android não demonstradas.|
|2|Compositor 2.5D persistente|**Concluída em implementação e gate offline v759**|Cache temporal de fundo 5:1, buffers por mundo, memo técnica mesmo frame com weakrefs e geometry emprestado; prova LivingWorld real (Cidade/Neve, dois mundos e switch) no CI #41717619668. Android pendente.|
|3|Híbrido CPU/GPU|Integrada, não aprovada|Staging/GLES via ponte; por segurança, não ativado no Android sem prova de HUD/input/roundtrip.|
|4|Zoom e pós-processamento unificados|**Concluída na implementação e gate CPU offline v765**|Finalizador único chamado no loop real; câmera, escala, LRU, RGBA oculto e self-blit aprovados CI #41724644441. GPU é #1 e permanece dependente de Android.|
|5|Scroll incremental pixel-exato|Integrada, fallback|Rotas não-RLE com clipping; origem RLE usa blit original byte-exato, sem prometer vantagem CPU.|
|6|Recorte de transparências|Concluída offline anteriormente|Culling RGBA com gates focados no histórico.|
|7|Evitar grandes alocações|Integrada, parcial|Atlas uniformes usam fill; escala deduplicada; novos mapas técnicos sem cópia extra ao repetir frame.|
|8|SIMD smoothscale|Integrada, não homologada|Seleção nativa por comparação; somente CPU original na ausência de gate Android.|
|9|Pré-composição de texturas|Concluída offline anteriormente|Atlas pré-calculados e cache de superfícies estáticas.|
|10|Remover cópias/passes|Integrada, parcial|Fill técnico uniforme; memo por frame; sky/clima e night optimizados, ainda há passes necessários.|
|11|Cache de menus|Concluída offline anteriormente|Fundo e prévias sob limite; UI dinâmica preservada.|
|12|Backend por dispositivo|Integrada, hardware pendente|Seleção conservadora SDL/GLES, sem forçar driver indisponível.|
|13|Sprites espelhados|Concluída offline anteriormente|Cache de props refletidos.|
|14|Alpha overlays|Concluída offline anteriormente|Buffers reutilizados e multiplicação noturna diretamente no destino.|
|15|FABRIK/deformação|Concluída offline anteriormente|Buffers QA reutilizados e limitados.|
|16|Culling fora da tela|**Concluída na implementação e gate offline v758**|Rotinas reais Neve/Deserto e wrapper preservam byte RGBA, inclusive RGB oculto; 180 combinações de camada/canal/travel/bioma aprovadas no CI #41714045870. Homologação Android pendente.|
|17|Blits em lote|Concluída offline anteriormente|Lote por strips e mapas modulares com fallback.|
|18|Cache de céu e clima|**Concluída na implementação e gate offline v763**|Céu real 7 biomas × fases/noite × RGB/RGBA (168 cenários), nuvens cacheadas RGB com fallback SRCALPHA, 14 climas clássicos e modular RGBA testados (CI #41721393824). Android pendente.|
|19|Vinheta noturna|Concluída offline anteriormente|BLEND_RGBA_MULT por fill sem superfície adicional.|
|20|Pool de partículas|**Concluída no código e gate offline v766 para partículas ativas do gameplay**|PoolManager original de explosões preservado e limitado só quando inativo; partículas ambientais reutilizadas com RNG/pixels idênticos nos 8 biomas; climas usam sementes; 41/41 testes CI #41726342467. Efeitos de menu menores permanecem procedurais.|
|21|Fontes e labels|Concluída offline anteriormente|Textos e fontes sob cache com limite.|
|22|Pré-carregar skins/pets|**Concluída offline para a produção atual v769**|As 3 skins ativas usam os caches de atlas reais. Para os pets desativados COMING SOON, pré-carrega exclusivamente as Surfaces transparentes 52x46 e 210x170 já usadas pelo próprio Studio; 3 testes da classe real e menu/RNG aprovados no CI #41730115687. NÃO existe atlas de pet jogável para carregar.|
|23|Pré-aquecimento biomas|**Concluída em implementação e gate offline v763**|Atlas SHA seguem na thread PROD original; tiles oficiais Neve/Deserto/Cidade Futurista SHA 3/3 em 13 passos de menu e 720381 bytes, até 64 KiB/frame, sem RNG/SDL. CI #41721393824; Android pendente.|
|24|Deduplicação Surfaces|**Concluída no código e gate offline v768**|Atlas estáticos da Cidade (5 canais técnicos e image quando elegível) compartilhados entre mundos só com formato/digest/bytes idênticos; tabela WeakValueDictionary, cenas independentes e rollback aprovados no CI #41727956431 (48/48). Android pendente.|
|25|Limite global de cache|**Concluída em mecanismo de código e gates offline v767**|Orçamento de cache SDL agregado por identidade, pressão acima do teto aciona trim escalonado mesmo sem RSS alto; SDF frio, atlas e caches inativos; hot protegido. Não é teto absoluto de RAM Android.|
|26|Pausas GC|Concluída na implementação offline v757; refinada v758|Coleta exclusiva de geracao maior quando 30/180/900 coincidem, apenas no quadro 1 mod 5. Gate local de 901 flips aprovado; Android pendente.|
|27|Telemetria assíncrona|Concluída offline anteriormente|Worker JSON/CSV, flush final e snapshots.|
|28|Cython/NEON seletivo|Integrada, não aprovada|Biblioteca ARM64 e seleção nativa condicional; hardware/rounding pendentes.|
|29|Uploads GPU/PBO|Integrada, não aprovada|Presenter GLES3+PBO sob flags, CPU sem uploads PBO; sem driver Android não ligar.|
|30|Apresentação SDL|Concluída offline anteriormente|Swap/cópias instrumentados com cache estático.|
|31|Atlas pré-aquecido|Concluída offline anteriormente|Atlas/tiles PROD com SHA verificável.|
|32|VSync/driver/Perfetto|Integrada, hardware pendente|Probes e trace disponíveis; VSync/Perfetto só podem ser demonstrados em Android.|

## Integrações concretas de fechamento no código real

**#2/#7/#10/#24 — repetição de mapas técnicos:** `pixelrush_qa_render_v327729._city_surface_qa` (instalado via `main.py`) evita recompor o mesmo mapa `geometry/normal/material/flow/fxmask` quando a mesma instância de World, cena, Surface, frame, bioma, travel, noite, clima, fase e qualidade pedirem o mesmo mapa novamente. Guarda somente dados de estado e **weakrefs**, nenhum framebuffer 450x500 novo. O render `image` e todas as passagens de foreground permanecem sem memo. Rollback `PIXELRUSH_QA_TECH_SAME_FRAME=0`. **Risco a medir**: consumidores externos que deliberadamente editem a Surface devolvida no mesmo frame, fora do contrato do World.

**#16/#10 — 2.5D modular:** `pixelrush_biomes2_v3128` (Neve) e `pixelrush_biomes2_v3130` (Deserto) agora evitam consultar, gerar e blitar um segundo tile quando seu deslocamento é `x=225` e a Surface destino tem largura 225. A mesma guarda existe no batching QA; não modifica climas, posições, crops, contagem visível nem alfa. Teste sintético local RGB/RGBA passou. Teste dos métodos reais com fixtures, várias camadas e RGB oculto **executado e aprovado na v758** pelo CI #41714045870 (2 biomas × 3 camadas × 5 canais × 6 deslocamentos = 180 combinações); sem inferir aprovação Android.

**#22 — pré-aquecimento durante menu:** `pixelrush_qa_precarregamento_visual_v327757` é chamado pela engine real somente em menu QA Android; prepara as skins ativas (equipada primeiro) e o ID pet equipado, **1 item a cada 8 quadros de menu**, preservando o estado completo de `random`. Não inicia durante jogo, tutorial, pause ou replay, nem altera desbloqueios, atlas de pets ou saves. **Limite atual:** `PetStudioPlayer.preload()` é um placeholder do jogo, portanto o pré-carregamento do pet não faz render real de pets e a frente continua parcial. 100 quadros `JOGANDO` + 32 de `INICIO` em fixture passaram no ensaio local.

**#23 — atlas/tiles:** o carregador `pixelrush_qa_atlas_io_v327747` pré-lê por blocos e verifica SHA tanto os atlas PROD como as tiles PROD existentes, sem pickle, sem carregar Surface, sem sorteio e com limite total de 125 MiB. Se não há espaço/origem válida, mantém o carregamento original quando o bioma for realmente escolhido. `PIXELRUSH_QA_TILES_IO_PREWARM=0` é rollback.

**#26 — GC:** `pixelrush_qa_gc_cooperativo_v327757` entra depois dos outros wrappers de `pygame.display.flip`. No QA Android passa a fazer coletas de gerações 0/1/2 apenas em quadros 31/61/91... /181... /901..., sem sobrepor o quinto quadro 5:1; mantém refcount Python. `restaurar_para_teste()` restaura o flip original e GC automático. Teste local pygame-ce 2.5.8 passou 901 flips: 30 gen0, 5 gen1, 1 gen2, zero coletas programadas no quinto frame. Rollback `PIXELRUSH_QA_GC_COOPERATIVO=0`.

## Gates e segurança

**Executados localmente:** 3 testes sintéticos pygame-ce 2.5.8 aprovados (menu/RNG, GC 901 flips, culling modular RGB/RGBA). Sintaxe dos dois módulos locais de GC/pré-carga analisada via AST. Isso NÃO é teste da renderização completa do jogo.

**Preparados no GitHub para workflow manual-only** (não executado): `tests/test_qa_fechamento32_v327757.py` para menu/preload GC, SHAs de atlas, múltiplas instâncias e weakrefs; `tests/test_qa_fechamento_modular_v327757.py` para os métodos reais Neve/Deserto e byte RGBA; `.github/scripts/qa_preflight_v327757.py` para AST, SHAs e proteção de arquivos; `.github/workflows/qa-offline-v327757.yml` sem push automático, Gradle, Buildozer, ADB, APK ou AAB.

**Preservação:** `main.py`, branch main, DEV, tutorial, física, hitboxes, cadência de fundo 5:1, pixels e iluminação, sombras/clima, câmera, controles, HUD, lojas/desbloqueios, pets, saves, sons, assets, shaders e workflows de produção não foram alterados nesta branch. A engine QA recebeu apenas ligação do prewarm e versão; Buildozer só versão. **Não ativar GLES, GPU zoom, PBO nem C/NEON sem prova no Android.**

**Pendências de conclusão real:** #1/#3/#8/#12/#28/#29/#32 dependem do aparelho; #4/#5/#7/#10/#20/#22/#24/#25 ainda exigem cobertura/medição completa ou otimização funcional adicional. O trabalho feito nesta operação não pode ser renomeado 32/32 sem evidência. Não existe dependência de teste do usuário para continuar *implementando*; existe dependência de hardware para a homologação de determinados recursos.

## Revisao de integração v3.277.58 (mesma branch QA)

- **#25 (parcial):** `pixelrush_qa_cache_policy_v327758.py` é usado tanto pelo trimmer parcelado quanto pelo fallback de pressão RSS. Um mapa technical ativo sem marcador confiável permanece residente; mapas comprovadamente frios ainda podem ser removidos. O comportamento é por instância de mundo e não retém uma segunda Surface.
- **#26 (concluída offline; refinamento):** as gerações do GC não se sobrepõem num mesmo flip. Gen2 substitui gen1/gen0, gen1 substitui gen0; 901 flips de SDL dummy permitem verificar 25/4/1 coletas, zero no quinto quadro, restauração do GC.
- **Testes efetivamente executados localmente neste avanço:** 3/3 testes sintéticos pygame-ce 2.5.8 (política multi-instância, preservação byte-RGBA de mapa quente, GC com 901 flips). A suíte nova `tests/test_qa_cache_gc_v327758.py` de integração dos módulos completos foi criada, mas não executada neste ambiente; não confundir com os três testes sintéticos.
- **Placar final atualizado pela CI v758: 14/32 concluídas offline e 18/32 parciais**, sem homologação Android. Nenhuma frente foi promovida sem gate integrado. Não foi executada homologação final, nem APK/AAB.

## Correção pixel-exata descoberta na revisão offline da mesma v758

A verificação com pygame-ce 2.5.8 revelou que blitar `SRCALPHA=(0,0,0,0)` sobre um pixel de alpha zero pode **zerar os bytes RGB ocultos**. A otimização anterior #18/#20 pulava o blit meteorológico em tempo seco e não cumpria igualdade RGBA estrita. O método real `pixelrush_biomes2_v3128.ModularBiomeScene.render_scene` foi corrigido: o blit continua acontecendo, mas o `fill` do buffer é omitido apenas em quadros secos consecutivos, quando o buffer já está limpo. Após neve/areia, a limpeza sempre acontece. Não há outra Surface criada. O novo teste `tests/test_qa_weather_byte_rgba_v327758.py` compara a saída completa do método contra o modo fallback em Neve/Deserto, com sprites sintéticos de RGB oculto e sequência de transições.

## Evidência integrada final v3.277.58 — GitHub Actions #41714045870

**Execução real:** [CI pygame-ce v758](https://github.com/MrPoopBR/pixel_rush/actions/runs/41714045870), conclusão `success`, commit `3f94a61fec4fa8cba5706819e8a06b922c68ccd3`.

- `tests/test_qa_cache_gc_v327758.py`: **4/4 aprovados** (trimmer, fallback RSS, GC exclusivo 901 flips, multi-instância/RGBA).
- `tests/test_qa_fechamento32_v327757.py`: **4/4 aprovados** (GC/flip, memo por mundo, SHA atlas+tiles, prewarm skins/pet e RNG).
- `tests/test_qa_fechamento_modular_v327757.py`: **1/1 aprovado** (funções originais `_draw_layer` de Neve/Deserto e 180 cenários byte RGBA); esta evidência fecha **#16 apenas no critério offline**.
- `tests/test_qa_weather_byte_rgba_v327758.py`: **2/2 aprovados** (render_scene modular RGBA completo e transições meteorológicas, incluindo RGB oculto). Corrigido skip do blit transparente, agora sempre preservado; apenas o fill redundante pode ser omitido.
- `qa_preflight_v327758.py`: AST, versões, ligações QA e SHA de arquivos protegidos **aprovados**.

**Total da suíte offline integrada: 11/11 testes aprovados.** Isso não mede FPS/RSS Android nem aprova drivers GPU/GLES/PBO/NEON/VSync. Estado consolidado: **14/32 implementadas e cobertas por gate offline**, **18/32 parciais**, **0/32 homologadas como conjunto no aparelho**. As sete frentes associadas a GPU/driver precisam de Android para homologação; as demais ainda precisam de implementação/cobertura adicional e não serão promovidas sem prova.

**Histórico:** referências anteriores a testes `não executados` são relatos da entrega v757; eles foram **executados no workflow da v758**. Não houve testes manuais do usuário, merge `main`, APK ou AAB.

## Avanço QA v3.277.59 — no caminho real

- #2/#7/#10/#24: buffer geometry 450x500 já pertencente a LivingWorld._city_surfaces emprestado por padrão no QA, sem segunda Surface/cópia. Ambiente de referência: pixelrush_city2_v3124 e pixelrush_biomes2_v3128 continuam com snapshot se o destino não pertence ao World. Rollback PIXELRUSH_QA_GEOMETRY_BORROW=0. Resultado RGBA e ambient_occlusion sujeitos ao novo gate.
- #18/#20: sementes das partículas Neve/Deserto e fatores invariantes da atmosfera da Cidade pré-computados, sem alterar quantidade, posição, cor, ordenação, RNG ou buffer meteorológico. Rollbacks PIXELRUSH_QA_MODULAR_SEEDS=0 e PIXELRUSH_QA_CITY_PARTICLE_SEEDS=0.
- 17 frentes continuam parciais até gates e/ou implementação integral; nenhuma rota GPU/NEON/PBO/VSync ativada sem aparelho. Placar provisório 14/32 offline, 18/32 parciais, 0 Android.

### Bloqueante encontrado e corrigido na primeira CI v759

O renderizador de Cidade v3118 usa caches/metadados _qa_uniform_tech, _qa_scaled_alias, _qa_empty_base_maps, _qa_alpha_bounds e _qa_cloud_use_cache. O construtor mais novo v3122 reimplementa __init__ sem executar o construtor v3118 e por isso estes atributos não existiam na cena final. O primeiro teste real de CityPilotScene da CI #41716396740 reproduziu AttributeError no render de geometria (demais 14 testes passaram). **Correção integrada na mesma versão v759:** módulo novo pixelrush_qa_city_bootstrap_v327759.py, instalado ANTES do hotpath e após a construção da arte da Cidade, inicializa somente metadados/índices seguros, confere RGBA/formatos e não altera lib, posições, sprites, física nem eventos. Também reconstitui uniform fill e alias de texturas que estavam inativos por esse bug. Fallback PIXELRUSH_QA_CITY_BOOTSTRAP_METADATA=0 conserva os dicionários exigidos com otimizações de metadata desligadas. Nova suíte confere image/geometry/normal/flow/material/fxmask com bootstrap ON vs fallback, byte RGBA completo. Resultado deste gate: pendente de reexecução, **não homologado**.

## Evidências da CI v759 e próximo gate

- Execução https://github.com/MrPoopBR/pixel_rush/actions/runs/41717129303: **16/16 testes offline aprovados**, mais preflight AST/SHA. A primeira execução https://github.com/MrPoopBR/pixel_rush/actions/runs/41716396740 detectou falta de _qa_uniform_tech na hierarquia real e foi corrigida pelo bootstrap QA, não ocultada.
- Novo teste de integração do LivingWorld real instalado pelo QA vai verificar 2 instâncias simultâneas (normal e leve), channel geometry com/sem empréstimo, ambient_occlusion, memo no mesmo frame, troca de Cidade→Neve, e microbench de CPU. **Ainda não executado neste commit**: não pressupor aprovação nem desempenho superior Android.

## Fechamento comprovado da frente #2 e custo do geometry (CI v759)

- **GitHub Actions #41717619668** (https://github.com/MrPoopBR/pixel_rush/actions/runs/41717619668), commit e57a80263380c60fe255b18094ce031dbd717410: **18/18 testes offline aprovados**, mais preflight de AST/versão/integridade. Os 2 testes novos executam o instalador QA, dois LivingWorld Cidade (qualidades diferentes), o cache de geometry com e sem empréstimo, valores de ambient_occlusion, memo de mesmo frame e troca Cidade→Neve com limpeza/invalidação. Nenhum teste Android.
- **Critério #2 (concluída offline)**: buffer do mundo persiste, cache de fundo temporal 5:1 existente, memo por instância/estado do frame testada no caminho real, transição de bioma e oclusão preservadas. Scroll incremental entre diferentes frames é **#5, que permanece parcial**; #2 não implica GPU homologada.
- **Benchmark do host Linux (somente referência):** mediana de 15 renderizações de geometry: snapshot **0,577948 ms**, empréstimo **0,613193 ms**. Não foi demonstrado ganho de CPU nesse host; a melhoria comprovável é a eliminação de uma Surface/cópia RGBA de 900.000 bytes por cena quando usa o buffer próprio. Não afirmar redução de latência Android. Manter fallback PIXELRUSH_QA_GEOMETRY_BORROW=0 para perfilagem no hardware.
- **Status vigente:** **15/32 implementadas e validadas offline**, **17/32 ainda parciais**, **0/32 homologadas em Android**. #7/#10/#18/#20/#24 continuam parciais embora tenham melhorias novas; nenhum recurso dependente de hardware foi promovido artificialmente. A evidência v758 de 14/32 é histórica e permanece acima para rastreabilidade.

## Micro-otimização climática refinada na v759

Microbenchmark local Python 3.13.5 + pygame-ce 2.5.8 revelou que buscar cada par de sementes usando índice e condicional por partícula poderia tornar a areia ~10% mais lenta (13,638 µs original vs 15,031 µs na primeira tentativa). Por isso a implementação foi ajustada para iterar diretamente as tuplas pré-computadas, com variantes pequenas previamente separadas e mantendo exatamente o loop antigo como fallback. Novo microbenchmark isolado de areia (12 desenhos pygame.draw.line, sem limpeza por frame) mediu mediana **6,796 µs original vs 6,498 µs iterador**, diferença local aproximada de 4,4%; **não é benchmark de frame completo nem ganho FPS Android**. O gate de equivalência byte RGBA da suíte v759 será reexecutado.

## Avanço v3.277.60 — corrigir o cache de nuvens sem degradar o visual

Um teste sintético pygame-ce 2.5.8 demonstrou que blitar sprite de nuvem transparente sobre alvo SRCALPHA com RGB oculto não equivale a chamar pygame.draw.rect para as 16 primitivas, mesmo quando alpha final é 0: a cor RGB escondida podia ser zerada. A otimização anterior cacheava o blit de nuvens scale 1 sem distinguir o destino. **Correção integrada no caminho QA da função visual.nuvem_pixel:** cache LRU somente em superfícies RGB e cores com alpha 255; destino SRCALPHA, cores translúcidas ou escala diferente mantêm a função original. Fallback PIXELRUSH_QA_SAFE_CLOUD_CACHE=0. Nada altera cores, posições, número de nuvens, ciclos, nuvem atlas ou física.

Novo gate de 3 testes verifica nuvens de múltiplos tamanhos/posições com saída RGB/RGBA byte-exata (incluindo RGB oculto), chuva/neve/areia/vento das 14 condições de clima clássico via World._weather vs QA._weather_cached, e microbenchmark de custo CPU do cache em destino RGB. **Até comprovação pelo CI não promover #18.** Placar provisório 15/32 concluídas offline, 17/32 parciais, 0 homologadas Android.

## Integração adicional v3.277.61 (mesma branch isolada)

- **#7/#10/#25:** `pixelrush_qa_geometry_retire_v327761.py` intercepta apenas o *retorno de uma troca de bioma já concluída* pelo `LivingWorld.switch`. Se a Cena antiga ainda mantiver `_geometry_view` apontando exatamente para a Surface RGBA `('geometry',False)` que o World liberou, remove apenas as duas referências de empréstimo aposentadas, permitindo ao Python liberar ~900.000 bytes. Se for snapshot independente, não toca. Sem cache de bioma ativo, alteração de frame, RNG, imagem ou oclusão da cena atual. Flag de rollback `PIXELRUSH_QA_GEOMETRY_RETIRE=0`.
- **#18:** criado gate integrador `tests/test_qa_sky_full_v327761.py` que renderiza o método original completo `desenhar_ceu` em 7 biomas, 4 fases, 3 níveis noturnos e alvos RGB/SRCALPHA (168 cenários), comparando bytes RGBA contra a versão com cache, incluindo nuvens e estrelas. Complementa clima modular/14 modos clássicos e testes de pixels ocultos da v760. A frente continua parcial **até o gate passar**.
- **Gates novos:** `tests/test_qa_geometry_retire_v327761.py` usa World real Cidade→Neve→Cidade, weakref das Surfaces, snapshots externos e troca idêntica. Os 21 testes offline anteriores continuam no workflow. **Placar provisório 15/32 concluídas offline, 17 parciais e 0 homologadas Android** até evidência de CI. Nenhum APK/AAB.

## Avanço v3.277.62 — #23 tiles prewarm em menu

O preflight QA anterior lia e validava tiles PROD inteiros durante o boot, mesmo com atlas já tratados pela thread PROD. Agora o módulo pixelrush_qa_tiles_menu_v327761.py executa no máximo 64 KiB de leitura SHA-256 por frame de menu, um arquivo por passo, com limites 40 MiB por arquivo / 125 MiB total, stat tamanho+mtime antes e depois de cada bloco. Nenhum descritor aberto entre frames, Surface, pickle, sorteio ou seleção de bioma. PrecargaVisuaisQA usa o mesmo passo(estado) existente, com fila de skins/pets a cada 8 quadros intacta. Em corrida não há leitura; se menu curto, loaders PROD continuam originais. Flags PIXELRUSH_QA_TILES_IO_MENU=0 (rollback boot) e PIXELRUSH_QA_TILES_IO_PREWARM=0 (desabilitar). Novo gate com 4 testes de orçamento, mutação, SHA, RNG e estado de jogo. O trabalho v761 anterior de geometry retirement e céu integral foi preservado. Não promover #23 sem gate. Placar pré-teste: 15/32 offline, 17/32 parciais, 0 Android.

## QA v3.277.63 — verificação dos tiles reais, fechamento sujeito ao CI

A suíte anterior #23 tinha fixtures sintéticas aprovadas (CI #41720901804, 29 testes integrados). Foi adicionada uma prova independente dos binários oficiais neve.tiles, deserto.tiles e cidade_futurista.tiles, comparando os SHA reais de produção e exigindo conclusão em até 32 passos de menu de 64 KiB sem RNG/SDL nem arquivo aberto na corrida. Dados fonte do GitHub: 416901, 196268 e 107212 bytes; total 720381 bytes. Essa prova deve ser aprovada antes de promover #23 a concluída offline. A frente #18 já tem céu integral nos sete biomas, cache de nuvens, 14 climas clássicos e comparação RGBA de clima modular: pode ser encerrada offline após confirmação dos gates integrais. No ponto desta gravação mantêm-se 15/32 comprovadas e 17/32 parciais, zero homologação de hardware.

## Fechamento comprovado offline da #18 e #23 — CI v3.277.63

**Execução [GitHub Actions #41721393824](https://github.com/MrPoopBR/pixel_rush/actions/runs/41721393824): status success, 29/29 testes pygame-ce offline aprovados e preflight AST/SHA.** A prova do menu nos arquivos PROD reais confirmou neve.tiles 416901 B, deserto.tiles 196268 B, cidade_futurista.tiles 107212 B (total 720381 bytes), 3/3 SHA verificados em 13 passos de até 64 KiB por quadro; RNG preservado, sem Surface e com rollback. O céu integral dos sete biomas passou no teste do método real em 168 combinações, complementado pela prova de nuvens RGB/RGBA ocultos, 14 climas clássicos e transições modulares. O cache usa fallback SDL original nos casos não pixel-exatos. **#18 e #23 passam a concluídas apenas no critério implementação + QA offline; não significam aprovação de FPS ou hardware Android.**

**Placar vigente: 17/32 concluídas offline; 15/32 ainda parciais; 0/32 homologadas no Android.** As sete frentes dependentes do dispositivo (#1/#3/#8/#12/#28/#29/#32) não foram forçadas a ON e permanecem pendentes. Outras oito frentes ainda precisam de implementação/medição mais extensa (#4/#5/#7/#10/#20/#22/#24/#25). Não fazer APK/AAB nem homologação final nesta operação. Referências anteriores neste documento ao placar 15/32 registram estados históricos dos commits passados.

## Otimização adicional de RAM QA v3.277.64

A regra compartilhada modular_cache_fria identifica caches recompostos sob demanda nos módulos modulares. Sob pressão RSS, trimmer parcelado (fora do quadro 5) e fallback liberam _maps/_composites somente de Neve/Deserto inativos; _night_tiles somente de Deserto. Neve pré-gera _night_tiles e não pode perdê-las. Biomas são rechecados a cada entrada, inclusive quando ocorre troca enquanto o trim está agendado. Nenhuma fonte/pose, arte, pets, save ou física modificados. Novo gate tests/test_qa_modular_cold_cache_v327762.py compara RGBA real do Deserto antes/depois. Esta frente permanece parcial até medição agregada Android. O placar de conclusão anterior é preservado; esta mudança isolada não promove a #25.

## Resultado integrado real QA v3.277.64

GitHub Actions #41721816822 terminou SUCCESS no commit 6b4c8ed90d0c61d509a0d7994d3259338405c0d0. Foram **33/33 testes offline aprovados com pygame-ce 2.5.8** (4 cache/GC, 4 compositor e SHA, 1 culling, 2 clima modular, 5 geometry/clima Cidade, 2 LivingWorld real, 3 nuvens/clima clássico, 3 geometry retirement, 1 céu integral 168 estados, 5 tiles menu SHA, 4 caches modulares sob RSS). Além disso, passou o preflight AST/versões/hash de arquivos protegidos. Testes novos confirmam RGBA de render_scene Deserto após desalocação e recomposição dos caches, garantem que Neve mantém precomputação, que bioma ativo não é desalocado por fila atrasada e fallback limpa só mapas frios. **Não foi executado APK/AAB/Android ou homologação final.** Status inalterado: **17/32 concluídas em implementação e QA offline, 15/32 parciais, 0/32 homologadas no aparelho**. #25 segue parcial por orçamento agregado Android.

## Integração concentrada QA v3.277.65

Frente #25: implementado inventário agregado de caches World, Cidade e Neve/Deserto pelo `id(Surface)` usando pitch*altura, sem copiar imagens nem contar alias repetidos. A sondagem ocorre apenas na mesma fase fora do quadro 5 (181 mod 180); limite conservador de 8192 entradas e skip do acionamento se truncado. Se cache SDL medido excede o orçamento de 48 a 192 MiB derivado do teto RSS, o trimmer parcelado é ativado mesmo com RSS geral abaixo do teto. Permanece impossível desalocar caches ativos, prebake de Neve ou outras referências de imagem necessárias; **não se trata de teto absoluto de RAM do jogo**. Rollback `PIXELRUSH_QA_SURFACE_BUDGET=0`.

Frente #4: novo gate de apresentação real compara saída byte-RGBA do finalizador QA contra o código legado, câmera habilitada/desabilitada, escalas, alfa oculto e self-blit; sem trocar física ou transformações de imagem. O código já usa esse finalizador no loop, com rollback existente. GPU, NEON, GLES, VSync exigem homologação Android separada. **Placar antes do gate: 17/32 offline; 15 parciais; zero homologadas Android**.

## Implementação real v766 e evidência v765

A frente #4 passou 2 gates adicionais de equivalência do finalizador único de câmera/escala/apresentação na CI [#41724644441](https://github.com/MrPoopBR/pixel_rush/actions/runs/41724644441), com 38/38 testes aprovados. Fechada exclusivamente no critério CPU/QA offline; a aceleração GPU segue #1.

A frente #20 recebe reaproveitamento real de dicionários das partículas ambientais (8 a 14 elementos) entre as oito cidades/biomas, com sequência e estado de RNG local iguais. O PoolManager original já possui 250 Particula: o hook QA não cria outro pool e só libera o excedente após as partículas morrerem e o número de disponíveis passar de 256; nunca reduz explosões ainda ativas, nem ordem, propriedades, imagem, velocidade ou cor. Flags `PIXELRUSH_QA_PARTICULAS_POOL=0` e `PIXELRUSH_QA_PARTICULA_RELEASE=0` restauram o comportamento antigo. Novo teste compara métodos reais do engine extraídos via AST, sorteio global, atributos, oito biomas, RGBA RGB e alpha, 300 sprites em grupo, e limites do pool. Até novo CI, #20 permanece parcial. Placar de fechamento comprovado até o momento: **18/32 offline, 14/32 parciais, 0/32 Android homologadas**.

## Avanço QA v3.277.67 — memória SDF e gate de pool

**CI [#41726342467](https://github.com/MrPoopBR/pixel_rush/actions/runs/41726342467) passou 41/41 testes pygame-ce offline.** O teste novo v766 confirmou estados/dicionários de partículas ambientais em oito biomas, desenhos RGBA, RNG global intacto, e 300 partículas reais de explosão simultaneamente visíveis com limitação SOMENTE das livres excedentes. O sistema já tinha um PoolManager de explosões; com a versão QA ele é preservado e os dicionários de clima/ambiente são reaproveitados. A frente #20 fica concluída em implementação+gates offline para famílias reais do gameplay; qualquer nova família futura precisará de novos gates. Não se afirma ganho FPS Android. **19/32 concluídas offline, 13/32 parciais, zero homologadas no aparelho**.

Frentes #7/#25: sob pressão de cache, a Surface de dano/SDF 450×500 retida por mundos que já não têm chunks de dano ativos agora pode ser descartada pelo trimmer parcelado ou fallback RSS. O inventário agregado passa a contá-la por identidade; a condição de `damage.chunks` é reavaliada imediatamente antes da remoção, preservando qualquer dano atual. Um novo evento SDF no futuro cria o mesmo buffer pelo código original; o desenho e física não mudam. Novo gate de inventário, trim com e sem chunks e fallback. #7/#25 continuam parciais até o CI e auditoria do restante da RAM. Sem APK/Android.

## Avanço QA v3.277.68 — static atlas intern por mundo e fechamento do orçamento cache

CI [#41727086275](https://github.com/MrPoopBR/pixel_rush/actions/runs/41727086275) **44/44 testes offline pygame-ce aprovados**, inclusive novo descarte de Surface SDF fria de 900 KB sob pressão, preservando frame/dano ativo, e RAM de caches contabilizada sem dupla contagem de alias. A frente #25 está **concluída como implementação de limite agregado SOFT de caches**, não como teto de toda a RSS Android; se o uso estritamente ativo exceder o orçamento não se excluem Surfaces necessárias. O conjunto continua não homologado no dispositivo.

Nova implementação #24: `pixelrush_qa_city_intern_v327768.py` mantém tabela WEAK de atlas da Cidade inteiramente finalizados, somente `geometry/normal/material/flow/fxmask`, com mesma dimensão, pitch, flags, alpha, máscaras, hash BLAKE2b e bytes brutos RGBA idênticos — inclusive RGB oculto. Roda após `CityPilotScene.__init__` e antes do bootstrap dos índices, de forma que o código do renderer encontra as identidades corretas. Nenhuma Surface ou recurso visual adicional é criado; cenas/estados continuam separados e as fontes podem ser liberadas quando não utilizadas. Em qualquer incompatibilidade, guarda a textura independente original; rollback `PIXELRUSH_QA_CITY_GLOBAL_INTERN=0`. Testes novos: duas instâncias reais renderizando 6 canais de forma byte-exata, comparação com modo sem intern, textura sintética com alpha0 e RGB oculto e coleta weak. **Aprovação de #24 depende de sucesso CI, não deve ser presumida.** Placar antes CI: **20/32 offline, 12 parciais, zero homologadas Android**.


## Avanço consolidado v3.277.69-QA — fechamento seguro sem Android

- **#24 concluída offline após evidência comprovada:** CI #41727956431 passou **48/48** casos integrados, incluindo 3 testes específicos de atlas técnicos imutáveis, pixel RGBA (incluindo RGB oculto), compartilhamento entre duas Cidades independentes, rollback e weakrefs. O intern não muda sprites, clima ou cenas.
- **#22 com implementação complementar real:** o callback de menu QA chama o preload legado e antecipa o mesmo cache de superfícies transparentes de `PetStudioPlayer.frames` nos tamanhos `(52,46)` e `(210,170)`, usados na corrida/popup. Isso evita a criação inicial sob demanda; **não ativa pets** e **não há atlas reais de pets para aprovar**. Nova suíte verifica AST da classe real, bytes RGBA transparentes, identidade das Surfaces, ordem das skins, restrição ao menu e RNG intacto. **Ainda depende do CI v769**, portanto não declarada concluída nesta pré-publicação.
- **Novo placar comprovado no momento do commit:** 21/32 concluídas offline, 11/32 com pendências, 0/32 homologadas Android. Se a CI v769 passar, revisar a frente #22 sem presumir teste de arte de pets desabilitados.
- **Sem alterações** em `main.py`, branch `main`, linha DEV, tutorial, física, colisões, câmera, gameplay, skins, modelos/atlas, saves, áudio, workflows APK/AAB nem assets. O arquivo da engine recebeu apenas versão e callback QA no preloader; Buildozer recebeu números de versão. Nenhum Android executado.

### Reforço de deduplicação na mesma versão v3.277.69

O preload final de Cidade v3122 pré-compõe as props imóveis no atlas `image` antes de qualquer uso; a auditoria de `_render_chunk` e `render_scene` encontrou apenas leituras da origem após o construtor. O intern por BLAKE2b + igualdade RAW completa passa a aceitar também esse `image` estático quando seus bits/flags/máscaras/alpha são compatíveis, sem compartilhar sprites móveis nem o estado de cena. Novos testes incluem o RGB oculto do canal `image`, duas cenas reais e igualdade RGBA na renderização; resultado sujeito ao mesmo workflow offline. Flag `PIXELRUSH_QA_CITY_GLOBAL_INTERN=0` conserva rollback.

## Evidência integrada final da mesma v3.277.69 (CI real)

- Execução GitHub Actions [#41730115687](https://github.com/MrPoopBR/pixel_rush/actions/runs/41730115687), commit `e1f0154af749e3e383c74745af6e81e018684f3e`: **sucesso 51/51 testes offline pygame-ce 2.5.8** e preflight AST/versões/SHA protegidos.
- Testes específicos de `image` + cinco atlas técnicos imutáveis da Cidade entre instâncias, equivalência dos 6 canais byte RGBA e RGB oculto, weakrefs e fallback: **3/3** aprovados. #24 concluída no critério offline.
- Testes da classe `PetStudioPlayer` real (extraída do AST da engine), pré-carga de skins/pet no menu, RNG e ordem, bytes de frames transparentes 52x46 e 210x170: **3/3** aprovados. #22 concluída **para os recursos realmente disponíveis na produção atual**; pets reais continuam deliberadamente desativados/COMING SOON, portanto não se alega pré-carga de animações/atlas inexistentes.
- **Placar consolidado da implementação atual:** **22/32 concluídas offline, 10/32 parciais/integradas, 0/32 homologadas Android**. Dependências de dispositivo não se confundem com ausência de código. Sete frentes GPU/native/driver ainda só têm componentes ou laboratório; #5 scroll tem fallback pixel-exato, mas não benefício comprovado no SDL-RLE, e #7/#10 ainda demandam cobertura de todo caminho.
- Não executar APK, Android, AAB nem pedir testes do usuário neste avanço. `main.py`, produção estável, DEV, física, visual, HUD, saves, pets bloqueados, tutorial, assets e workflows APK/AAB não mudaram nesta versão.
