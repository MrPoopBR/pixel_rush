# PIXEL RUSH v3.277.93-QA — R23 integração de tutorial, biomas e jogabilidade

**Branch isolada:** `qa/r23-integracao-gameplay-tutorial-v3.277.93`. **Base testada:** v3.277.92-QA, commit `d8f97adf246bc593da3bb049bef2f3a5c31dd698`.
**Versão:** `v3.277.93-QA-ANDROID-RC`; Buildozer `3.277.93 / 327793`. **APK/AAB: não compilados.**
**Estado:** implementação em QA; homologação Galaxy A54, comparação de FPS/memória e aprovação final de jogabilidade dependem de testes reais.

## Código implementado nesta versão
- Tutorial obrigatório original de seis lições foi preservado como base, estendido por `src/pixelrush/ui/tutorial/premium_v327793.py`, sem substituir a física, sprites ou saves. Abertura de 300 ticks (~5 s a 60Hz) sem obstáculos; indicadores visuais pulsantes durante gesto congelado; quadro congelado reutilizado para evitar recriação do mundo 2.5D; reset de partículas com `kill()` no rebobinamento; quatro lições extras (combo real de moedas, quase-colisões guiadas e febre demonstrativa, baú, descanso/moedas); apenas a transição final ativa `tutorial_inicial_concluido`. Touch residual não deve avançar popup recém-aberto.
- Corrida: controle de swipe para cima iniciando pulo longo, e swipe para baixo no mesmo contato para descida; clique no painel de missões abre a pausa e progresso completo; retomada com contagem 3-2-1 de ticks fixos e SFX sintético; sons de passos; novo ritmo de spawn gradual de 1500ms até 730ms e tolerância de terceiro perigo após 2500m; baús (5,5%→2,6%) e letras mais raros.
- Mundos: sete biomas existentes entram na seleção aleatória sem repetição consecutiva; órbita de sol/lua contínua com ciclo de **180 segundos de simulação**; paleta ambiental interpolada; Cidade Nevada com asfalto azul-claro gelado e faixas de neve no tile cacheado; sete trilhas instrumentais próprias geradas uma única vez; movimentos dedicados a rato C1, pombo C2 e pinguim N1 com poses já cacheadas; inimigo pula-pula limitado à Cidade Futurista; spawn aéreo da Cidade usa pombo C2; novo Boneco de Neve N5 cria um projétil por aparição em alturas alternadas; bola usa imagem cacheada.
- Qualidade gráfica: `modo_grafico_leve()` já retornava `False` na base; a configuração continua fixada em `completo`. Não reativar perfil automático/leve.

## Já existentes e reutilizados (sem duplicação)
- Sistema de câmera cinematográfica, poses de corrida, efeitos de aterrissagem e transições de bioma.
- Diretor de padrões `SALTO`, `PASSAGEM`, `ESCOLHA`, `REFLEXO_CURTO/LONGO/BAIXO`, `DESCANSO` e `TRILHA`; combos/febre reais e gerente de saves.
- Renderizador 2.5D pesado em processamento por passes e cache R12/R17/R20; permanece em uso e ainda precisa de medições em Android.

## Ainda parcial / NÃO declarar concluído
- Reescrita de alto desempenho do mundo 2.5D preservando qualidade visual; benchmarks R23 não substituem análise no A54.
- Migração em massa de todos os módulos antigos e exclusão definitiva dos arquivos inúteis: caminho de imports e preflights ainda pinam muitos.
- Refinamento final de toda a arte, animações de corrida e câmera cinematográfica, cenários em todos os biomas e novos adversários exclusivos para cada um; nesta versão há melhorias pontuais, não revisão artística integral.
- Tutorial em dez etapas ainda **não homologado em hardware**; a fase de swipe-down agora contém duas pausas reais: pulo longo comandado, seguida de descida no ar no mesmo contato. O teste sintético de input FINGERDOWN → FINGERMOTION passou, mas não substitui verificação de gestos em Android.
- Testes de justiça/alcance dos baús, letras, densidade de perigos e controles multifinger em Android real. Sem alegar zero mortes e zero bugs sem validação.

## Proteções de escopo e evidência
`main.py`, `JOGAR.py`, DEV, código dos pets e arquivos de saves, todos os assets e workflows Android/APK/AAB devem permanecer byte-idênticos à QA792. Android `buildozer.spec` altera **somente os números de versão**. CI R23 confere sintaxe, pygame-ce 2.5.8, AST, RNG/objetos, 3 minutos de paleta, RGBA estável da UI, boneco de neve, integridade de arquivos e benchmark Cidade 2.5D. Não afirmar conclusão de CI antes de verificar resultado real.

## Migração adicional integrada e auditável (R23)
Foram migrados **21 módulos históricos** adicionais, com conteúdo byte-idêntico ao commit QA792 e aliases `sys.modules` nos 21 caminhos originais. A raiz não perdeu arquivos físicos porque imports Android, CI e módulos históricos ainda usam esses nomes. O manifesto completo está em `docs/arquitetura/MANIFESTO_R23_MIGRACAO_v327793.json`, com teste de identidade/importação. Inclui áudio, corredores, moedas, cenas, cinema, sombras, geometria, pista, i18n, sequências e física de áudio. NÃO mover `pixelrush_inimigos_v3221.py`, `pixelrush_profiler_v3204.py` ou `pixelrush_avisos_raros_i18n_v3247.py` indiscriminadamente: usam `__file__` para recursos e telemetria.


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


## R23 — zoom RGB diretamente no destino, sem superfície temporária
- Continuação isolada da mesma v3.277.93-QA, sem alterar main, DEV, gameplay, física, saves, pets, assets, workflows Android/APK/AAB ou aparência.
- pixelrush_gamefeel_v3152.py: acabamento_camera passa a usar transform.scale diretamente em uma subsurface do buffer existente, somente para fonte e destino RGB opacos 450x800 com formato de pixels idêntico. Remove a criação de Surface dependente do tamanho e o blit intermediário. Para alfa, SRCALPHA, colorkey, outra resolução/formato e falhas SDL: fallback integral para o método anterior.
- tests/test_qa_r23_zoom_direto_v327793.py: novo gate de 500 quadros RGBA idênticos ao legado + 4 fallbacks e 3 casos sem zoom; adicionado ao CI R23 sem compilar Android.
- Benchmark local pygame-ce 2.5.8 Python 3.13 SDL dummy: 500 RGBA idênticos; p50 do zoom original 0,4234 ms, novo 0,1848 ms, cerca de 56,3% de queda apenas nessa operação isolada. Não é ganho de FPS total nem medição no A54. CI remoto ainda deve ser verificado.
- Não declarar eliminação dos 64,7 ms pós-sprites nem homologação de hardware sem relatório real.
