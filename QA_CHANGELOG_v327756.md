# PIXEL RUSH v3.277.56-QA — compositor SRCALPHA, CPU/RAM e scroll seguro

**Origem:** `qa/android-full-performance-v3.277.55`  
**Destino isolado:** `qa/android-full-performance-v3.277.56`  
**Versão QA:** `v3.277.56-QA-ANDROID-RC`  
**Metadados Buildozer:** `3.277.56` / `327756` — **nenhum APK/Android/AAB compilado**.

## Avanço 1: remover passagens completas de atlas técnico uniforme (código real)

`pixelrush_city2_v3118.CityPilotScene` valida, durante a construção do cenário e fora do quinto quadro, cada fonte estática técnica de `geometry`, `fxmask`, `normal`, `material` e `flow`. Quando o atlas original inteiro é 450×250 SRCALPHA 32 bits, sem colorkey, alfa global 255 e pixels de cor+alpha 255 uniformes, faz a comparação de bytes crus de todos os pixels, inclusive RGB oculto. Somente neste caso guarda o identificador da Surface e a cor RGBA exata (sem guardar uma cópia dos pixels).

O método real `_render_chunk` substitui a escala para 900×500 e o blit daquela fonte por **um único `target.fill(cor,(x,0,900,500))`**, com clipping SDL normal. Não faz scan de pixels no frame5, não cria entrada 900×500 no LRU e não muda ordem dos sprites. Fontes não uniformes, alpha parcial, image/efeitos e formatos incompatíveis permanecem no caminho anterior. A fonte original ainda está disponível para todos os demais usos. A flag `PIXELRUSH_QA_CITY_UNIFORM_TECH_FILL=0` restaura inteiramente o render anterior.

**Equivalência limitada comprovada da operação:** ensaio direcionado pygame-ce 2.5.8 com 180 blits de atlas SRCALPHA uniformes alpha255 versus fills do destino, nas posições -950...450, destinos RGB ou RGBA e vários alfas de destino (inclusive 0), manteve todos os bytes RGBA idênticos. O teste integrado do cenário real está **preparado, não executado**. Não alegar ganho FPS/RSS de dispositivo real nem melhoria confirmada no canal `image`, que é preservado.

## Avanço 2: scroll 2.5D sem custo de exceção Python no quinto quadro

A versão anterior descartava corretamente o scroll SDL-RLE, mas lançava `ValueError` para cada chunk RLE, capturando-o logo no wrapper. Em `pixelrush_qa_incremental_scene_v327750.py`, o contrato de retorno normal agora é `None` para fontes RLE ou formato inadequado. O wrapper já usa `None` para invocar `_render_chunk` original diretamente, com os mesmos pixels RGBA inclusive RGB oculto e sem cache inseguro. As estatísticas de RLE e incompatibilidade seguem disponíveis.

**Não ativa scroll na corrida por presunção:** `PIXELRUSH_QA_CITY_INCREMENTAL=0` e `PIXELRUSH_QA_CLASSIC_INCREMENTAL=0` continuam o padrão. As melhorias anteriores para cobertura da janela, fontes não RLE, saltos e buffers por instância foram preservadas. A economia de tratamento de exceção só atua no caminho experimental quando habilitado; não altera o quinto quadro da corrida normal por padrão.

## Gates novos preparados (não executados na homologação final)

- `tests/test_qa_uniform_tech_v327756.py`: compara os atlas reais de Cidade, composição `_render_chunk` no destino RGB/RGBA incluindo alpha0, seis canais do `render_scene` com clima/noite, fontes imutáveis e fallback RLE sem exceção.
- `.github/scripts/qa_benchmark_uniform_tech_v327756.py`: 96 quadros RGBA do mundo real por canal, CPU p50/p95/max e RSS; compara duas instâncias para contagem lógica de surfaces ampliadas evitadas (não considera economia de RAM do SO automaticamente).
- `.github/scripts/qa_preflight_v327756.py`: hashes exatos, sintaxe AST, versão, flags e integridade de arquivos protegidos.
- `.github/workflows/qa-offline-v327756.yml`: disparo **exclusivamente manual** `workflow_dispatch` e sem Buildozer, Gradle, ADB, APK ou AAB.

## Status / preservação

**Placar conservador: 12 de 32 anteriormente concluídas offline e 20 parciais.** Os avanços desta versão são limitados às frentes #2, #5, #7, #10, #24, #25 e #26, sem declarar novas conclusões sem os gates. A redução de blits técnicos não significa ausência de recomposição das camadas dinâmicas do quinto quadro.

O comparativo com a versão anterior deve mostrar exclusivamente módulos de renderização/scroll solicitados, arquivos QA de gates e documentação, além de três metadados de versão (`PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py` versão apenas, `VERSAO_ATUAL.txt`, `buildozer.spec` versão apenas). Preservados `main.py`, DEV, `main`, física, jogabilidade, tutorial, efeitos de clima, qualidade visual, câmera, som, sprites, HUD, pets, saves, skins, assets, política de fundo 5:1 e workflows de produção.
