# PIXEL RUSH v3.277.31-QA — otimização experimental de profundidade

**Base:** qa/android-ultraleve-v3.277.30
**Isolamento:** qa/android-profiling-extremo-v3.277.31
**Estado:** otimização pontual aplicada; sem homologação Android e sem APK v3.277.31 confirmado.

## Evidência real do Android (v3.277.30)
Relatório: pixelrush_qa_v327730.json; 2.400 quadros, 665 de corrida normal.
* Corrida normal: 4,80 FPS estimados; trabalho p95 495,90 ms; 412/665 quadros >100 ms.
* Replay: 26,28 FPS; trabalho p95 36,84 ms.
* Camera smoothscale: 332 amostras de corrida, p95 187,89 ms.
* Profundidade de fundo: 136 amostras, p95 143,97 ms.
* Mundo 2.5D: 136 amostras, p95 95,24 ms.
* Simulação: p95 6,03 ms; fisica do jogador: p95 0,15 ms.
* Memória RSS máxima observada: 474,36 MB.
As submedidas se sobrepõem às fases de renderização; nunca somá-las.
A medição GPU real não está disponível nessa coleta.

## Modificações
1. Novo módulo isolado `pixelrush_qa_alpha_blit_v327731.py`.
   Recorta apenas os limites de alfa não zero de texturas cacheadas das
   camadas de profundidade v3272, v3273, v3275 e v3276; conserva v3274.
   Mesmas posições, texturas, cores e ordem. Sem RLE (que introduziu
   divergências de arredondamento RGB nos testes locais).
2. `pixelrush_qa_render_v327729.py`: ativa a otimização pelo compositor
   exclusivo do QA Android antes de iniciar o jogo.
3. Atualização de **apenas uma string de identificação** na cópia QA de
   `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py`: v3.277.31-QA-ANDROID-RC.
4. `pixelrush_qa_android_v327728.py`: nomes novos de exportação
   `pixelrush_qa_v327731.json` e `pixelrush_qa_frames_v327731.csv`
   para não sobrescrever relatórios da versão anterior.
5. Teste `tests/test_qa_alpha_blit_v327731.py`: referência visual
   pixel a pixel entre a cadeia original e a cadeia QA em sete biomas.

## Testes executados
* `python -m py_compile`: passou no novo módulo.
* pygame-ce 2.5.8 + SDL dummy local: 300 casos de equivalência de
  pixels (fixtures), passaram; nenhum byte RGB divergente.
* Microbenchmark isolado: 3.000 blits de textura esparsa,
  79,6 ms base contra 56,6 ms recortado, ~1,41x nesse *blit*.
  Hardware Linux; NÃO equivale à medição de FPS no Android.
* Teste de regressão de fontes reais está versionado no GitHub;
  execução GitHub Actions e APK v3.277.31 ainda não comprovados.

## Fora do escopo / preservação
Nenhuma física, colisão, dificuldade, HUD, compras, saves, pets, áudio,
resolução, shaders, funcionalidades ou fluxo AAB foi alterado.
Nenhuma modificação foi aplicada aos branches main e DEV.
**Pendente:** profiling Android da v3.277.31, benchmark em aparelho,
diagnóstico de aceleração por GPU para camera_smoothscale.
