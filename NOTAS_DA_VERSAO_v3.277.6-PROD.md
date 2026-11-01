# Notas da versão — Pixel Rush v3.277.6-PROD

**Data:** 31/10/2026. **Linha:** exclusivamente LIMPA/PROD; a v3.277.5-PROD e o DEV continuam intactos.

## Objetivo e mudanças (somente preparação gráfica)

1. Adicionado `pixelrush_atlas_prod_v32776.py`: carrega cópias exatas das camadas e superfícies dos biomas modulares originais geradas offline pela própria v3.277.5-PROD. No mundo, a construção pesada deixa de ocorrer em toda primeira renderização.
2. Adicionado `pixelrush_world_prod_v32776.py`: liga o carregador ao construtor de `pixelrush_world_v3185`, preservando **todas as chamadas originais** de acabamento e pós-processamento das versões 3.197, 3.200, 3.219, 3.220 e posteriores.
3. Adicionados **6 atlas** (`assets/atlas_prod_v32776/`): Neve, Cidade Futurista e Deserto, tanto em qualidade normal quanto em modo leve. Cidade permanece com seu mecanismo original. Atlas em RGBA, sem modificar imagens, shaders ou materiais.
4. Mantido o nevoeiro que varia por sessão na Cidade Futurista e reconstruídos os índices originais de luminárias do Deserto para preservar os mesmos efeitos.
5. SHA-256 interno para verificar os arquivos pré-gerados antes de carregar; leitura em fluxo para reduzir cópias temporárias de memória. Em instalação incompleta, o jogo usa o construtor antigo, sem remover recursos.
6. Alteradas apenas a referência ao módulo do mundo no arquivo principal, a identificação **v3.277.6-PROD**, o launcher, as instruções e este changelog.

## Resultados no Pygame (SDL dummy, sem GPU)

| Cenário | v3.277.5 (mediana de 3 visitas) | v3.277.6 (mediana de 3 visitas) | Redução |
|---|---:|---:|---:|
| Cidade | 1.6 ms | 1.8 ms | -10.2% |
| Cidade nevada | 326.9 ms | 70.8 ms | 78.3% |
| Cidade futurista | 496.7 ms | 65.6 ms | 86.8% |
| Deserto | 1039.8 ms | 72.7 ms | 93.0% |


**Jogo integrado:** ambas as versões concluíram 2.201 quadros com os mesmos quatro cenários e sem exceção. Pior intervalo entre quadros: **1269.2 ms antes → 167.7 ms depois**. Pico de RAM: **323.8 MiB → 338.6 MiB** (aumento, monitorar em Android).

**Qualidade:** 16/16 capturas de mundo iguais pixel a pixel, 72/72 testes de imagem/mapas normais e 72/72 em modo Android leve; Pygame executou o tutorial completo e houve salvamento e recarga de progresso.

## Arquivos, preservação e limitações

Todos os módulos da v3.277.5-PROD são preservados bit a bit, exceto o arquivo principal (import/versão), JOGAR.py e documentação, com dois módulos de carregamento acrescentados. Nenhuma mudança de física, hitbox, controle, IA, spawn, economia, câmera, transições, shaders, partículas ou efeitos foi solicitada ou feita. A coleta do lixo v3.277.5 continua intocada.

**Atenção:** atlas não comprimidos ocupam cerca de 104 MiB no disco após a extração; no ZIP eles são comprimidos automaticamente. Esse é um custo de armazenamento em troca de montagem visual mais rápida. Picos de cerca de dezenas de milissegundos ainda existem e dependem também dos acabamentos e efeitos originais. Não é garantia de 60 FPS em Android; não houve teste com GPU, shader ou aparelho físico. Não é APK/AAB assinado. O formato dos atlas é um snapshot interno versionado (não reutilizar com outra versão do código sem regenerar e verificar).
