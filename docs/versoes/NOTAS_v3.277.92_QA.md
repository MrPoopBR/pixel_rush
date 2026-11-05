# PIXEL RUSH v3.277.92-QA — R22: classes e módulos históricos

**Base:** QA791 `aafbb354b78fc7be50013176cd9847f6ff4729bc`. **Branch:** `qa/r22-classes-historicos-v3.277.92`.

Três classes do motor, `Moeda`, `PoolManager` e `MonitorQualidadeVisual`, extraídas com métodos e AST idênticos; dependências de constantes ligadas somente na inicialização. Mantidos cache único de moedas (120 no pool), 250 partículas e mesma classe canônica de partículas da QA791.

Seis módulos históricos migrados byte a byte: touch v3229, aprendizado v3208, feedback v3190, percursos v3191, rotas v3225 e hidrante Cidade v3276. Adaptadores nos nomes antigos mantêm identidade com módulos canônicos em `src/pixelrush/`. Raiz permanece com 341 nomes Python. Inventário e bloqueios em `docs/arquitetura/INVENTARIO_R22_v327792.md`.

Versão do motor `v3.277.92-QA-ANDROID-RC`; Buildozer só muda `version` 3.277.92 e `android.numeric_version` 327792. Testes AST, pygame-ce, RNG, RGBA, imports e viewport preparados em QA isolado. Nenhuma alteração intencional de física, jogabilidade, arte, sprites, HUD, tutorial, pets, saves, main, DEV, AAB, assets; nenhum APK/AAB; Android A54 não homologado.
