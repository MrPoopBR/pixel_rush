# PIXEL RUSH — Tracker auditado das 32 melhorias (v3.277.49-QA)

**Fonte inicial:** `QA_AUDITORIA_32_v327738.md`; reavaliação com código até v3.277.49 e evidências anteriores da v3.277.47.  
**Critério:** *concluída no código/QA offline* significa técnica presente e com testes focados; **não implica FPS Android comprovado nem todas as 32 homologadas**. *Parcial* significa atuação limitada a alguns cenários, flag OFF, falta de teste integral ou pré-carregamento não integrado; *pendente* significa proposta ainda não integrada ao render real.

**Resultado: 12/32 concluídas em código/QA offline (37,5%); 15/32 parciais (46,875%); 5/32 pendentes (15,625%). Total 32/32.**
**Homologação de ganhos em aparelho Android para esta versão: 0/32 novos gates Android comprovados na v3.277.49.**

| # | Melhoria das 32 | Estado | Evidência e ressalva |
|---:|---|---|---|
|1|Zoom por GPU|Pendente|GLES shader/presenter experimental existe; gate v747 exige janela, input, HUD, RGBA e Android reais, OFF|
|2|Compositor 2.5D persistente|Parcial|v749 reutiliza o plano (posições/referências) de tiles da Cidade real entre canais de render; nenhum framebuffer extra; redraw do quinto quadro continua|
|3|CPU/GPU híbrido|Pendente|gate de backend seguro v747 recusa troca SDL Surface para OpenGL sem integração real; CPU preservada|
|4|Unificação zoom/posprocessamento|Pendente|renderer SDL e GLES laboratório ainda não têm contrato único pixel-exato integrado ao frame real|
|5|Scroll incremental de pixels|Pendente|prova isolada de strips existe; inserção no loop de cenário real sem atrasar o frame não homologada|
|6|Recorte de transparências|**Concluída (offline)**|wrapper Fase B; culling RGBA testado|
|7|Evitar grandes alocações|Parcial|v749 cache de metadados de tiles por cena/posição e constantes meteorológicas reais; grandes Surfaces do compositor permanecem|
|8|SIMD para smoothscale|Parcial|preflight offline/opt-in, fallback ativo, sem Android|
|9|Pré-composição de texturas|**Concluída (offline)**|atlas e superfícies estáticas presentes, testes de paridade|
|10|Remover cópias/passes|Parcial|v749 ativa batching modular de neve/deserto no QA, mantendo ordem; cópia integral do cache do quinto quadro ainda permanece|
|11|Cache de menus|**Concluída (offline)**|fundo e prévias limitados, sem remoção de UI dinâmica|
|12|Backend por dispositivo|Parcial|gate CPU/GPU v747 tem testes offline de rejeição segura; seleção real permanece SDL CPU|
|13|Sprites espelhados|**Concluída (offline)**|cache de props integrado|
|14|Alpha overlays|**Concluída (offline)**|reuso de masks/transições implementado|
|15|FABRIK/deformação|**Concluída (offline)**|buffers QA integrados e limitados|
|16|Culling fora da tela|Parcial|várias camadas; cobertura integral não comprovada|
|17|Agrupar blits|**Concluída (offline)**|Fase B/SDF/strips; modular atual opcional OFF, sem afirmar ganho dele|
|18|Cache céu/clima|Parcial|v749 integra otimização do CityLifeDirector.draw_atmosphere e reflexos reais da Cidade; caches meteorológicos de outros biomas ainda não totalmente cobertos|
|19|Vinheta noturna|**Concluída (offline)**|cache de faixas 12 entradas em v3192|
|20|Pool chuva/neve/partículas|Parcial|v749 integra clima Cidade real; v748 otimiza wrapper LivingWorld para biomas clássicos, mas não cobre todas as famílias nem substitui efeitos|
|21|Fontes/labels|**Concluída (offline)**|caches limitados com atualização por necessidade|
|22|Pré-carregamento skins/pets|Parcial|previews e caches existentes, pets não validados integralmente|
|23|Pré-aquecer biomas|Parcial|atlas PROD e API v746; v747 lê/valida os 4 atlas no bootstrap sem alocação SDL ou antecipar RNG; cena do próximo bioma não é conhecida antes do sorteio|
|24|Deduplicar Surfaces|Parcial|algumas duplicações eliminadas, não toda VRAM/RAM|
|25|Limites globais de cache|Parcial|v748 integra EscalonadorTrimQA após flip; sob RSS alto agenda a cada 180 quadros, no máximo 12 chaves/quadros fora do quinto; fallback legado por flag; sem prova Android|
|26|Pausas GC|Parcial|sonda existe; v748 retira apenas a VARREDURA de caches do quinto quadro, não altera política nem remove pausas reais do GC|
|27|Telemetria assíncrona|**Concluída (offline)**|worker JSON/CSV, snapshot parcelado, flush final preservado|
|28|Native/Cython seletivo|Parcial|câmera C/NEON experimental disponível, OFF até prova Android; sem Cython geral|
|29|Evitar uploads GPU|Pendente|PBO GLES3 implementado em laboratório, mas não há janela GPU compatível no jogo, upload real ainda não integrado|
|30|Apresentação final/SDL|**Concluída (offline)**|swap/cópias instrumentados; não comprova taxa de atualização Android|
|31|Atlas pré-aquecido|**Concluída (offline)**|atlas PROD SHA-256 verificados v32776 + tiles PROD v32777|
|32|VSync/driver/Perfetto|Parcial|sondas instrumentadas, Perfetto Android não coletado|

