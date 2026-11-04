# PIXEL RUSH v3.277.74-QA — redução de alocações de escala no 2.5D (candidata)

**Base rastreável:** v3.277.73-QA commit `4ddaf3dbe0b756f165b503417722612e9f0ae13b`. 
**Branch isolada:** `qa/fechamento-parciais-v3.277.74`. **Sem APK/AAB.**

## Alterações exatas
1. `pixelrush_city2_v3118.CityPilotScene._scaled_surface`: no miss do LRU de 14 texturas 900×500 da Cidade, a rota de canais técnicos pode reutilizar a Surface expulsa em vez de alocar outra. Usa `weakref.WeakSet` para identificar **apenas outputs próprios de scale** (nunca atlas originais ou `image` RLE), `sys.getrefcount` para impedir mutação quando houver referências externas, e gates de tamanho, bits, masks, SRCALPHA, colorkey, alpha e RLE. Em qualquer formato incompatível, aloca pelo caminho original. `pygame.transform.scale` escreve pixels por substituição, sem alpha-blend acumulativo. Preserva o LRU e ordem de renderização.
2. `pixelrush_city2_v3122.CityPilotScene.__init__`: acrescentados exclusivamente WeakSet e 3 contadores QA, porque o construtor da Cidade final não chama o construtor v3118.
3. `tests/test_qa_scale_recycle_v327774.py`: método realmente herdado, snapshots RGBA (inclusive RGB oculto), referência externa/alias, rollback, modos RGB e SRCALPHA de `render_scene` da Cidade real em seis canais, comparação baseline × candidata e microbenchmark alternado.
4. Versão nominal v3.277.74-QA, `buildozer.spec` version 3.277.74/numeric 327774, tracker e workflow de CI **apenas pygame-ce offline**. Os workflows Android anteriores não incluem esta branch.

## Evidências e limites
O protótipo local pygame-ce 2.5.8 SDL dummy Python 3.13 com 36 texturas sintéticas, 160 escalas de 900×500 e LRU14 registrou 160 alocações na rota original contra 14 alocações e 146 reutilizações na candidata. Todos os buffers analisados produziram bytes RGBA idênticos e a retenção de referência externa preservou seus bytes. Tempo de microbenchmark local que **também capturava RGBA a cada passo**: 0,984 s original vs 0,631 s candidata; não é medida pura de scale nem prova de ganho na corrida. A CI com Cidade REAL deve ser consultada antes de declarar aprovação. A otimização está **OFF por padrão**, `PIXELRUSH_QA_CITY_RECYCLE_SCALE=1` é opt-in de QA.

Para #5, ensaio de blit individual versus lote não apresentou ganho robusto; não foi aplicado. #1/#3/#8/#12/#28/#29/#32 precisam hardware GPU/native/driver e permanecem parciais. #7/#10 avançaram apenas na implementação de uma rota segura, **sem fechamento de frente**. Placar ainda **22/32 concluídas offline, 10 parciais, 0 homologadas Android**.

**Preservação:** `main.py`, DEV, AAB, saves, pets, arte, tutorial, física, controles, câmera, HUD, áudio, shaders, assets e cronograma 5:1 não foram alterados. Não foram acionadas compilações APK nem AAB.
