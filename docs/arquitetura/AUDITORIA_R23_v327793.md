# Auditoria funcional R23 — inimigos, biomas, estrutura, performance e lacunas

QA792 base: d8f97adf246bc593da3bb049bef2f3a5c31dd698. Código QA793 preserva imports e classes históricas que ainda são alvo de CI. **Nenhum arquivo foi apagado por critério superficial.**

## Inimigos e obstáculos reais por bioma
O inventário abaixo inclui os **28 códigos originais AMEACAS (4×7)** e ameaças especiais, com descrições baseadas no comportamento do código. Nem todos os adversários foram redesenhados na QA793.

| Bioma | Adversário/código | Comportamento |
|---|---|---|
| Cidade | C1 — Rato Urbano | Corre em disparadas, ziguezague patrulheiro e pequenas oscilações na calçada |
| Cidade | C2 — Pombo Atrapalhado | Voo irregular, mergulho, ziguezague e batidas de asas mais frequentes |
| Cidade | C3 — Cones de Construção | Barreira baixa fixa para salto curto ou longo |
| Cidade | C4 — Cavalete de Obras | Barreira larga fixa, exige altura e antecipação |
| Cidade | Hidrante da Cidade | Obstáculo urbano fixo, aparece também na lição de salto longo |
| Neve | N1 — Pinguim Deslizante | Desliza rapidamente pelo gelo com oscilação sutil |
| Neve | N2 — Coruja Invernal | Voa ondulando, exige agachamento ou salto bem calculado |
| Neve | N3 — Bloco de Gelo Rachado | Bloco estático sólido; evitar colisão com salto |
| Neve | N4 — Tronco Nevado | Tronco baixo, girando visualmente sobre a pista |
| Neve | N5 — Boneco de Neve | Inimigo novo, acena e arremessa uma bola em um de três níveis por aparição |
| Neve | N5_BOLA — Bola de Neve | Projétil pequeno em linha reta que pode cruzar alturas diferentes |
| Deserto | D1 — Serpente das Dunas | Balança a cabeça antes do bote |
| Deserto | D2 — Besouro Rolador | Rola pelo chão e se aproxima |
| Deserto | D3 — Coluna de Ruínas | Obstáculo alto e imóvel |
| Deserto | D4 — Ossada Ancestral | Barreira ampla fixa |
| Vulcão | V1 — Salamandra Magmática | Salta periodicamente |
| Vulcão | V2 — Morcego Vulcânico | Voa em ondas |
| Vulcão | V3 — Rocha de Obsidiana | Pedra sólida fixa |
| Vulcão | V4 — Gêiser de Vapor | Rachadura de aviso seguida de coluna perigosa |
| Floresta | F1 — Caracol Blindado | Anda devagar |
| Floresta | F2 — Tucano Travesso | Mergulha durante o voo |
| Floresta | F3 — Tronco Oco | Tronco rolante com textura animada |
| Floresta | F4 — Galho Suspenso | Obstáculo alto, exige agachamento |
| Cidade Futurista | CF1 — Robô Patrulheiro | Patrulha em pequenos deslocamentos |
| Cidade Futurista | CF2 — Drone Sentinela | Drone aéreo ondulante, exclusivo do bioma futurista |
| Cidade Futurista | CF3 — Caixa Tecnológica | Barreira tecnológica fixa |
| Cidade Futurista | CF4 — Cabos Energizados | Barreira elétrica alta |
| Cidade Futurista | Obstáculo Pula-Pula | Autômato que salta repetidamente, agora limitado ao futuro |
| Ilhas Celestes | IC1 — Besouro Luminoso | Salta por fases |
| Ilhas Celestes | IC2 — Arraia Celestial | Voa em ondas |
| Ilhas Celestes | IC3 — Cristal Gigante | Barreira alta e fixa |
| Ilhas Celestes | IC4 — Arco de Pedra | Obstáculo suspenso, exige abaixar |

