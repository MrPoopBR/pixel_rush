# PIXEL RUSH v3.277.39-QA — Camera, mundo 2.5D e GPU experimental

**Branch isolada:** `qa/android-full-performance-v3.277.39`  
**Base confirmada:** `qa/android-full-performance-v3.277.38`, commit `5aca2626ff2499ac26f39f67fa5c86cda0e11aba`.  
**Versao do jogo QA:** `v3.277.39-QA-ANDROID-RC`. **APK debug:** `version 3.277.39`, `android.numeric_version=327739`.  
**Status:** implementacao QA; sem homologacao FPS/compatibilidade do novo APK em Android real.

## Diagnostico orientado por evidencias

- **Historico Android real v3.277.30-QA:** corrida ~4,8 FPS, replay ~26,28 FPS; p95 `camera_smoothscale` 187,89 ms; profundidade 143,97 ms; mundo 2.5D 95,24 ms. Medidas sobrepostas, **nao somar**.
- **Camera atual:** `CameraCinematica.aplicar` em `pixelrush_cinema_v3172.py` ja usa superficie destino persistente. Otimizacao existente `pixelrush_qa_camera_v327733.py` somente escolhe SIMD se bytes identicos e ganho suficiente; nao duplicar buffer nem forcar backend diferente.
- **Microbenchmark Linux de camera (SDL dummy, pygame-ce 2.5.8, RGB 450x800):** zoom 0,5%, 2,5%, 3,4%; GENERIC aproximadamente 2,3–2,5 ms; SSE2 aproximadamente 0,39–0,43 ms com destino reutilizado. **GENERIC vs SSE2 geraram bytes diferentes**, logo trocar backend indiscriminadamente alteraria o visual. Os numeros nao predizem Android/NEON.
- **Cidade 2.5D:** `pixelrush_city2_v3117.py` ja possui caches de flip/texturas/halos e `pixelrush_city2_v3118.py` cache de sprites escalados e clipping por viewport. Nenhum deles foi duplicado. Uma oportunidade restante era recalcular `math.sin` para os mesmos sprites de um chunk repetido dentro do mesmo quadro.
- **GPU experimental:** `pixelrush_qa_gles_present_v327735.py` fazia `pygame.image.tobytes(...,'RGBA',True)` seguido por `ctypes.create_string_buffer`, duplicando 1.440.000 bytes para a tela base 450x800. A GPU real Android nao foi medida, e o contexto SDL/GL do jogo nao esta integrado.

## Alteracoes concretas da v3.277.39

1. **`pixelrush_city2_v3118.py`**, SOMENTE na branch QA: calcula o fator de vento uma vez por chunk (e nao uma vez para cada sprite); a formula de `math.sin` e `round` continua identica para cada sprite, sem cache adicional. Ordem visual, `math.sin` original, `round`, coordenadas, recortes, sprites, climas e opacidade preservados.
2. **`pixelrush_qa_gles_present_v327735.py`**, prototipo que NAO e importado pelo jogo: substitui o segundo buffer alocado por `ctypes.cast(ctypes.c_char_p(data),ctypes.c_void_p)`. Bytes RGBA e flip permanecem iguais; `data` fica vivo durante `glTexSubImage2D`. Sem leitura da GPU e sem habilitacao da GPU no jogo.
3. **`tests/test_qa_camera_city_v327739.py`**: comparacao RGBA/RGB pixel a pixel de `_render_chunk` original vs novo com quadros, scroll, climas, map kinds e fundos; camera real `CameraCinematica` contra referencia `pygame.transform.smoothscale` nao cacheada; teste de bytes da entrada GLES; gate contra integracao prematura GLES.
4. **`.github/scripts/qa_benchmark_camera_world_v327739.py`**: benchmark de CPU com p50/p95, reutilizacao vs nova Surface, verificacao de igualdade entre backends (sem forcar otimizacao que muda pixels), custo de desenho da cidade e staging GLES. Publica `qa-benchmark-camera-world-v327739.json` nos diagnosticos CI.
5. **Telemetria e versao QA:** relatorios `pixelrush_qa_v327739.json` e `pixelrush_qa_frames_v327739.csv`; preflight de hashes `qa_preflight_v327739.py` e workflow isolado `qa-apk-debug-v327739.yml`. Nao alterados workflows AAB nem o entrypoint `main.py`.

