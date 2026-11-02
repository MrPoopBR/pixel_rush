# PIXEL RUSH — v3.277.32-QA (experimental)

Branch isolada: `qa/android-performance-full-v3.277.32`.
Base: `qa/android-profiling-extremo-v3.277.31`.
**Sem homologação de FPS ou APK ARM64. Não publicar como versão de produção.**

## Motivo e perfil Android real (v3.277.30)
JSON/CSV enviados do Android, 2.400 frames. Corrida normal: 665 frames,
~4,8 FPS, p95 de trabalho 495,897 ms. Replay: ~26,28 FPS.
p95 de câmera smoothscale 187,89 ms (332 chamadas), profundidade do fundo
143,975 ms (136 chamadas), mundo 2.5D 95,243 ms (136 chamadas);
simulação p95 6,03 ms; física jogador p95 0,15 ms.
Memória RSS máxima observada: 474,36 MB. Submedidas são inclusivas e
não devem ser somadas. GPU REAL NÃO MEDIDA.

## Mudanças efetivamente aplicadas nesta versão

1. `pixelrush_world_v3130.py`: espelhamentos de props cacheados por
   identidade do sprite, com invalidação e limite de 64 itens.
2. `pixelrush_profissional_v3108.py` e `pixelrush_world_v3130.py`:
   deformação FABRIK pode reutilizar Surface por rig; preenchimento
   transparente em cada chamada e limite de oito buffers.
3. `pixelrush_world_v3130.py`: transições com alfa no objeto original
   seguido da restauração em `finally`, sem cópia completa a cada frame.
4. `pixelrush_fase_b_visuais_v3272.py`: três sinais fixos de laser
   pré-renderizados com cache LRU.
5. `pixelrush_fase_b_visuais_v3274.py`: números do laser têm fontes e
   glifos renderizados uma vez, sem criar `pygame.font.Font` por chamada.
6. `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py` **somente no branch QA**:
   cache LRU de 64 redimensionamentos de textos de botões, sem mudar
   tamanho, fonte ou idioma.
7. Telemetria QA: `pixelrush_qa_android_v327728.py` registra o backend
   smoothscale, o driver SDL e mede `menus_fundo` separadamente.
   `pixelrush_qa_ultraleve_v327730.py` contém apenas essa sonda adicional.
8. Identificador QA, Buildozer, versionCode, arquivos novos de relatório,
   preflight e workflow APENAS APK debug ARM64 atualizados.
9. `tests/test_qa_performance_full_v327732.py`: regressão de
   equivalência RGBA/RGB de FABRIK, transição, ícones, rótulos e invariantes.
   Continuam os testes anteriores da branch QA v327731/v327730.

**Tentativa descartada:** outra cache de vinheta noturna de
`pixelrush_city2_v3118.py` foi revertida após confirmar que
`pixelrush_city2_v3124.py` já mantém `_night_veils` em cache.
Não foi contada como otimização nova.

## Inventário das 32 frentes solicitadas

| # | Frente | Estado na v3.277.32-QA |
|---|---|---|
| 1 | Zoom de câmera na GPU | PENDENTE: risco de diferença de pixels e contexto SDL |
| 2 | Compositor 2.5D persistente GPU | PENDENTE: reconstrução estrutural |
| 3 | Renderização CPU/GPU híbrida | PENDENTE: ModernGL atual faz readback CPU |
| 4 | Fundir zoom e pós-processamento | PENDENTE: equivalência geométrica |
| 5 | Rolagem incremental | PENDENTE: invalidar camadas sem alterar parallax |
| 6 | Blit apenas de alfa visível | JÁ EXISTE na QA v3.277.31 |
| 7 | Remover alocações grandes por frame | PARCIALMENTE IMPLEMENTADO: FABRIK/transições |
| 8 | SIMD do smoothscale | DIAGNÓSTICO incluído; NÃO alterado sem equivalência |
| 9 | Pré-composição de texturas fixas | PARCIALMENTE IMPLEMENTADO: avisos laser |
| 10 | Evitar cópias e passes duplicados | PARCIALMENTE IMPLEMENTADO: transições |
| 11 | Cache de menus por regiões | JÁ EXISTE fundo; textos escalados otimizados |
| 12 | Escolha de backend por aparelho | DIAGNÓSTICO incluído; comutação pendente |
| 13 | Cache de sprites espelhados | IMPLEMENTADO em props do mundo |
| 14 | Cache de alfa/efeitos de brilho | PARCIAL: cópias de transição removidas |
| 15 | Buffers de deformação do vento | IMPLEMENTADO por rig FABRIK |
| 16 | Culling de props fora de tela | JÁ EXISTIA |
| 17 | Batch de blits | PENDENTE, exige benchmark |
| 18 | Caches de gradiente céu/clima | JÁ EXISTIAM em módulos da cidade |
| 19 | Cache da vinheta noturna urbana | JÁ EXISTIA em City v3124 |
| 20 | Reuso de partículas e chuva | AUDITORIA PENDENTE |
| 21 | Cache de fontes/rótulos | PARCIALMENTE IMPLEMENTADO |
| 22 | Pré-carregar visualizações de skin/pet | AUDITORIA PENDENTE |
| 23 | Prefetch de biomas | JÁ EXISTIA via buffers_prod_v327710 |
| 24 | Deduplicação de superfícies | AUDITORIA PENDENTE |
| 25 | Limites de cache por memória | JÁ EXISTIAM; novos caches limitados |
| 26 | Reduzir pausas de GC | AUDITORIA PENDENTE; não mexer sem logs |
| 27 | Escrita de telemetria fora do frame | PENDENTE, risco de concorrência |
| 28 | Código nativo/Cython seletivo | PENDENTE, exige profiling de funções |
| 29 | Evitar uploads GPU repetidos | PENDENTE do compositor GPU |
| 30 | Escala final para tela física | AUDITORIA PENDENTE |
| 31 | Pré-aquecer atlas | JÁ EXISTIA parcialmente |
| 32 | VSync/driver, Perfetto/gfxinfo | PENDENTE de dispositivo |

**Não foram concluídas todas as 32 propostas:** foram aplicadas
otimizações restritas com equivalência visual verificável e instrumentação.
Principal gargalo da câmera de ~188 ms NÃO está resolvido.

## Testes e critérios de aprovação
- A suíte pygame de regressão v327732 foi adicionada ao workflow
  `.github/workflows/qa-apk-debug-v327732.yml` da branch QA.
- Pygame-ce 2.5.8 + SDL dummy local: 300 combinações de blit alfa
  da QA anterior foram repetidas com sucesso.
- Smoke test local adicional v327732: 185 comparações isoladas
  (18 transições, 80 mirrors, 80 deformações, 4 rótulos e 3 ícones);
  igualdade RGB/RGBA nas amostras. Estas operações simuladas NÃO
  substituem a regressão completa dos arquivos GitHub nem Android.
- Testes de regressão remotos, compileall de toda a árvore, build APK,
  ABI ARM64/DT_NEEDED/ZIP_STORED/16 KB e novo FPS no celular estão
  **PENDENTES DE COMPROVAÇÃO**. Nunca declarar gate aprovado sem log.
- Meta 30 FPS em Android fraco, 60 Hz de física preservados; depende de
  evidência real, não de extrapolar microbenchmark.

## Preservação e escopo
Não houve alteração direta nos branches main, DEV ou release.
Não houve alteração de física/colisões/spawns, saves, pets, compras,
atlas/PNGs, recursos desligados, semântica do replay ou AAB.
Toda alteração de código compartilhado foi feita APENAS na branch QA
experimental e não é uma versão de publicação.
