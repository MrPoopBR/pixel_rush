# PIXEL RUSH v3.277.86-QA — R16 Cidade / overdraw dos mapas
Data: 5/11/2026
Branch: `qa/r16-city-opaque-overdraw-v3.277.86`
Base imutável: QA785 commit `3574963d8e127ab106a39b5dec426aaefe175ebf`

## Problema e solução
O mundo Cidade 2.5D ainda faz blits de `far` e `mid` para os mapas
`normal` e `flow` a cada quinto quadro. As superfícies do plano `near`
são 100% opacas (alfa 255 em TODOS os pixels) e cobrem toda a largura
lógica de 450 pixels ao fim desses canais. Assim, a composição posterior
sobrepõe inteiramente os pixels anteriores. A v3.277.86 **deixa de
rasterizar somente esses chunks invisíveis**. Não reduz resolução, remove
detalhes, manipula cores, usa filtros ou modifica o mundo visual `image`.

## Proteções
O novo módulo QA `pixelrush_qa_city_opaque_overdraw_v327786.py`
verifica TODOS os bytes alfa de TODOS os atlas `near` usados nos canais
`normal` e `flow` após o bootstrap real. Confere formato, tamanho,
`SRCALPHA`, colorkey e ordem das camadas. O atalho é específico da
instância da Cidade e tem teste de identidade da Surface para voltar
ao original quando o atlas for substituído. Nunca altera os outros canais
`image`, `fxmask`, `geometry` ou `material`; sprites urbanos,
iluminação e reflexos seguem idênticos. Mantém o cache QA785 com 20 slots.

Somente o perfil Android QA habilita o recurso por padrão.
Rollback: `PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW=0` antes do boot.
Sem aumento de cache ou novas Surfaces persistentes.

## Evidência de laboratório (pygame-ce 2.5.8 / Linux)
Workflow R16 LAB: `41965990223` — SUCCESS.
`LivingWorld('cidade')` real, 130 quadros por perfil,
cinco canais técnicos a cada quinto quadro, travessia de chunks,
normal/leve, dia/chuva/tempestade:
- **260 hashes RGBA idênticos em cada perfil**, cobrindo a imagem e os mapas.
- **114 blits redundantes suprimidos** por perfil no percurso.
- Quinto quadro COMPLETO, p50 normal: **4,8263 → 4,2096 ms** (**-12,78%**).
- Quinto quadro COMPLETO, p50 leve: **4,7964 → 4,1291 ms** (**-13,91%**).
- Mapa `normal`, p50: **0,9978 → 0,5100 ms** (normal).
- Mapa `flow`, p50: **0,3805 → 0,3052 ms** (normal).
- A regressão independente do cache QA785 passou.
- RLE nos mapas foi **descartado**: alterou bytes RGBA e ficou mais lento.

Os ganhos são **offline**, não homologação de FPS, RAM e P95 no
Galaxy A54. Não marcar 32/32 por causa desse teste.

## Preservação / build
No `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py` alterou-se apenas
a string `VERSAO`. `main.py`, DEV, AAB, saves, pets, tutorial,
física, jogabilidade, assets, zoom, HUD, áudio, shaders GLES e
demais biomas permanecem inalterados. `buildozer.spec`: somente versão
e código numérico. Não compilar APK/AAB nesta entrega.
