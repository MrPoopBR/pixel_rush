# PIXEL RUSH v3.277.84-QA — GLES3 fisico em duas passagens

**Origem:** v3.277.83-QA (`06f0c4f41a1b6f277e782d9fe8fb62ed9801df1a`).
**Branch:** `qa/r14-gles-fisico-pixel-exato-v3.277.84`.
**Escopo:** apenas infraestrutura QA GLES e testes. Nenhum APK/AAB.

## Mudanca integrada (isolada e OFF por padrao)

1. **Render camera logico 450×800 no FBO RGBA8** pelo shader preexistente homologado somente na bancada.
2. **Apresentar no tamanho fisico com segunda passagem GLES3** usando texelFetch e coordenadas inteiras de alta precisao. A regra de amostragem imita o `pygame.transform.scale`: passos de 16 bits, coordenadas no centro do pixel, orientacao Y invertida; funciona inclusive nas escalas fracionarias.
3. Solicitar canal **alpha8** somente na janela experimental GLES fullscreen.
4. **Gate de boot obrigatorio:** compara 8 quadros fisicos RGBA completos (inclusive RGB oculto quando alpha=0) e mede p50 de GPU (inclui glFinish) contra CPU pygame-ce. O candidato so e selecionado se GPU for >=15% mais rapida e economizar >=0,15ms. Sem ganho/paridade/ES3, retorna para SDL SCALED|FULLSCREEN com flags originais. `PIXELRUSH_QA_GLES_FULLSCREEN_PROBE` continua OFF por padrao; nenhuma mudanca no profile normal.
5. Telemetria QA registra preflight fisico, ganho, causa do fallback e numero de quadros de duas passagens.

## Evidencia offline

- **RGBA:** 8 padroes por resolucao em 1024×1280, 945×2048, 1080×2340, 750×1600 e 720×1600 com pygame-ce 2.5.8 + Mesa GLES3: zero diferencas, inclusive transparency/zoom/foco.
- **Cena real:** seis quadros Cidade por resolucao 945×2048 e 1080×2340 (dia/chuva/tempestade, opaco e translucido): zero bytes diferentes.
- **Velocidade dentro da rota GLES fullscreen:** antigo shader de uma passagem ~28ms p50 a 945×2048 (zoom 2,5%); novo ~10–11ms. Melhoria do candidato GPU na bancada, **nao da corrida**.
- **Contra CPU pygame-ce:** o CPU p50 ~1–2ms ainda supera a GPU de duas passagens ~9–11ms no Mesa. A selecao automatica deve portanto rejeitar GPU e preservar SDL fullscreen.
- **Cidade/scroll:** tentativas de fastpath RLE, cache e recorte nao demonstraram ganho integral de mundo RGBA-identico no host. Nenhuma dessas alteracoes foi habilitada; o renderizador original e mantido. Nao marcar esse gargalo como resolvido.

## Regressao automatizada

- `tests/test_qa_r14_twopass_rgba_v327784.py`: 8 RGBA fisicos + gate local.
- `qa_a54/probe_city_twopass_v327784.py`: cena real Cidade, RGBA integral.
- `qa_a54/test_bridge_gles_fallback_v327784.py`: fallback SDL e preservacao da geometria de tela.
- `.github/workflows/qa-r14-gles-physical-v327784.yml`: somente Python3.13 pygame-ce/Mesa/Xvfb, regressao GL, C/camera e viewport; sem build Android.

## Politica de aprovacao

**Nao confundir ganho relativo dentro de GPU experimental com ganho do jogo no Galaxy A54.** GPU, PBO e NEON nao estao homologados no aparelho. O RGBA e valido para os casos exercitados no Mesa. Continua obrigatorio um teste futuro real Mali + FPS/RSS/tempos R13 antes de liberar a aceleracao.

**Nao alterados:** `main.py`, DEV, AAB, shaders/efeitos de producao, recursos, arte, hitboxes, fisica, tutorial, saves, pets e jogabilidade. O arquivo principal de jogo teve apenas a string VERSAO atualizada.