## Testes locais independentes (Linux, NAO Android)

| Teste isolado | Resultado observado |
|---|---|
| Reuso trigonometrico em cenario sintetico pygame-ce | cerca de 0,0217 ms original vs 0,0189 ms com fator de vento fora do loop, mediana em 3 chunks sinteticos; nao e ganho global FPS |
| Camera `GENERIC` vs `SSE2` | backend mais rapido **nao** pixel-identico; troca automatica proibida |
| Camera com vs sem Surface destino | destino reutilizado reduz alocacao; caminho ja existente preservado |
| Preparacao GLES 450x800 RGBA (1,44 MB) | `create_string_buffer` ~0,826 ms vs ponteiro direto ~0,737 ms, mediana Linux; bytes identicos |
| GPU end-to-end Android/EGL real | **Nao medido**; shaders continuam desligados |

Os testes Linux sao microbenchmarks de bancada. O CI pygame usa referencias pixel-exatas de metodos reais. Ainda e necessario comparar frames completos, FPS e p95/p99 em aparelho, por bioma, corrida vs replay.

## Auditoria das 32 frentes: atualizacao parcial

Inventario integral anterior: [QA_AUDITORIA_32_v327738.md](QA_AUDITORIA_32_v327738.md).

- **#2 Compositor 2.5D:** nova eliminacao de checagens repetidas de clima por sprite na cidade; composicao completa persistente ainda **pendente**.
- **#7 e #10 Alocacoes e copias:** removida uma copia de 1,44 MB por frame **somente no prototipo GPU**, que segue desligado; nenhuma melhoria declarada na corrida real pelo GPU.
- **#8 SIMD:** comparacao concreta mostra diferencas pixelicas GENERIC/SSE2; nao forcar SIMD para evitar regressao de visual.
- **#17 Batching:** preservado trabalho comprovado de v3.277.37 e v3.277.38; nenhuma duplicacao.
- **#24 Deduplicacao:** sem novo cache: otimizacao remove redundancia de calculo, sem alocar superficies.
- **#29 Upload GPU:** `glTexSubImage2D` ainda transfere RGBA completo em cada frame; otimizacao de staging **nao resolve upload**. Proxima etapa exige prova real de GPU/transferencia e plano para evitar readback.
- **#30 Apresentacao final:** tempo de escala, blit e swap continuam instrumentados; nao mudar composicao ainda.
- **#32 Driver/Perfetto:** pendente. Nao ha p95 GPU real nem temperatura de teste da v3.277.39.

Os demais estados do inventario v3.277.38 permanecem inalterados. **Nao declarar 32/32 implementadas**.

## Gates e compatibilidade

- Toda mudanca limitada a branch QA `qa/android-full-performance-v3.277.39`, sem tocar `main`, DEV, releases, assets, saves, pets, compras, hitboxes, fisica, tutorial, audio, gameplay, UI nem AAB.
- `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py` dentro da branch QA altera apenas **string de versao**.
- Novo preflight exige SHA de fontes criticas, versao e workflow debug, e proibe modulo shader experimental no entrypoint principal.
- APK ARM64, `pygame-ce`, NumPy, `DT_NEEDED`, `ZIP_STORED`, alinhamento de 16 KiB e testes integrados so serao declarados aprovados apos evidencia do Actions.
- Para homologar desempenho, comparar JSON/CSV da v3.277.38 vs 3.277.39 no mesmo Android com corrida normal, replay, p50/p95/p99, RSS, aquecimento e travamentos.