## Escolhas para desempenho em Android fraco
- Reutilização de sprites do jogo no tutorial, sem um segundo jogo; **um único** cache de quadro congelado, animando indicadores por operações de desenho SDL; nenhum `Surface` por tick.
- Três quadros pré-cacheados para o Boneco de Neve, uma imagem pequena para bolas e no máximo um lançamento por inimigo.
- Sprite animado do pombo usa quadros do atlas pré-existente, sem novo atlas nem mutação por pixel em runtime.
- Asfalto da neve desenhado somente na construção do tile de 960×70 e reutilizado no cache normal, em vez de ser refeito no loop.
- Música procedural sintetizada uma vez no carregamento, não por frame, e passo sonoro com efeito curto.
- Nenhum cache ou shader GPU extra foi criado para o 2.5D nesta etapa.

## Migração adicional integrada e auditável (R23)
Foram migrados **21 módulos históricos** adicionais, com conteúdo byte-idêntico ao commit QA792 e aliases `sys.modules` nos 21 caminhos originais. A raiz não perdeu arquivos físicos porque imports Android, CI e módulos históricos ainda usam esses nomes. O manifesto completo está em `docs/arquitetura/MANIFESTO_R23_MIGRACAO_v327793.json`, com teste de identidade/importação. Inclui áudio, corredores, moedas, cenas, cinema, sombras, geometria, pista, i18n, sequências e física de áudio. NÃO mover `pixelrush_inimigos_v3221.py`, `pixelrush_profiler_v3204.py` ou `pixelrush_avisos_raros_i18n_v3247.py` indiscriminadamente: usam `__file__` para recursos e telemetria.

## Auditoria de modularização
Módulos legados existem por imports indiretos e verificações SHA de preflight. A QA792 já transferiu seis componentes com aliases seguros; nesta QA793, novos componentes (`world/daynight_v327793`, `ui/tutorial/premium_v327793`, `entities/enemies/snowman_v327793`) nasceram canônicos dentro de `src/pixelrush`. Migração massiva remanescente exige manifesto por blob e atualização de imports/safe paths em Android. `pixelrush_inimigos_v3221.py` usa `Path(__file__)` para localizar atlases e NÃO pode ser movido diretamente sem corrigir esse recurso.

## Lacunas e limites
Não houve troca por outro renderizador 2.5D, reimplementação cinematográfica de todas as câmeras nem polimento completo de cada sprite. Mudanças de física/intensidade e estética na corrida são intencionais por solicitação, portanto RGBA antigo de **toda a tela** não deve ser igual à QA792. Os gates usam estabilidade deterministicamente local e preservação de caminhos/arquivos não solicitados. Apenas o Galaxy A54 pode comprovar FPS, bateria, calor e gestos Android reais.

## Evidências de CI R23
- <https://github.com/MrPoopBR/pixel_rush/actions/runs/42052127948> — **SUCCESS** em Python 3.13 + pygame-ce 2.5.8, head `eeb2a98fb0cbc2e97875d05a1cb23437dc8113b9`.
- Motor completo importado com SDL dummy, mantendo `main()` sem execução e sem ler/gravar saves de partida; teste de AST/sintaxe, módulos canônicos e compatibilidade.
- **8 testes dinâmicos** de tutorial/biomas (inclui swipe-down em dois tempos no mesmo dedo, 300 ticks da introdução, limpeza de partículas de morte, progressão das quatro lições extras, ciclo de 10.800 ticks, RGBA reproduzível e três alturas de bolas de neve) e **2 testes** de 21 migrações; regressões QA792/790/789 executadas em worktree histórico.
- Benchmark Cidade 2.5D: 260 buffers RGBA produzidos, intervalo periódico de desenho de cinco quadros preservado. **Não há** ganho de FPS comprovado contra hardware Android; não confundir teste com homologação.

## R23 — duas frentes adicionais de desempenho e polimento (mesma versão)

