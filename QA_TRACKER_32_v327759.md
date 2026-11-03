# PIXEL RUSH — Fechamento consolidado das 32 frentes (v3.277.59-QA)

**Branch única:** `qa/fechamento-32-v3.277.57`  
**Base exata:** `qa/android-full-performance-v3.277.56`  
**Objetivo do usuário:** todas as melhorias implementadas antes de realizar testes finais em Android; não criar versões intermediárias e não alterar física, arte, saves, DEV nem fluxo de APK/AAB.

## Resultados discriminados

- **32 de 32 frentes auditadas no código**, incluindo os módulos QA, integração no `main.py` e engine Android.
- **14 de 32 concluídas em nível de implementação/testes offline direcionados** (12 anteriores + #26 GC cooperativo + #16 culling modular validado no código real); esta categoria **não significa homologação Android**. O gate de #26 passou em teste local sintético de 901 flips pygame-ce, não em corrida Android.
- **18 de 32 possuem integração ou componentes, mas ainda não cumprem TODOS os critérios de conclusão.** Avanços reais nesta operação nas #2, #7, #10, #16, #22, #23, #24, #25 e #26. Algumas ficam parciais por escopo dos algoritmos, outras exigem hardware.
- **0 de 32 homologadas como pacote Android completo** nesta tarefa, porque não foi solicitado nem executado APK, Android, Perfetto ou teste final do aparelho.
- **Não converter as 19 frentes parciais em concluídas artificialmente**: GPU/GLES/PBO/NEON/driver precisam do gate no hardware, e scroll incremental não comprovou desempenho superior para atlas SDL-RLE usados no caminho real.

| # | Melhoria | Estado de implementação | Evidência / pendência |
|---:|---|---|---|
|1|Zoom GPU|Integrada, não aprovada|Ponte shader com opt-in e fallback SDL; igualdade de pixels e latência Android não demonstradas.|
|2|Compositor 2.5D persistente|Integrada, gate real pendente|Cache fundo 5:1 mantido; memo técnica de mesmo frame por instância com weakrefs, sem copiar pixels.|
|3|Híbrido CPU/GPU|Integrada, não aprovada|Staging/GLES via ponte; por segurança, não ativado no Android sem prova de HUD/input/roundtrip.|
|4|Zoom e pós-processamento unificados|Integrada, parcial|Contrato único da apresentação QA já usado; transformações GPU/CPU não foram eliminadas integralmente.|
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
|18|Cache de céu e clima|Integrada, parcial|Cache de céu/nuvens existentes; secas neve/deserto pulam a passagem meteorológica inerte.|
|19|Vinheta noturna|Concluída offline anteriormente|BLEND_RGBA_MULT por fill sem superfície adicional.|
|20|Pool de partículas|Integrada, parcial|Sementes fixas pré-computadas e Surface clima reutilizada; ainda sem pool unificado de todas as famílias.|
|21|Fontes e labels|Concluída offline anteriormente|Textos e fontes sob cache com limite.|
|22|Pré-carregar skins/pets|Integrada, parcial|Novo precarga menu: skins ativas e ID pet equipado, em fatias e sem RNG; PetStudio atual é placeholder, não declarar atlas de pet carregado.|
|23|Pré-aquecimento biomas|Integrada, parcial|Leitura SHA streaming de atlas PROD + tiles PROD com orçamento compartilhado, sem instanciar bioma antes do sorteio.|
|24|Deduplicação Surfaces|Integrada, parcial|Dedup integral de atlas técnicos + fill uniforme e memo mesma instância/quadro.|
|25|Limite global de cache|Integrada, parcial|LRUs por cena; fallback e trim parcelado agora preservam mapas tecnicos quentes em multiplas instancias. Falta prova de orçamento agregado Android.|
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

**Pendências de conclusão real:** #1/#3/#8/#12/#28/#29/#32 dependem do aparelho; #2/#4/#5/#7/#10/#18/#20/#22/#23/#24/#25 ainda exigem cobertura/medição completa ou otimização funcional adicional. O trabalho feito nesta operação não pode ser renomeado 32/32 sem evidência. Não existe dependência de teste do usuário para continuar *implementando*; existe dependência de hardware para a homologação de determinados recursos.

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
- 18 frentes continuam parciais até gates e/ou implementação integral; nenhuma rota GPU/NEON/PBO/VSync ativada sem aparelho. Placar provisório 14/32 offline, 18/32 parciais, 0 Android.

### Bloqueante encontrado e corrigido na primeira CI v759

O renderizador de Cidade v3118 usa caches/metadados _qa_uniform_tech, _qa_scaled_alias, _qa_empty_base_maps, _qa_alpha_bounds e _qa_cloud_use_cache. O construtor mais novo v3122 reimplementa __init__ sem executar o construtor v3118 e por isso estes atributos não existiam na cena final. O primeiro teste real de CityPilotScene da CI #41716396740 reproduziu AttributeError no render de geometria (demais 14 testes passaram). **Correção integrada na mesma versão v759:** módulo novo pixelrush_qa_city_bootstrap_v327759.py, instalado ANTES do hotpath e após a construção da arte da Cidade, inicializa somente metadados/índices seguros, confere RGBA/formatos e não altera lib, posições, sprites, física nem eventos. Também reconstitui uniform fill e alias de texturas que estavam inativos por esse bug. Fallback PIXELRUSH_QA_CITY_BOOTSTRAP_METADATA=0 conserva os dicionários exigidos com otimizações de metadata desligadas. Nova suíte confere image/geometry/normal/flow/material/fxmask com bootstrap ON vs fallback, byte RGBA completo. Resultado deste gate: pendente de reexecução, **não homologado**.

## Evidências da CI v759 e próximo gate

- Execução https://github.com/MrPoopBR/pixel_rush/actions/runs/41717129303: **16/16 testes offline aprovados**, mais preflight AST/SHA. A primeira execução https://github.com/MrPoopBR/pixel_rush/actions/runs/41716396740 detectou falta de _qa_uniform_tech na hierarquia real e foi corrigida pelo bootstrap QA, não ocultada.
- Novo teste de integração do LivingWorld real instalado pelo QA vai verificar 2 instâncias simultâneas (normal e leve), channel geometry com/sem empréstimo, ambient_occlusion, memo no mesmo frame, troca de Cidade→Neve, e microbench de CPU. **Ainda não executado neste commit**: não pressupor aprovação nem desempenho superior Android.
