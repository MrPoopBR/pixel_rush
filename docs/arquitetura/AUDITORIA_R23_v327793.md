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