### Otimizações integradas e verificadas (qualidade completa)
1. **World Cidade 2.5D:** eliminada a limpeza completa redundante do buffer na rotina `_city_surface` quando `CityPilotScene.render_scene` já faz o fill do mesmo mapa no início. Experimento controlado `qa_a54/benchmark_city_preclear_v327793.py`, 130 quadros e 260 buffers RGBA pixel-exatos. No primeiro benchmark Linux, queda do p50 por passe de 2,18% a 14,22%; em repetição, a variância oscilou em imagem/geometria, portanto **não alegar melhoria estável em todos os passes**. Ganhos mais consistentes em normal e flow.
2. **FLOW da Cidade diretamente no destino:** subsurface sobre a região 450x500 da Surface final, sem alocar seu buffer intermediário `('flow', False)` (~900.000 bytes) e sem blit adicional. Fallback para targets com colorkey, alfa suspeito, resolução diferente e todos os demais biomas. GATE rígido 260 hashes RGBA idênticos para RGB/SRCALPHA e ausência do buffer retido; p50 do passe FLOW caiu 22,98% no experimento pré-integração e 23,09% após integração, em Linux CI. **Não equivale a ganho de FPS total no A54**.
3. **Nenhum normal direto:** embora RGBA fosse idêntico, um experimento apresentou +56,83% no tempo do mapa normal; candidato rejeitado, manteve pipeline original.
4. **Gráficos únicos completos:** a criação e troca de bioma do `ParallaxBackground` agora usam `LivingWorld(... lightweight=False)` / `world.lightweight=False` desde o primeiro quadro também no Android. Nenhum fallback automático oculto na inicialização. Atenção: exigência de arte completa pode aumentar o custo inicial no Android e ainda requer homologação real.
5. **Câmera leve e suave:** `GameFeel.seguir_jogador` adiciona seguidor amortecido (até ~4px em Y, ~2,4px de tendência lateral ao pulo longo, ~4px de impacto no swipe-down). Nenhuma Surface, `smoothscale`, mudança de hitbox ou tick da física novos; reduz movimento se acessibilidade pede efeitos mínimos. A câmera clássica continua disponível para outros eventos.
6. **Céu diurno/noturno mais contínuo:** refinados 64 passos de fase e 32 níveis de noite no cache existente (máximo 4 Surfaces) e sincronizadas aurora em fase 0/1, pôr do sol perto de 0,47 e transições de 180 segundos. Teste de variação cromática ao longo de uma volta completa aprovado.
7. **Pombo C2 com animação rápida e estável:** passa por todas as poses existentes no atlas já carregado, avançando por fase fracionária em função da velocidade da corrida; sem novas imagens por tick. Testes de 6+ poses, variação lateral/vertical e cache PNG pré-existente aprovados.

### Evidências e isolamento
- CI incremental `#42057063672`: **SUCCESS**. Pygame-ce 2.5.8 em Python 3.13; import integral do motor sem `main()`; 8 testes do tutorial, 4 de câmera/céu, 2 de pombo, 2 de módulo canônico, regressões QA792/790/789.
- Benchmarks A/B de 260 RGBA para preclear e fluxo direto, ambos com igualdade de pixels; fluxo direto também exige comprovante de ausência do buffer na `_city_surfaces`. Benchmark clássico da Cidade com 260 buffers e período de cinco quadros preservado.
- Nenhum APK/AAB, benchmark ou medição no Galaxy A54 neste ciclo. Não há comprovação de performance no Android. Nada em `main.py`, `JOGAR.py`, código DEV, pets, saves, assets ou workflows Android/AAB foi alterado.
- **Ainda pendentes:** reconstrução profunda de todos os passes do 2.5D, medição em hardware real, polimento de cada sprite do elenco, mais inimigos específicos para os seis biomas adicionais, reforma completa da arquitetura/migração dos demais arquivos, suite de teste de jogabilidade real multi-minuto, e homologação do tutorial/gestos MEmu/A54. Não declarar todos os itens como finalizados.