## Regra de aprovação definitiva
**A taxa 37,5% é de implementação/cobertura offline, NÃO uma taxa de otimizações validadas por desempenho no Android.** Para encerrar as 32 como pacote, falta a rodada única de homologação Android, mais gates de gameplay completo/performance/cadência. Não declarar resultados de testes de atlas base `world_v3130` como equivalentes a `world_prod_v32777`, nem confundir cenário Linux com frame real Android. Nenhum APK compilado nesta tarefa.

## Bloqueios técnicos específicos para concluir as 20 restantes

Para respeitar *absolutamente* as funções e pixels, os cinco itens dependentes de GPU (#1, #3, #4, #5 e #29) não podem ser marcados como concluídos pela mera presença de classes experimentais. O renderer atual usa `pygame.display.set_mode` com `Surface`; o laboratório GLES abre outra janela e não fornece entrada/HUD compatíveis com a produção. O shader GPU também apresentou divergências de arredondamento no passado. O gate v747 recusa trocar a saída sem integração/igualdade total.

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

**Placar mantido até comprovação de integração e regressão:** 12 concluídas, 15 parciais, 5 pendentes. Melhorias reais em três frentes parciais não equivalem à conclusão delas.

## Avanços da v3.277.49-QA (somente branch isolada)

**Atualizações efetivamente conectadas ao jogo QA:**
- #2: `pixelrush_qa_city_tiles_v327749.py` intercepta o método `_layer_tiles` de **CityPilotScene v3125**, que é a classe real de Cidade utilizada pelo `LivingWorld`. Planos idênticos para image/normal/geometry/material/fxmask/flow de mesma posição podem reutilizar tuples de tiles. A cada novo `travel`, descarta o plano anterior; usa WeakKeyDictionary por cena sem duplicar pixels. Fallback por `PIXELRUSH_QA_CIDADE_TILE_PLAN=0`. Benefício restrito à renderização multicanal; não elimina a composição de cada quinto quadro no caminho comum somente image.
- #18/#20: `pixelrush_qa_city_weather_v327749.py` intercepta **CityLifeDirector.draw_atmosphere** e **draw_wet_reflections** da Cidade real, pré-calcula deslocamentos iguais por quadro e conserva SDL, `int`, cores, número de primitivas e ordem. Fallback `PIXELRUSH_QA_CITY_WEATHER_FAST=0`.
- #10/#17: batching dos dois tiles sobrepostos no módulo de neve/deserto `pixelrush_qa_modular_batch_v327744.py` habilitado por padrão **apenas na cópia QA**, mantendo `PIXELRUSH_QA_MODULAR_BATCH=0` para rollback imediato. Testes RGBA históricos cobriram subconjunto de condições; medição comparativa de CPU/Jitter Android pendente.
- #7/#24/#25: os planos de tiles não armazenam imagens nem criam novos buffers persistentes; continuam os LRUs e a limpeza RSS v748 com proteção multi-instância. Redução de duplicação de memória de texturas **não comprovada**; não marcar #24 concluída por confundir tuplas com surfaces.
- #26: GC Python original, somente limpeza de cache fria parcelada da v748. Coletor não foi modificado nem declarado resolvido.

**Cobertura preparada, não executada por solicitação do usuário:** `tests/test_qa_cidade_real_v327749.py`, `.github/scripts/qa_benchmark_cidade_v327749.py`, `.github/scripts/qa_preflight_v327749.py` e workflow **manual-only** `.github/workflows/qa-offline-v327749.yml`. Nenhum APK/Android/ADB, nenhum ganho de FPS do Android alegado. Testes e benchmark aguardam execução posterior, sem impedir trabalho de implementação.

**O que realmente impede 32/32 hoje:** integração segura do presenter GLES na janela SDL existente (#1/#3/#4/#29), paridade e tempo comprovados da rolagem incremental no caminho de Cidade real (#5), testes integrais não realizados de clouds/pets/GC/RSS e clock de driver Android (#12/#22/#25/#26/#28/#32). Implementar APIs laboratoriais não autoriza marcá-las como concluídas.

**Placar conservador ainda: 12 concluídas offline, 15 parciais, 5 pendentes**. A nova branch melhora código real de diversas parciais, mas não conclui as 32 nem declara ganho de FPS antes de medir.
