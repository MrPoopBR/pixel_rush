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
