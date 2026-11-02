# PIXEL RUSH v3.277.40-QA — Câmera, compositor persistente e GPU Android

## Versão e escopo

- Branch exclusiva: `qa/android-full-performance-v3.277.40`, criada do commit `498757c110d45a6c7e741689ee3c2b1a5f4bd1ab` da v3.277.39-QA.
- Identificador QA `v3.277.40-QA-ANDROID-RC`; Buildozer `3.277.40`, versionCode `327740`. Relatórios Android `pixelrush_qa_v327740.json` e `pixelrush_qa_frames_v327740.csv`.
- Nenhuma alteração na execução da física, cenas artísticas, câmera ativa, HUD, gameplay, dificuldade, tutorial, saves, pets ou produção. O jogo usa o compositor e a câmera **originais**.
- O protótipo GLES de v3.277.39 e os shaders fixos permanecem **desligados** no jogo. Nenhum novo shader habilitado.

## Novos experimentos

### 1. Compositor 2.5D persistente, faixas sujas

Arquivo: `pixelrush_qa_rolling_v327740.py` (NOVO, não importado por `main.py` nem pelo jogo).

O experimento mantém uma única Surface RGBA da largura virtual e altura da faixa, com deslocamento módulo largura da textura. Um avanço de 1 px provoca `Surface.scroll(dx=-1)`, limpeza apenas da coluna exposta e blit da mesma região da textura original. Ao saltar, mudar a fonte ou formato, refaz o quadro; existe `invalidar()` explícito para mudanças de pixels na mesma fonte. Não há interpolação nem descarte de camadas. Inclui `mosaico_referencia` para provar bytes equivalentes e um gate `gate_integracao` que **não permite ativar** sem igualdade RGB/RGBA, ganho comprovado por frame completo no Android, RAM limitada e física preservada.

**Evidência de bancada Linux pygame-ce 2.5.8:** 2.160 comparações de buffer/tela com RGBA, RGB, colorkey, deslocamentos grandes e rolagem negativa passaram. Teste multícamadas adicional: três faixas RGBA, 90 quadros em alvo RGB e RGBA, pixel iguais. Todos são testes artificiais, não full-scene Android.

**Resultado de desempenho decisivo:** recompor somente o cache pode ser cerca de 5–6 vezes mais rápido do que recriar uma Surface de teste, mas isso mede a operação errada. Incluindo a composição na tela, com Surface de destino já alocada, a bancada Linux mediu aproximadamente **0,077–0,085 ms (direto)** contra **0,095–0,100 ms (persistente)** por quadro nos padrões simulados de 450x500 pixels. Portanto **não ativado**: o cache exige cópia extra de ~900 KiB por faixa, e a prova de benefício em Android não existe. O teste em CI `.github/scripts/qa_benchmark_persistent_camera_v327740.py` registra p50/p95 para as duas alternativas, no *mesmo* caminho final.

### 2. Matriz de câmera com zoom e formatos de pixel

A câmera já usa `pygame.transform.smoothscale` com buffer reutilizado. Nova bancada compara RGB e RGBA, quatro níveis de zoom (`.002`, `.01`, `.025`, `.034`) e backends disponíveis (`GENERIC`, `SSE2`, `NEON` quando aceitos), medindo p50/p95 e hash exato dos pixels. Não habilita backend por força bruta, pois diferenças de arredondamento de pixel foram identificadas em experimentos anteriores. Mantém resampling, geometria e área de corte originais.

Em Android, os valores anteriores v3.277.30-QA (p95 `camera_smoothscale` ~187,89 ms, profundidade ~143,97 ms, mundo 2.5D ~95,24 ms, FPS normal ~4,8 e replay ~26,28) indicam prioridade, mas não provam a causa atual. Os períodos instrumentados podem ser aninhados: não somar esses p95.

### 3. Caminho GLES e viabilidade real

A GPU não pode ser introduzida na janela SDL2 `WindowSurface` atual apenas alterando `blit`: é necessário um novo caminho de apresentação, sem roundtrip GPU→CPU. A sonda de v3.277.40 gera hash do shader GLES2 fixo, sem criar contexto, e mantém os gates exigindo **prova visual full-frame**, `eglSwapBuffers`, custo de upload+draw+swap, estabilidade de FPS Android e compatibilidade saves/física. A v3.277.39 já reduziu cópia temporária na preparação RGBA do protótipo, mas isso não otimiza o upload nativo da textura a cada quadro. Qualquer integração fica bloqueada.

## Gates de teste e CI

- `tests/test_qa_rolling_camera_v327740.py`: comparação de pixels de scroll estático e composição final em RGB/RGBA/colorkey, fontes diferentes, saltos, invalidação, três camadas, câmera original e gates de GPU.
- `.github/scripts/qa_benchmark_persistent_camera_v327740.py`: baseline **frame completo**, alternativa com cache, p50/p95, matriz de câmera e flags explícitas de não homologação Android; gera `qa-benchmark-persistent-camera-v327740.json`.
- `.github/scripts/qa_preflight_v327740.py`: hashes de arquivos, versão, invariantes (main, física, pets, shaders desativados), AST e dependências.
- `.github/workflows/qa-apk-debug-v327740.yml`: testes pygame e só `buildozer -v android debug`, auditoria de bibliotecas ARM64/NumPy/DT_NEEDED/ZIP_STORED/16KiB, sem executar AAB.
- Nenhum gate Android é aprovado só por sucesso em Linux. O APK debug gerado, quando houver, deve ser instalado preservando saves e comparado com v3.277.39-QA no **mesmo aparelho**; usar JSON/CSV `v327740` para FPS normal/replay, p50/p95/p99 por subsistema, RSS e temperatura.

## Decisão

**Progresso concreto:** protótipo incremental exato com invalidadores e gate, teste de três camadas e matriz de zoom/backends; descoberto que acelerar só a reconstrução do fundo não basta. **Não foi introduzida mudança experimental no renderizador ativo.** Para alto impacto seguro, priorizar otimização de câmera em hardware ARM/NEON com igualdade em frames reais, compositor de camadas persistentes que evite o blit final extra, ou GPU GLES sem cópia de volta, todos com prova Android antes de habilitar.

Preservado: main, DEV, produção, AAB, assets, gameplay, controles, física, colisões, tutorial, HUD, câmera original, pets e saves.
