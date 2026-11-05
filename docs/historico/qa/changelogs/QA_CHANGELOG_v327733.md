# PIXEL RUSH v3.277.33-QA — câmera e compositor de cenário

**Branch exclusiva:** `qa/android-camera-scene-v3.277.33`
**Base:** `qa/android-performance-full-v3.277.32`
**Status:** candidata de teste QA; NÃO homologada no Android.

## Diagnóstico que orientou as mudanças
Relatório real v3.277.30-QA extraído do aparelho, 2.400 quadros.
Corrida normal ~4,8 FPS (665 quadros) e replay ~26,28 FPS (415).
p95 de `camera_smoothscale` 187,89 ms em 332 amostras; p95
`mundo_2_5d` 95,243 ms em 136 amostras; p95
`mundo_composicao_interna` 28,222 ms em 136 amostras.
Essas etapas se sobrepõem; não somar percentis.
O compositor ativo para artes externas passa por
`pixelrush_cenarios_v398`, não somente `LivingWorld`.
GPU real não foi medida.

## Implementado, estritamente na branch QA

1. `pixelrush_qa_scene_v327733.py`: transforma a nuvem de
   `pixelrush_cenarios_v398.nuvem_pixel` de 16 retângulos/sprite
   em uma textura RGBA cacheada e um blit; mantém a mesma posição,
   cor, alpha, tamanho e ordem da arte. LRU de 96 entradas
   (~0,9 MB no máximo para escala 1). Sem alterar nuvens, bioma,
   lógica, física ou saves. Interface original preservada.
2. Mesmo módulo instrumenta OITO passes reais:
   `cenario_ceu`, `cenario_panorama`, `cenario_emenda`,
   `cenario_animacoes_fundo`, `cenario_animacoes_frente`,
   `cenario_reacao_noturna`, `cenario_foco_pista`,
   `cenario_acabamento`. Instrumentação exclusiva na telemetria
   QA, sem corromper a pilha do profiler legado.
3. `pixelrush_qa_camera_v327733.py`: adapta SOMENTE o
   `CameraCinematica.aplicar` experimental para sondar backends
   NEON/SSE2 disponíveis. Só escolhe backend alternativo se
   o resultado RGB/RGBA do frame real E de outro padrão independente
   for byte-a-byte idêntico E medido pelo menos 20% mais rápido.
   Ao terminar, restaura o backend original global. Caso contrário,
   mantém `pygame.transform.smoothscale` anterior. O teste é
   feito uma vez, apenas quando há zoom efetivo e quando o
   backend atual ainda não é NEON/SSE2.
4. `pixelrush_qa_render_v327729.py`: ativa esses dois módulos
   somente no entrypoint QA Android, antes de executar o jogo.
5. `pixelrush_qa_android_v327728.py`: registra tempos novos,
   status SIMD e exporta `pixelrush_qa_v327733.json` e
   `pixelrush_qa_frames_v327733.csv`, preservando coletas anteriores.
6. Atualização exclusiva de VERSAO para
   `v3.277.33-QA-ANDROID-RC`, Buildozer 3.277.33,
   numeric_version 327733 e testes anteriores de invariantes.
7. `tests/test_qa_camera_scene_v327733.py`: testes de pixels
   dos sete biomas, nuvens RGB e RGBA, zoom por 42 quadros,
   backend restaurado, física/versão/branch.
   Novo preflight e workflow debug ARM64
   `.github/workflows/qa-apk-debug-v327733.yml`;
   release e AAB não são executados.

## Evidências offline da decisão

- pygame-ce 2.5.8 Linux SDL dummy: composição idêntica nos
  450 blits de nuvem comparados, 50 cenas RGB/RGBA.
- Microbenchmark local de desenho das nuvens: aproximadamente
  98–109 ms (retângulos) vs 4,4–4,6 ms (cache/blit)
  para 2.400 chamadas. Isso é custo da operação isolada,
  NÃO equivale a ganho de FPS nem reproduz o hardware Android.
- Alternativa NumPy de ROI para zoom: descartada; cerca de
  30 ms contra 0,66 ms do `smoothscale` SSE2 no Linux e
  diferenças RGB de até 3 por componente.
- SDL2 Renderer separado com readback: descartado; diferenças
  grandes de pixels e sem vantagem consistente.
- SIMD local: SSE2 ~0,46 ms vs GENERIC ~2,43 ms
  no zoom de teste desktop; imagens SSE2/GENERIC divergiram,
  portanto NENHUMA troca forçada é aprovada.
- A câmera permanece exatamente igual quando nenhum backend
  mais rápido e byte-idêntico está disponível.

## Gatilhos pendentes de homologação

[ ] Executar suíte real no GitHub Actions e inspecionar logs.
[ ] Validar compilação APK ARM64/DT_NEEDED/NumPy/pygame-ce/16 KB.
[ ] Coletar nova telemetria v327733 no mesmo Android.
[ ] Comparar corrida/replay/tutorial/menus e p95/p99, RAM e picos.
[ ] Só aprovar caminho GPU completo após prova visual e
    desempenho em aparelhos físicos e emuladores.

Esta versão **não reconstrói completamente o zoom via GPU**.
ModernGL existente requer OpenGL desktop 3.3, múltiplos uploads
e leitura de volta da GPU; ativá-lo no Android sem uma migração
testada pode piorar o desempenho e a compatibilidade. A branch
preserva esse código existente e não muda o modo padrão.

**Preservado:** branches main, DEV e produção, physics 60 Hz,
colisões, spawns, moedas, pets, saves, compras, FX, recursos
desativados, atlas/PNGs, UI, shaders, replay e workflow AAB.
Nenhuma alegação de FPS homologado nesta v3.277.33.
