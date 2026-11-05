# PIXEL RUSH v3.277.52-QA — Notas de implementação

**Origem:** `qa/android-full-performance-v3.277.51`  
**Branch de destino:** `qa/android-full-performance-v3.277.52`  
**Versão do jogo QA:** `v3.277.52-QA-ANDROID-RC`  
**Metadados de empacotamento (SEM BUILD):** `3.277.52` / `327752`

## A) Auditoria da v751 — somente leitura
- Vinte frentes parciais classificadas individualmente por impacto, dificuldade, risco visual/funcional e gate necessário. Arquivo `QA_AUDITORIA_20_BASE_v327751.md`.
- Priorizar CPU do quinto quadro e deduplicação; não antecipar GPU, AArch64, PBO, driver/VSync, saves/pets ou escolha do bioma futuro sem prova real.

## B) Mudanças no caminho real QA v752

**#7/#10/#18/#20 — clima Neve/Deserto:** `pixelrush_biomes2_v3128.ModularBiomeScene.render_scene` não executa `_weather.fill` e `low.blit(_weather)` quando a camada de partículas meteorológicas estaria integralmente transparente. Não troca cor, visibilidade, frequência nem ordem de nenhuma partícula, e ao voltar a nevar/chover areia limpa e desenha como antes. `PIXELRUSH_QA_MODULAR_WEATHER_SKIP=0` usa caminho antigo. Valor padrão QA: ON.

**#7/#24 — níveis diurnos de textura:** `pixelrush_biomes2_v3128._prepare` reaproveita a Surface original da textura quando `level==0`, evitando uma cópia sem alteração RGB/alpha. No Deserto com distritos reais `pixelrush_biomes2_v3130._tile_map` usa o `src` no mesmo nível, evitando `Surface.copy`, fill multiplicativo de identidade e regravação de pixels de lâmpadas que já têm cor correta. O source é imutável durante a apresentação. `PIXELRUSH_QA_SHARE_DAYLIGHT=0` volta à geração antiga. Valor padrão: ON. Ganho lógico máximo por textura omitida: 225×250×4 bytes, sem comprovação de RSS Android.

**#2/#10/#26 — eliminar cache sem hits:** `pixelrush_qa_city_tiles_v327749` usa padrão `auto`; quando o jogo usa backend SDL CPU sem passes de imagem/normal/material múltiplos, não instala o cache de planos que criava tuples temporários sem hits relevantes no quinto quadro. `PIXELRUSH_QA_CIDADE_TILE_PLAN=1` força modo anterior. Tratamento de exceção corrigido para não tentar desenhar novamente após falha do consumidor do gerador.

**#7/#10/#24 — geometria sem segundo buffer (experimental):** `pixelrush_qa_render_v327729` identifica a Surface geometry que pertence ao mundo real e pode oferecê-la a `CityPilotScene` e `ModularBiomeScene` como `_geometry_view`. Não afeta surfaces temporárias. Se o modo for desativado e um snapshot independente voltar a ser necessário, cria nova cópia em vez de executar scale sobre si. `PIXELRUSH_QA_GEOMETRY_BORROW=0` padrão OFF, até teste de uso por ambient_occlusion, vida útil das Surfaces, multi-instância, mudanças de bioma e shader GPU.

**#5 — scroll incremental:** wrapper real e rollback anteriores preservados, sem ativar buffer adicional que pode piorar CPU/RSS. NÃO declarar #5 concluída.

## Gates preparados, sem homologação final
- `tests/test_qa_render_memory_v327752.py` cobre RGBA Neve/Deserto com neve/areia e tempo seco, aliases dos tiles diurnos, buffer geometry e plano de tiles automático, inclusive teste de exceção do consumidor do generator.
- `.github/scripts/qa_benchmark_render_memory_v327752.py` prepara comparação CPU e RSS por bioma e métricas de buffers lógicos deduplicados; relatórios têm flags `android_testado=false`, `fps_android_comprovado=false`.
- `.github/scripts/qa_preflight_v327752.py` prepara verificação estática de hash, versão, flags de retorno, sintaxe e workflow exclusivamente manual.
- `.github/workflows/qa-offline-v327752.yml` depende somente de `workflow_dispatch`; não executar automaticamente testes nem builds Android.

**Sem resultado alegado de FPS Android, tempo de frame em corrida completa ou conclusão de novas frentes.** Status conservador: 12 antigas concluídas offline, 20 parciais.

## Preservação de escopo
Sem modificações em `main.py`, DEV, branch principal, física, hitboxes, moedas, tutorial, saves, pets, skins, HUD, entrada, áudio, regras, arte, 5:1 cache do fundo, efeitos de clima ativos, workflows APK/AAB ou compilação/ADB Android. Arquivos do runtime alterados somente no ramo QA isolado: `pixelrush_biomes2_v3128.py`, `pixelrush_biomes2_v3130.py`, `pixelrush_qa_city_tiles_v327749.py`, `pixelrush_qa_render_v327729.py`, `pixelrush_city2_v3124.py` (e metadados de versão).
