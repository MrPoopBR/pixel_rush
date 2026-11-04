# PIXEL RUSH v3.277.75-QA — preparação do Galaxy A54 e campanha das 32 frentes

**Base imutável:** `qa/fechamento-parciais-v3.277.74` @ `c07fe4f0301dbb3e4d41797b4d171dceae088fe0`.

**Nova branch isolada:** `qa/a54-fechamento-32-v3.277.75`.

## Alterações integradas
- Versão de QA da engine `v3.277.75-QA-ANDROID-RC` e `buildozer.spec` versionName 3.277.75 / numeric_version 327775.
- Preflight independente v775, preservando SHA de `main.py`, engine modular neve/deserto, câmera native e ponte GPU.
- Gate QA A54 cobrindo explicitamente as dez frentes, com teste de fallback CPU/GPU/SDL, PBO GLES2 bloqueado, scroll, SIMD, NEON desativado, Perfetto e preservação de pixels.
- Testes herdados da v774 com atualização **apenas** das asserções de versão nos quatro arquivos v775.
- Workflows isolados: suíte offline pygame-ce, GPU GLES2/GLES3 Mesa RGBA pixel-exato, cross-build ARM64 ELF/16 KiB e APK debug para Galaxy A54 (sem AAB).
- Scripts de coleta ADB sem root e de instalação `adb install -r`; nunca executar `adb uninstall`, `pm clear`, downgrade ou editar saves. Não enviar serial ou outros dados pessoais por padrão.

## Critérios de conclusão das frentes
- **#1 GPU zoom:** imagem RGB/RGBA byte-idêntica ao SDL original com foco/zoom, backend Mali-G68 real; frame completo melhor e estável.
- **#3 CPU/GPU híbrido:** SDL input, HUD e context loss/recovery sem regressão, sem readback no loop e melhor FPS no A54.
- **#5 scroll:** origem RLE e não RLE, 4 bytes RGBA incluindo RGB oculto, redução efetiva de tempo do mundo, sem RAM excessiva.
- **#7 alocações:** comparação GC/RSS/buffers no jogo real, ganho positivo sem alias em uso.
- **#8 SIMD:** backend NEON/GENERIC exato no A54 e mediana/p95 melhores que o backend CPU padrão.
- **#10 passes:** profiler por sky/world/fx/HUD/replay/simulação, custo residual e frame completo menores sem mudar visual.
- **#12 backend:** detectar GLES2/3, motorista, limites reais, optar somente com gates e fallback.
- **#28 C/NEON:** biblioteca ARM64 carregável e arredondamento byte-idêntico ao SDL; nenhum símbolo/ABI quebrado.
- **#29 PBO:** driver GLES3 real, buffers com upload correto sem regressão/tearing; se falhar, upload direto.
- **#32 VSync/Perfetto:** capturas de jank do A54 e eventos ATrace/SurfaceFlinger por frame, sem mascarar quedas de FPS.

## Separação rigorosa de evidências
1. **Gates offline**: testes pygame-ce SDL dummy, Mesa software GPU, ELF no runner Ubuntu. Passar não equivale a homologação do Galaxy A54.
2. **APK compilado e auditado**: confirma distribuição/ABI/ZIP/alinhamento e entrada da QA; não comprova GPU do aparelho.
3. **Coleta A54 real**: exigirá conectar o aparelho físico por USB e executar os scripts locais após instalar o APK compatível e conferir saves. O celular não está conectado ao runner GitHub.
4. **Promoção de frente**: exige prova específica correspondente. Componentes GPU, NEON e PBO continuam opt-in OFF até critérios completos.

**Placar antes de testes no Galaxy A54: 22/32 concluídas offline; 10/32 parciais; 0/32 homologadas em hardware Android físico.** Não marcar 32/32 por expectativa.

**Não alterado:** `main.py`, DEV, AAB de publicação, assets, tutorial, sons, pets, saves, física, jogabilidade, zoom efetivo, câmera efetiva, shaders, cadência do 5º quadro. Somente identificação QA, testes, relatórios e workflows isolados.


## Auditoria de fechamento das falhas de CI — v3.277.75-QA, 04/11/2026

