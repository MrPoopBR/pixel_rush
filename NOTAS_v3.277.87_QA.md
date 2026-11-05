# PIXEL RUSH v3.277.87-QA — R17 Cidade 2.5D / mapas técnicos

**Base:** v3.277.86-QA commit `dcce704639e2b42bfade76d93b5766cda325cc9b`.
**Branch:** `qa/r17-city-techmaps-v3.277.87` (isolada).
**Sem APK/AAB:** somente código QA e testes offline.

## Problema e solução (somente Cidade)
Depois do cache QA785 e do overdraw QA786, os canais `geometry`,
`material` e `fxmask` continuavam executando blits desnecessários a cada
quinto quadro. O módulo `pixelrush_qa_city_technical_cover_v327787.py`
adota dois recortes seletivos, sem modificar as texturas:

- **Geometry/material:** identifica a faixa inferior de todos os atlas
  `near` cuja opacidade é 255 em cada pixel. Enquanto `far` e `mid`
  desenham, limita temporariamente o clip SDL à região acima dela.
  A camada `near` sobrescreve integralmente a faixa descartada.
- **FXmask:** só recorta atlas de `far` e `mid` *sem sprites* que sejam
  RGBA=(0,0,0,0) em todos os pixels excluídos do retângulo de alfa
  significativo. O `render_scene` limpa integralmente o buffer do mapa
  antes de desenhá-lo; o recorte não é usado em chamadas avulsas de chunk.

O gate é por instância, valida tamanho 450×250, alfa, colorkey, ordem das
camadas, fonte Near e identidade do atlas. O modo só atua em destino
SRCALPHA 450×500. O clip anterior é restaurado em `finally` após
cada chunk; os blits de `image`, `normal`, `flow`, HUD, sprites dinâmicos,
iluminação, clima e câmera permanecem no caminho original.

Ativado apenas no perfil `PIXELRUSH_QA_ANDROID=1` com configuração agressiva,
ou explicitamente no laboratório. **Rollback:**
`PIXELRUSH_QA_CITY_TECH_COVER=0` antes do bootstrap, sem perder saves.
Nenhuma nova Surface persistente ou cache é criado. O orçamento de 20
texturas da QA785 continua idêntico e os skips QA786 normal/flow continuam.

## Evidências do laboratório
GitHub Actions [#41968404735](https://github.com/MrPoopBR/pixel_rush/actions/runs/41968404735)
— **SUCCESS**; Python 3.13, pygame-ce 2.5.8, SDL headless/Linux.

Foram realizadas duas repetições intercaladas off/on por perfil com
`LivingWorld('cidade')` real e o cache QA785 + QA786 **ativos nos dois lados**.
Cada repetição percorre 130 quadros com atualização de clima/noite e
travessia entre chunks, renderizando cinco mapas técnicos a cada quinto
quadro. **260 buffers RGBA comparados byte a byte por perfil e repetição**,
todos idênticos; política de redesenho 5:1 preservada.

- Quinto quadro completo normal p50: **2,7965 → 1,9473 ms** (-30,37%).
- Quinto quadro completo leve p50: **2,7987 → 2,2595 ms** (-19,26%).
- Conjunto dos três mapas normal p50: **1,9971 → 1,2368 ms** (-38,07%).
- Conjunto dos três mapas leve p50: **2,0580 → 1,5023 ms** (-27,00%).
- No percurso de cada execução otimizada: **114 chunks** parciais
  `geometry/material` e **57** `fxmask` desenhados com recorte.
- O gate de memória aprova no Linux; nenhuma textura persistente adicional.
- Atlas `near` substituído invalida a otimização na hora do render.
- Fora do `render_scene`, o caminho dos chunks fica intocado.

**Cuidado:** resultados são relativos ao Linux/pygame-ce, não indicam FPS,
RSS nem p95 homologados em hardware Samsung Galaxy A54.

## Segurança, preservação e QA
O teste `tests/test_qa_r17_city_technical_v327787.py` obriga igualdade
RGBA e ganho de pelo menos 3% no quinto quadro total, além de 10% no
conjunto de mapas, nos dois perfis. Inclui rollback, mutação de referência
do atlas e verificação da entrada de buffer com RGB oculto.
`qa_a54/smoke_city_render_integrated_v327787.py` valida a integração real
na cadeia QA e a compatibilidade com QA785+QA786; o CI isolado repete gates
de versões anteriores e testa o escopo do diff.

Preservados `main.py`, DEV, jogos LIMPA, shaders GLES, AAB, visuais,
skins, pets, tutorial, colisões, física, saves, áudio e demais biomas.
O único ajuste no arquivo `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py`
é o literal `VERSAO`. `buildozer.spec`: apenas version/nameCode.
**Nenhuma compilação Android realizada.**
