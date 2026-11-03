# PIXEL RUSH v3.277.43-QA — A–F: seguranca de desempenho, somente offline

**Branch isolada:** `qa/android-full-performance-v3.277.43`
**Origem imutavel:** `qa/android-full-performance-v3.277.42` @ `e90927476544b0b141002fba7e6c9d0c6c310962`
**Versao do jogo QA:** `v3.277.43-QA-ANDROID-RC` / `android.numeric_version = 327743`.
**Estado da entrega:** codigo offline; **nao foi compilado APK/AAB nem executado Android/ADB**.

## A. Benchmarks fora dos frames jogaveis
- A camera `pixelrush_qa_camera_native_auto_v327742.py` nao faz mais paridade RGBA nem suas 12 medições C/pygame na primeira aparicao do zoom. A certificacao fica disponivel via `preparar_fora_do_frame`, por opt-in `PIXELRUSH_QA_NATIVE_AUTO=1` e fora do gameplay.
- `pixelrush_qa_camera_v327733.py` nao executa teste SIMD no render. `preparar_fora_do_frame` continua disponivel para bancada quando `PIXELRUSH_QA_CAMERA_AUTOTUNE=1`.
- `pixelrush_qa_scroll_auto_v327742.py` nunca chama `_bench` na primeira faixa visivel. A aprovacao opcional e preparada explicitamente via `preparar_fora_do_frame`. Sem certificado precomputado, blits SDL originais e flags experimentais desativadas por padrao.
- O algoritmo, movimento, zoom, coordenadas, hitboxes e camera original continuam intocados; APIs opcionais permanecem presentes.

## B. Gerenciamento de memoria multi-instancia
- `_reclaim_inactive_caches` usa snapshot de todas as instancias `LivingWorld` vivas, retem a uniao dos biomas ativos e so depois limpa o atlas global `_SOURCE` de biomas frios.
- Preserva caches locais do bioma atual, transicoes e superficies em uso. Corrige a possibilidade de um mundo liberar o recurso global de outro.

## C. Regressao de nuvens
- O experimento de sete blits RGBA estava mais lento no Linux (p50 0,0278 ms contra 0,0228 ms do desenho de 28 circulos). `CityPilotScene` usa o desenho original por padrao.
- Alternativa cacheada preservada apenas com `PIXELRUSH_QA_CLOUD_CACHE=1`, para pesquisa offline, pixel-exata em RGB/RGBA, clipping e dia/noite.

## D. Telemetria sem grandes snapshots no frame
- `CapturaParceladaQA` captura no maximo duas series e 64 linhas por frame; conserva janelas de 1800 amostras e 4000 linhas CSV.
- Serializacao e percentis permanecem no worker de I/O. A etapa de envio nao recopia milhares de dicionarios ja desacoplados (`linhas_prontas=True`).
- Fluxo periodico continua a cada 600 quadros; gravacao final ainda sincroniza e salva o ultimo estado ao sair, sem mudar seus campos JSON/CSV.
- Nome dos arquivos QA atualizado para `pixelrush_qa_v327743.json` e `pixelrush_qa_frames_v327743.csv`.
- Registros coletados ao longo de varios quadros representam uma janela recente, nao um snapshot atomico de um unico instante.

## E. Testes de regressao ampliados
- `tests/test_qa_safe_performance_v327743.py`: sem benchmarks no frame, camera sem duplo zoom, scroll original, dois mundos ativos, nuvens opt-in, limite por parcela, JSON/CSV.
- `tests/test_qa_frame_completo_v327743.py`: sequencia real Cidade/Neve com clima, HUD, zoom/foco e RGBA byte-identico.
- Testes de versao e contrato de telemetria legados sincronizados com v3.277.43.

## F. Benchmark completo, offline
- `.github/scripts/qa_benchmark_frame_completo_v327743.py`: mede mundo+HUD, camera, blit/flip SDL e tempo total, p50/p95/p99 para Cidade/Neve; verifica paridade RGBA em sequencia.
- `.github/workflows/qa-offline-v327743.yml`: somente Python/pygame-ce 2.5.8, validacoes estaticas, C nativo Linux como fixture, testes SDL dummy e relatorio JSON; **NAO chama Buildozer/Gradle/ADB/Android**.
- `.github/scripts/qa_preflight_v327743.py`: valida SHA das fontes/visual de base, inalterabilidade de main/DEV/AAB, versoes, flags GLES OFF e isolamento do novo workflow.

## Escopo preservado
Sem alteracao de fisica 60 Hz, controle, jogabilidade, colisao, tutorial, dificuldade, spawns, HUD, assets, skins, pets, compras, saves, audio, renderer de producao, main ou workflows AAB. C/NEON e shaders GLES2/GLES3/PBO nao foram ligados sem homologacao Android. **Nenhum FPS Android novo foi declarado.**

## Homologacao
Aprovar gates estaticos e pygame local/offline; somente depois, quando solicitado, construir APK debug e executar uma unica rodada no aparelho, comparando FPS/p50/p95/p99 e RSS. Nao confundir benchmark Linux SDL dummy com resultado de GPU do smartphone.
