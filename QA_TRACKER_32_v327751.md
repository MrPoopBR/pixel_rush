# PIXEL RUSH — Tracker auditado das 32 melhorias (v3.277.51-QA)

**Fonte inicial:** `QA_AUDITORIA_32_v327738.md`; reavaliação com código até v3.277.51 e evidências anteriores da v3.277.47.  
**Critério:** *concluída no código/QA offline* significa técnica presente e com testes focados; **não implica FPS Android comprovado nem todas as 32 homologadas**. *Parcial* significa atuação limitada a alguns cenários, flag OFF, falta de teste integral ou pré-carregamento não integrado; *pendente* significa proposta ainda não integrada ao render real.

**Resultado da integração em código (não homologação): 12/32 anteriormente concluídas offline (37,5%); 20/32 parciais (62,5%); 0/32 sem integração inicial. Total 32/32 catalogadas. A maioria ainda NÃO está concluída nem validada.**
**Homologação de ganhos em aparelho Android para esta versão: não realizada na v3.277.51, conforme solicitação do usuário.**

| # | Melhoria das 32 | Estado | Evidência e ressalva |
|---:|---|---|---|
|1|Zoom por GPU|Parcial|v749 integra wrapper de CameraCinematica com geometria de zoom original e shader fixo GLES em janela opt-in; flags OFF, paridade/ganho Android pendentes|
|2|Compositor 2.5D persistente|Parcial|v751 retira um overlay RGBA de tela inteira e os buffers de vinheta na Cidade real; desenho do quinto quadro ainda recompõe tiles e sprites|
|3|CPU/GPU híbrido|Parcial|v749 cria ponte real CPU staging Surface -> GLES2 durante display.flip, preservando HUD/input SDL e fallback SDL, totalmente OFF por padrão|
|4|Unificação zoom/posprocessamento|Parcial|v750 chama pixelrush_qa_unified_post diretamente no loop real após gamefeel/GPU FX e engloba câmera, escala, blit e flip. Implementado no QA por padrão, caminho antigo preservado; ainda não elimina transformações GPU duplas e sem gate RGBA integral|
|5|Scroll incremental de pixels|Parcial|v751 amplia wrapper real da Cidade para chunks COM sprites; desenha base cacheada e chama original somente com only_sprites=True, preservando ordem. Opt-in OFF até paridade RGBA/CPU total; strips clássicos seguem opt-in|
|6|Recorte de transparências|**Concluída (offline)**|wrapper Fase B; culling RGBA testado|
|7|Evitar grandes alocações|Parcial|v751 elimina até 13 superfícies noturnas 450x500 RGBA por Cidade via fill BLEND_RGBA_MULT; reuso geometria valida format/masks, outras alocações persistem|
|8|SIMD para smoothscale|Parcial|preflight offline/opt-in, fallback ativo, sem Android|
|9|Pré-composição de texturas|**Concluída (offline)**|atlas e superfícies estáticas presentes, testes de paridade|
|10|Remover cópias/passes|Parcial|v751 remove blit intermediário de overlay noturno em todas as recomposições com noite; elimina pygame.Rect por tile; copia fundo 5:1 ainda permanece|
|11|Cache de menus|**Concluída (offline)**|fundo e prévias limitados, sem remoção de UI dinâmica|
|12|Backend por dispositivo|Parcial|gate CPU/GPU v747 tem testes offline de rejeição segura; seleção real permanece SDL CPU|
|13|Sprites espelhados|**Concluída (offline)**|cache de props integrado|
|14|Alpha overlays|**Concluída (offline)**|reuso de masks/transições implementado|
|15|FABRIK/deformação|**Concluída (offline)**|buffers QA integrados e limitados|
|16|Culling fora da tela|Parcial|v751 evita _scaled_surface de tiles totalmente invisíveis da Cidade antes de buscar/criar texture LRU; culling restante e outros biomas ainda parciais|
|17|Agrupar blits|**Concluída (offline)**|Fase B/SDF/strips; modular atual opcional OFF, sem afirmar ganho dele|
|18|Cache céu/clima|Parcial|v751 aplica multiplicação direta da noite da Cidade, sem Surface/overlay; otimizações atmosféricas v749 mantidas, climas dos outros biomas ainda incompletos|
|19|Vinheta noturna|**Concluída (offline)**|v3192 mantém vinheta de faixas; v751 remove full-surface overlay multiplicativo da Cidade por fill BLEND_RGBA_MULT, com fallback e ensaio sintético RGB/RGBA|
|20|Pool chuva/neve/partículas|Parcial|v749 integra clima Cidade real; v748 otimiza wrapper LivingWorld para biomas clássicos, mas não cobre todas as famílias nem substitui efeitos|
|21|Fontes/labels|**Concluída (offline)**|caches limitados com atualização por necessidade|
|22|Pré-carregamento skins/pets|Parcial|previews e caches existentes, pets não validados integralmente|
|23|Pré-aquecer biomas|Parcial|atlas PROD e API v746; v747 lê/valida os 4 atlas no bootstrap sem alocação SDL ou antecipar RNG; cena do próximo bioma não é conhecida antes do sorteio|
|24|Deduplicar Surfaces|Parcial|v751 não aloca _night_veils na rota padrão; economia potencial de até 11,7 MB lógicos/instância Cidade, além de reuso geometry_view; outras Surfaces ainda duplicadas|
|25|Limites globais de cache|Parcial|v751 registra último uso de cada mapa FX da cena real e preserva superfícies quentes sob RSS; limpa somente mapas frios, vinhetas antigas e caches frios fora do quinto quadro|
|26|Pausas GC|Parcial|v751 evita alocação de 13 véus noturnos e Rect por tile, além de reuso geometry; não muda thresholds ou GC real sem evidência Android|
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

