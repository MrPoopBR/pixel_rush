# PIXEL RUSH QA 3.277.45 — Quinto quadro e memória sob pressão

## Cadeia ativa verificada no código
- O jogo `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py`, ramo Android JOGANDO, chama `cache_fundo_mobile.reusar(display_surface,chave,ativo)`. Se nao houver hit, executa `bg_parallax.draw`, `profundidade_cinematografica`, `desenhar_profundidade_bioma`, nuvens de clima e cenas épicas, depois chama `cache_fundo_mobile.guardar`. Segue com chão/sprites/HUD/câmera/apresentação a cada quadro.
- `CacheFundoUltraQA(periodo=5)`: redraw no frame local 0, 5, 10...; cache hit nos 4 intermediários, sem queda de resolução. `CacheFundoMobile.guardar` copia o fundo renderizado para uma única Surface `pygame.Surface(tamanho).convert(superficie)`; sua ocupação real depende do pitch/bitdepth do SDL (450×800×4 = 1.440.000 bytes para 32bpp; 450×800×3 = 1.080.000 bytes para 24bpp).
- `pixelrush_qa_performance_integrated_v327742.py` cronometra `display.flip` e, após o flip, executa a limpeza `_reclaim_inactive_caches` a cada 180 apresentações. A limpeza pode ocorrer no ultimo cache hit antes do próximo redraw, dependente da fase do ciclo. Para evitar ilusão de medição, o `swap_cpu_p95_ms` nao inclui limpeza, o `cache_cleanup_p95_ms` inclui somente a limpeza, e o custo medido externamente do `flip` pode incluir ambos.

## Perguntas a responder com o novo CI
1. Quais os p50/p95/p99 separadamente no frame de redraw e nos 4 hits para Cidade v3125, Neve/Deserto v3130?
2. Quanto custam especificamente `world.draw` e `cache.guardar`? Quanto o 180º flip aumenta quando o ramo de RSS é forçado, comparado com flip sem limpeza?
3. A política de um redraw/4 hits permanece pixel-exata com HUD mutável e mudança de clima/bioma?
4. Um render no buffer alternativo preserva os bytes de `LivingWorld.draw` sob mesmo formato inicial? Isso é somente requisito parcial — não valida trocar o destino no loop completo.
5. Os caches LRU ativos sobrevivem à limpeza sob RSS simulado acima do budget? Quais alocações permanecem no ciclo cidade→neve→deserto→cidade?
6. A memória RSS reportada pelo SO acompanha a ocupação de `_scaled`, `_city_surfaces` e dos mapas modulares, sem confundir memória lógica com física?

## Técnicas pixel-exatas candidatas (não implementadas no gameplay)
- **Desenho direto no buffer-base do cache, mais blit para a tela:** pode dispensar `guardar`, porém precisa comparar pilha completa de ParallaxBackground/Depth/Fase B/Climate/Epic e todas as máscaras; o custo pode apenas trocar uma cópia por outra.
- **Reuso de superfície converted RGB com formato alinhado ao display:** já existe no cache; não duplicar.
- **Batching dos blits de fundos técnicos:** já existe parcialmente, e módulos modulares estão opt-in OFF; não generalizar sem testes no caminho real.
- **Conservação de LRU quente sob RSS:** já implementada na v44, especialmente texturas da cidade ativa; investigar só sob pressão forçada, sem aumentar limite.
- **Orçamento de limpeza incremental após flip:** possível, mas mudaria agendamento e precisaria provar ausência de referêcias em uso; não implementar agora.
- **Pré-composição incremental de fundo durante os quatro hits:** alteraria o escalonamento de trabalho e possivelmente o instante visual/efeitos; requer especificação de paridade temporal por frame e deve permanecer experimental.

## Segurança e limites
NUNCA baixar qualidade, mudar frequência de frames, simplificar shaders, omitir sprites, antecipar/deslocar efeitos visuais ou mexer na física. Nenhuma inferência de FPS Android antes do teste único no dispositivo. O teste com RSS simulado cobre o fluxo condicional, não faz o sistema operacional aplicar pressão real.
