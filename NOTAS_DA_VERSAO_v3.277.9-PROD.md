# Notas da versão Pixel Rush v3.277.9-PROD

**Origem:** v3.277.8-PROD aprovada. **Ramo:** edição LIMPA de publicação, isolada do DEV. **Data:** 31/10/2026.

## Mudanças implementadas

- Novo módulo `pixelrush_buffers_prod_v32779.py`, ligado ao inicializador depois da preparação original v3.277.8.
- Seis pacotes `.pbuf` pré-computados a partir dos seis atlas originais (normal/leve), com SHA-256; no jogo mantém apenas dados compactados e um conjunto limitado de superfícies convertidas.
- Preparação incremental de até uma superfície por atualização, com fração máxima antecipada de 38% dos candidatos. Conversão SDL só na thread principal; leitura/verificação em thread de I/O.
- Descarte imediato do buffer comprimido ao criar cada superfície e liberação das estruturas de preparação na ativação do bioma. O sorteio do próximo cenário não foi modificado.
- Fallback para carregador gráfico v3.277.8 se buffers auxiliares estiverem ausentes ou inválidos.
- Versão identificada como `v3.277.9-PROD` e inicializador/documentação atualizados.

## Comparações e testes

- 144/144 renderizações e mapas RGBA coincidiram byte a byte (Neve, Deserto, Cidade Futurista; normal/leve; seis mapas, quatro estados). Cidade usa renderizador original.
- Linux/Pygame-CE 2.5.8, 6.502 quadros acelerados: **396,9 MiB pico de RAM**, **46,73 ms maior intervalo**, 0 quadros ≥100 ms, sem exceções.
- Três ZIPs experimentais recém-extraídos em processos separados (1.302 quadros cada): max **57,85 / 61,11 / 48,83 ms**, RAM **355,6 / 355,0 / 355,7 MiB**, 0 quadros ≥100 ms.
- Tutorial de seis etapas, Game Over e recarga do save concluídos (1.901 quadros).
- Os testes de Linux empregam SDL dummy e descarte solicitado do cache de arquivos via `posix_fadvise`; **não equivalem a reinicialização fria de Android real**. O teto de 400 MiB vale para os testes feitos, não é uma garantia em todos os telefones.
- A própria v3.277.8 por vezes ficou abaixo de 100 ms em ZIP frio nesta rodada, mostrando variabilidade do cache de arquivos do Linux.

## Escopo preservado

Os módulos anteriores de sons, shaders, partículas, texturas, efeitos, transições, colisão, física, jogabilidade, tutorial, missões, inimigos e economia não foram modificados. Ramo DEV intocado. A build não é um APK/AAB Android.