**Ação de impacto direto sem trocar visual:** `pixelrush_city2_v3124` aplica a mesma noite via `target.fill(...,special_flags=BLEND_RGBA_MULT)` em vez de Surface RGBA + blit. Isso elimina uma passagem full-frame e o conjunto de até treze véus (cada 450×500×4 bytes). O antigo caminho permanece selecionável por `PIXELRUSH_QA_DIRECT_NIGHT_MULT=0` na inicialização. Ensaios locais sintéticos 24/24 RGB/RGBA idênticos; gate integrado de cenas e CPU está preparado, não executado.

**Menos custo Python por tile:** `pixelrush_city2_v3118` agora deixa o SDL recortar o blit de base e cull antes de buscar textura se totalmente invisível. Não mexe no recorte dos sprites. Flag `PIXELRUSH_QA_CITY_NATIVE_CLIP=0` no boot reverte. Ensaios locais sintéticos 56/56 idênticos.

**Scroll mais abrangente, mas NÃO aprovado:** `pixelrush_qa_incremental_scene_v327750` pode desenhar a base reutilizada e entregar o desenho de sprites à rotina original `only_sprites=True`, para preservar animações. Permanece OFF por padrão: a cópia da Surface 450x500 pode ser mais cara que um blit direto, e sem benchmark integrado não se pode forçar a ativação. Não usar contagem de chamadas isoladas como prova de FPS.

**RAM sem serrilhar desempenho:** `pixelrush_qa_render_v327729` marca o uso de `geometry/normal/material/flow/fxmask` por bioma/frame. `EscalonadorTrimQA` deixa vivos os mapas em uso recente, evitando que a pressão RSS gere recriações caras. Formatos de `_geometry_view` agora verificam masks e SRCALPHA antes de reutilizar.

### Plano restante para as 20 parciais

As frentes de GPU/driver (#1/#3/#8/#12/#28/#29/#32) continuam dependentes de identidade pixel-exata e ganho do hardware real; não foi pedido teste Android. A eliminação de todo frame completo (#2/#4/#5/#10) ainda depende de validar animação, transparência e latência sem trocar a aparência. Outros biomas/efeitos (#7/#16/#18/#20/#24/#25/#26) ainda têm alocações e renderizações pontuais não cobertas. Skins/pets (#22) e pré-aquecimento de bioma futuro (#23) não podem alterar RNG, gameplay ou acesso aos saves.

**Resultado atual conservador (implementação != homologação): 12 concluídas em código/QA offline anterior; 20 parciais; 0 sem integração inicial. Nenhuma conclusão adicional reivindicada.** Os gates `tests/test_qa_hotpath_v327751.py`, `.github/scripts/qa_benchmark_hotpath_v327751.py` e workflow manual `.github/workflows/qa-offline-v327751.yml` estão PREPARADOS, não executados nesta entrega.

Escopo preservado: main, DEV, pets, saves, input, física, HUD, sprites, atlas, visual, tempo do jogo, render cache 1:5, APK/AAB e Android.
