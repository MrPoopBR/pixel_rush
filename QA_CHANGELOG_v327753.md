# PIXEL RUSH v3.277.53-QA — CPU do quinto quadro + scroll 2.5D real

**Origem:** `qa/android-full-performance-v3.277.52`  
**Branch isolada:** `qa/android-full-performance-v3.277.53`  
**Versão QA:** `v3.277.53-QA-ANDROID-RC`  
**Metadados Buildozer:** `3.277.53` / `327753` (**sem compilar APK/Android**).

## Objetivo 1 — Reduzir cópias/passes CPU e RAM no frame real

**A. Primeiro plano transparente da Cidade v3125 — ON, com validação do conteúdo**
- `pixelrush_qa_hotpath_v327753.py` intercepta `CityPilotScene.__init__` e `render_scene`, e verifica as variantes FG *quando a Cidade é criada*, fora do quinto quadro. A camada FG de `pixelrush_city2_v3125.py` contém fontes de imagem transparentes e nenhum sprite; desenhá-las seria nulo. Mantém a atualização idêntica de `_last_state` e delega ao método original se houver sprites/alpha não-vazio/cena diferente.
- Flags de rollback: `PIXELRUSH_QA_CITY_EMPTY_FG=0`. Sem alterações em vegetação próxima, cenário near, props, obstáculos, HUD ou colisões; somente descarta o passe FG comprovadamente inerte na arte atual. Nenhuma textura foi substituída.

**B. Strip clássico com um blit — ON, preservando o batch quando necessário**
- A mesma rotina QA intercepta `LivingWorld._blit_strip`. Quando `strip_width - off >= WIDTH`, a faixa visível vem de um só blit. Neste caso usa `target.blit(strip,(-off,TOP))` em vez da lista Python e `target.blits` com uma única operação. Caso haja duas ou mais faixas, chama o método original sem modificar parâmetros/ordem. Fallback `PIXELRUSH_QA_STRIP_ONE_BLIT=0`.
- **Evidência direcionada disponível:** ensaio local Pygame-ce 2.5.8 comparou 30 casos de strips RGB/RGBA com alpha de superfície em posições de recorte, todos com bytes RGBA iguais. Seis casos de superfície totalmente transparente também não modificaram pixels no alvo. Esses ensaios **não são** a homologação da PIXEL RUSH completa.

**C. Sonda de RAM/driver tirada do quadro 180 — ON com fallback**
- `pixelrush_qa_performance_integrated_v327742.py` realiza a sondagem a cada 180 apresentações, mas na fase **181, 361, 541...** quando `EscalonadorTrimQA` está instalado, evitando coincidir com o redraw do fundo (5:1). O período não foi alterado. A limpeza parcelada continua fora de múltiplos de cinco.
- `PIXELRUSH_QA_TRIM_PROBE_PHASE=0` conserva o frame 180 do histórico para os testes v748 e rollback. O fallback quando o escalonador não está disponível permanece no frame 180. Nenhuma mudança de física, FPS, GC, HUD ou tempo de jogo.

## Objetivo 2 — Aprofundar scroll incremental pixel-exato sem ativação prematura

**D. Cache por escopo, formato RGBA validado e menos churn**
- `pixelrush_qa_incremental_scene_v327750.py` aceita `PIXELRUSH_QA_CITY_SCROLL_SCOPE=static|all`. O modo `static` mantém as duas entradas para as bases estáticas far/mid e preserva os chunks com sprites no método original. `all` preserva a pesquisa anterior que atualizava também chunks com sprites e recorria a `only_sprites=True` para animação; evita cache de base quando o source não cobre a viewport.
- A rotina só admite entrada 900×500 SRCALPHA 32 bits sem colorkey, cria buffers com máscaras idênticas às da fonte e faz `Surface.scroll` mais reconstrução parcial da faixa exposta com `BLEND_RGBA_MAX`. Em formatos atípicos retorna ao blit original. Variáveis de ambiente lidas no install, **não por chunk**. Máximo de duas Surfaces 450×500 por Cidade, até 1,8 MB lógicos; memória extra real depende do SDL.
- **Continua OFF na execução normal:** `PIXELRUSH_QA_CITY_INCREMENTAL=0` e `PIXELRUSH_QA_CLASSIC_INCREMENTAL=0`. Mesmo com igualdade RGBA sintética, um scroll completo de buffer e blit podem ser mais lentos que o blit direto. Sem ganho medido, não ativar ou declarar #5 concluída.

**E. Recuperação sob RSS e troca de bioma**
- `pixelrush_qa_cache_trim_v327748.py` descarta caches incrementais da Cidade somente quando a instância está em outro bioma e há pressão RSS; execução pelo `EscalonadorTrimQA`, fora do quinto quadro. O mundo Cidade ativo conserva seu buffer e o estado de scroll.
- Separação por instância através de `WeakKeyDictionary`; não compartilha pixels entre mundos, não mantém objetos de cena vivos após a remoção do jogo.

## Gates preparados (NÃO executados na homologação final)

`tests/test_qa_hotpath_scroll_v327753.py`: PNGs/sprites reais via CityPilotScene v3125 e testes RGB/RGBA do FG, strip, scroll estático, descarte fora da Cidade e sonda RSS na fase 181.  
`.github/scripts/qa_benchmark_hotpath_scroll_v327753.py`: CPU p50/p95/max, RSS, quadros RGBA equivalentes; executado futuramente via workflow manual.  
`.github/scripts/qa_preflight_v327753.py`: versão, SHAs, AST, integridade de arquivos protegidos e flags de rollback.  
`.github/workflows/qa-offline-v327753.yml`: exclusivamente `workflow_dispatch`. Testes legados v748 usam fase 180 e teste v751 de scroll pode usar escopo `all`, sem bloquear regressões antigas. Sem Android, Gradle, ADB, APK ou AAB.

**Status das 32 frentes:** continua **12 anteriormente concluídas offline, 20 parciais** até aprovar o comportamento completo. A implementação desta versão avança principalmente #2, #5, #7, #10, #16, #24, #25 e #26. Nenhum ganho FPS Android alegado.

## Invariantes de escopo

Branch `main`, `main.py`, DEV, produção, física, hitboxes, controles, tutorial, HUD, saves, pets, inventário, skins, áudio, qualidade visual, sprites, efeitos ativos, 5:1 do fundo, shaders, assets e todos os workflows de empacotamento APK/AAB preservados. Alterações somente na branch QA e somente em caminhos de render/diagnóstico/versão/testes solicitados. A homologação final e o APK permanecem adiados.
