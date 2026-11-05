# R22 — organização de módulos históricos e classes

Base QA791 `aafbb354b78fc7be50013176cd9847f6ff4729bc` — branch `qa/r22-classes-historicos-v3.277.92`.

## Inventário e critérios
Na base havia **341 módulos Python na raiz** e **57 arquivos Markdown**. Os 50 nomes QA incluem 47 citados por testes/preflights históricos e 3 aliases já migrados. Não mover os QA pinados por hash. O motor atual ainda tem 15.928 linhas; jogador, obstáculos, clima, parallax, som e loop dependem de estado global, logo não foram extraídos nesta etapa.

Migrações byte-exatas de módulos históricos, mantendo aliases de mesmo objeto para import legado:
- `pixelrush_touch_v3229.py` → `src/pixelrush/systems/touch_v3229.py`
- `pixelrush_aprendizado_v3208.py` → `src/pixelrush/systems/contextual_learning_v3208.py`
- `pixelrush_feedback_v3190.py` → `src/pixelrush/ui/feedback_v3190.py`
- `pixelrush_percursos_v3191.py` → `src/pixelrush/systems/route_variety_v3191.py`
- `pixelrush_rotas_v3225.py` → `src/pixelrush/systems/biome_routes_v3225.py`
- `pixelrush_hidrante_cidade_v3276.py` → `src/pixelrush/entities/enemies/city_hydrant_v3276.py`

Os módulos originais não têm referências a `__file__`; `pixelrush_variantes_v3238.py`, que usa `__file__` para localizar atlas, foi **rejeitado** para não quebrar sprites. Preflights recentes QA756, QA758, QA774–776 e auditorias de Android consultados antes da migração, sem encontrar fixação de SHA para os seis candidatos. Todos os seis permanecem acessíveis pelos nomes antigos por `sys.modules`, sem wrappers no caminho por quadro. A raiz **continua com 341 arquivos .py** — não apresentar migração de módulo como redução da raiz.

Extração AST-identica do motor: `MonitorQualidadeVisual` em `src/pixelrush/performance/quality_monitor.py`; `Moeda` e `PoolManager` em `src/pixelrush/entities/collectibles.py`. Constantes de cores/transparência e E_ANDROID associadas uma vez antes da criação das instâncias. Reaproveitamento de `Particula` da QA791; sem introduzir novo pool/cache/loop.

Limites: não alterar player, physics, colisões, RNG efetivo, atmosfera, HUD, tutorial, pets, saves, main.py, JOGAR.py, DEV, AAB, recursos, nem políticas de apresentação. Checar AST integral, RNG, pool, RGBA das moedas/hidrante, import identidade, Cidade (260 RGBA por perfil), viewport e versão. Sem APK/AAB. **Nenhum ganho de FPS afirmado**. Galaxy A54 ainda sem homologação da reorganização.