## R23 — Nova extensão: 6 inimigos inéditos e mapa normal modular
- **Seis adversários por bioma, além do Boneco de Neve N5:** Cidade C5 Carrinho de Limpeza (pista, rodinhas e pequeno desvio lateral); Deserto D5 Besouro das Dunas (carapaça articulada e deslocamento rasteiro); Vulcão V5 Golem de Cinzas (rocha fissurada e batida curta); Floresta F5 Sapo de Folhas (saltos leves); Cidade Futurista CF5 Robô Varredor (robô terrestre com antena/leds, sem contaminar outros biomas); Ilhas Celestes IC5 Guardião das Nuvens (criatura de cristal/asa e oscilação curta). Todos reutilizam só três poses cacheadas do próprio jogo, desenhadas uma vez no primeiro spawn, sem arquivos PNG novos e sem alocações no update. Base de colisão regular e limites de altura próprios; surgem depois de 750 m e sua chance cresce de maneira suave.
- **Neve/Deserto normal RGBA:** o renderizador modular reescreve o target 450×500 ao escalar o composto low-res. A limpeza prévia do buffer para o mapa normal foi suprimida **somente nesses dois biomas**. Primeiro estudo de 40 quadros por bioma (160 hashes RGBA) com diferenças 0 e p50 normal -6,44% na Neve, -6,91% no Deserto; os outros passes foram preservados porque havia regressões/variância. O gate atualizado agora é bloqueante e compara controle x candidato isolados.
- Homologação real de hitboxes, justiça no spawn, desempenho e legibilidade no Android continua pendente. Mudanças intencionais na variedade de obstáculos não implicam igualdade de pixels ou sequência RNG da corrida completa com a QA792.

## R23 — consolidação das duas frentes (migração + pós-sprites, 05/11/2026)
- **Migração em massa adicional:** 15 módulos visuais/históricos de acessibilidade, Fase B v3270–3276, acabamento, profundidade, composição, bruma, contornos e texturas foram realocados sem alterar uma linha do conteúdo canônico. O total **R23 passa de 21 para 36 módulos**, com wrappers `sys.modules` nos caminhos antigos; `tests/test_qa_r23_migracao_modulos_v327793.py` e o CI comparam os 36 blobs à QA792 e importam módulo antigo e novo para garantir identidade. Não apagar as fontes/aliases antigas ainda: dependências de Android e preflights permanecem.
- **Instrumentação nova de pós-sprites:** `qa_a54/benchmark_postsprites_v327793.py`, 2 séries de 240 quadros SDL dummy, usando `SistemaClima` e `GameFeel` reais mais 48 sprites sintéticos; 8 amostras RGBA iguais entre ambas as séries. P95 de referência no runner Linux: cinzas **0,376 ms**, chuva ácida **0,372 ms**, areia **0,353 ms**, câmera **0,321 ms**, GameFeel **0,180 ms**, grupo de 48 sprites **0,052 ms**. Isso NÃO mede o frame completo ou o p95 do A54 e não demonstra a causa dos 64,7 ms relatados no hardware. Nenhuma alteração especulativa de efeito/paleta foi integrada.
- Mantidos os ganhos já medidos com pixels exatos no 2.5D: limpeza redundante removida, fluxo direto sem buffer 450x500, normal modular parcialmente otimizado e batch FABRIK condicionado a sprites maiores. O benchmark/maratona dos 7 biomas, testes pygame-ce/AST/RGBA, saves protegidos, compatibilidade de imports e integridade do Android permanecem gates bloqueantes.
- Não alterados **main.py, JOGAR.py, DEV, pets, saves, assets nem workflows Android/AAB**. Mesmo número de versão `v3.277.93-QA`, conforme o pedido de uma versão única; APK/AAB não compilados.
- **Ainda pendentes:** homologação Galaxy A54/MEmu, otimização profunda comprovada dos 64,7 ms pós-sprites e 88,6 ms do quinto quadro no hardware real, reestruturação artística total e exclusão segura dos arquivos legados depois da migração integral.
