# QA v3.277.44 — 20 frentes: auditoria de eficacia, CPU, RAM e frame spikes

Escopo real: `LivingWorld` de `pixelrush_world_v3130`; cidade `pixelrush_city2_v3125` → `render_scene v3124`; neve/deserto `pixelrush_biomes2_v3130` → v3128/sobrescritas v3130. FPS Android nao medido nesta versao; nenhum APK/AAB compilado.

| # | Frente | Situação do código (não é garantia de ganho Android) | Risco / gate |
|---:|---|---|---|
|1|Cache temporal de fundo|Ativo Android, 4 acertos por redraw fixo de 5 frames|picos todo 5º quadro; medir separado do FPS visível|
|2|Recorte transparência|Wrapper QA ativo em Fase B|Comparar scene RGBA real e clima|
|3|Props/FABRIK|Reuso de prop espelhado/deformado|estudar temporários e hit-rate|
|4|Skins/ícones/labels|Caches antigos preservados|medir RAM sem remover funcionalidades|
|5|Depth blits agrupados|Ativo nas camadas Fase B|verificar condições de chuva/noite|
|6|SDF blit batch|Ativo sob dano cenográfico|medir somente quando SDF existe|
|7|Compositor 2.5D|Reuso de Surface e eliminação de fill duplicado|custo real de City v3125, snow/desert v3130|
|8|Batch biomas modulares|Antes testado v3126, mas runtime usa v3128/3130|novo opt-in com paridade por mapa, OFF|
|9|Culling cidade|Herdado do renderizador v3118|testar sprite no caminho real v3125|
|10|Clima pool/culling|Método LivingWorld._weather não usado por Cidade/Neve/Deserto|não atribuir melhora nesses biomas|
|11|Nuvens cidade|Reversão CPU aplicada no método legado _draw_sky da v3118|cidade atual usa outro céu, sem mudanças|
|12|Véu noturno|Cache de até 13 níveis no render v3124|memória limitada, medir RSS antes de mudar|
|13|Memória RSS|Protege união de biomas; agora preserva _scaled ativo da cidade|limpeza ainda síncrona cada 180 flips; cronometrar|
|14|Telemetria|Snapshot parcelado, I/O no worker|cópia por frame e flush final permanecem|
|15|GC|Observa pausas|não prova redução de pausas|
|16|SDL Perfetto|Sondas CPU e ATrace opcionais|falta GPU real Android|
|17|SIMD|Teste preflight fora do frame|off por padrão, fallback original|
|18|C/NEON|Biblioteca de recorte e teste offline|sem ganho Android comprovado, fallback|
|19|Scroll persistente|Somente preflight explicito|off por padrão, preserva pixels|
|20|GLES PBO|Implementação experimental não ligada|manter OFF até homologação hardware|

## Caracterização de possíveis travamentos
- **A cada 5 frames:** recomposição de mundo+profundidade contra frames que apenas reutilizam pano. É esperado haver custo assimétrico; não alterar aparência/frequência sem decisão explícita.
- **A cada 180 flips:** governança RSS em `_reclaim_inactive_caches`. Até v43, reduzia `_scaled` de cidade ativa, produzindo potencial ciclo de reconstruções. v44 protege cache ativo, cronometrando limpeza em métricas separadas.
- **A cada 600 frames:** snapshot incremental da telemetria e eventual envio a worker. As próprias cópias do QA podem ocorrer após a medição do quadro; não somar tempos inclusivos.
- **Transição de bioma:** carregamento modular (especialmente deserto) cria superfícies, mapas e atlas. Inspecionar RSS e classe de memória, sem desabilitar cenários/assets.
- **Câmera/zoom:** operação smoothscale real ainda necessária no caminho padrão, sem autotune bloqueante. Experimentos C/NEON/GLES permanecem inativos.

## Evidências exigidas
1. CI pygame 2.5.8 com classes reais, cenas `image`, `normal`, `material`, `geometry`, `fxmask`, `flow` e paridade RGBA.
2. 1200 quadros cada em cidade e neve, 240 deserto, com p50/p95/p99 por fase, cache hits vs redraws, RSS e tempo da limpeza 180-flip (se atingido).
3. Preservação das chaves e limites do cache de 5 quadros e equivalência de câmera.
4. Impossibilidade de inferir FPS do aparelho a partir do SDL dummy: somente campanha única Android posterior, mediante solicitação.