**Correções comprovadas restritas à suíte de testes (jogo inalterado):**
1. O teste legado de scroll acessava `qa._CIDADE[scene]` apesar de o atlas SDL-RLE legítimo não criar cache: corrigido na cópia `tests/test_qa_pipeline_scroll_v327775.py` usando o acesso seguro `.get(scene,{})`. Igualdade byte RGBA e exigência de fallback continuam válidas.
2. O teste GLES importava a Cidade v3124, anterior ao bootstrap de metadados v759. Criada a cópia `tests/test_qa_gles_real_v327775.py` com `CityPilotScene` final v3125 e comando de execução pelo bootstrap QA real; nenhum shader, backend ou sprite foi alterado.
3. O teste antigo de limpeza do scroll exigia uma entrada persistente mesmo para atlas RLE recusado por segurança. Criada `tests/test_qa_hotpath_scroll_v327775.py` com textura técnica SRCALPHA **não-RLE** compatível, comparação RGBA contra `_render_chunk` original e verificação do descarte por bioma inativo. O renderer real continua recusando atlas RLE.

**Gates realmente executados após as correções:**
- [CI offline #41882454813](https://github.com/MrPoopBR/pixel_rush/actions/runs/41882454813): **123/123 testes pygame-ce 2.5.8 aprovados**, 32 grupos, AST/preflight SHA e proteção da versão, scroll, memória, clima, Cidade/Neve, câmera, tutorial e replay.
- [GPU Mesa #41882454845](https://github.com/MrPoopBR/pixel_rush/actions/runs/41882454845): **720** cenários GLES2/3 RGB/RGBA byte-exatos, **288** casos das cenas Cidade/Neve byte-exatos e **6** cenários PBO GLES3 byte-exatos, com **3 uploads e 3 quadros iguais sem reupload**; GPU usada nos testes é **Mesa llvmpipe no Ubuntu**, não Mali do Galaxy A54.
- [APK ARM64 #41876923149](https://github.com/MrPoopBR/pixel_rush/actions/runs/41876923149): **sucesso** na compilação e auditoria, com SHA-256 **`aca53e7c2efac6f608981b713ac1bef82fd19e7edcfebc28f1eea220451d3fc1`**. Metadados `com.bigheadmobile_pixelrush`, `versionCode=327775`, `versionName=3.277.75`, `minSdk=26`, `targetSdk=36`, ABI `arm64-v8a`, Python 3.12, pygame-ce 2.5.8, NumPy 2.3.0.
- Inspeção direta dos ZIPs publicados: 58.222.948 bytes de APK, ZIP integro, 17 entradas `.so` externas das quais 16 são ELF com **55 segmentos PT_LOAD alinhados a 16 KiB**, e `libpybundle.so` é arquivo de suporte **gzip/tar com 114 extensões nativas**; total **130 bibliotecas nativas**, compatível com o relatório. As `.so` externas estão comprimidas no APK e o **manifesto confirma `extractNativeLibs=true`**, portanto serão extraídas; `ZIP_STORED` se refere ao pacote da stdlib Python, não a essas entradas externas. 56 módulos stdlib com DT_NEEDED verificados no gate; ZIP align auditado no workflow. APK debug possui bloco de assinatura, mas **a compatibilidade da assinatura com a instalação existente do usuário NÃO foi comprovada**.
- O APK foi compilado no commit `a761d2e` e as correções posteriores afetam somente `tests/` e `.github/workflows/`; **código executável, arquivos de saves, `main.py`, DEV, recursos, física, jogabilidade, câmera e AAB não foram modificados**. Não é necessário recompilar APK para mudanças em testes de CI.

**Pendências não eliminadas:** faltam testes físicos no Galaxy A54 (Mali, entrada/HUD, FPS/p95, quinto quadro, RSS, NEON, driver, PBO, Perfetto), e comparação de assinatura do pacote instalado antes de `adb install -r`. Nunca desinstalar ou limpar dados para contornar falha de assinatura. **Placar preservado: 22/32 concluídas offline, 10/32 parciais, nenhuma homologada integralmente no hardware A54.**
