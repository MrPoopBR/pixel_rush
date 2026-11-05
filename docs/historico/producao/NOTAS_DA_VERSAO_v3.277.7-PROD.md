# Pixel Rush v3.277.7-PROD — Notas da versão

**Data:** 31/10/2026. **Linha:** exclusivamente PROD alternativa para publicação, derivada da v3.277.6-PROD.

## Alterações — somente otimização de preparação gráfica

1. Novo `pixelrush_tiles_prod_v32777.py`: reutiliza resultados de **quatro acabamentos gráficos existentes** (extrusão, identidade dos materiais, lapidação geométrica da Neve/Deserto e da Cidade Futurista) quando o tile de entrada, plano e parâmetros têm assinatura idêntica à versão original.
2. Novo `pixelrush_world_prod_v32777.py`: habilita somente o cache antes de importar o mundo original. Não muda os algoritmos dos shaders, as animações, o renderizador nem as classes de mundo preexistentes.
3. Arquivos compactos `assets/tiles_prod_v32777/*.tiles`, gerados offline pelas próprias rotinas originais, validados por SHA-256 antes da leitura. **Se o cache faltar ou não corresponder à imagem, a função original é executada.** Apenas um cache de bioma permanece residente por vez; não pre-carrega todos os cenários.
4. Alterada apenas a referência ao módulo de mundo no arquivo principal, o número da versão, a referência do launcher e esta documentação.

## Comparação Pygame — mesmo harness Linux, `SDL_VIDEODRIVER=dummy`

Mediana de **três visitas por bioma** em qualidade normal, oito quadros por visita e comandos idênticos de mundo:

| Bioma | v3.277.6 | v3.277.7 | Redução no primeiro desenho |
|---|---:|---:|---:|
| Cidade | 1.58 ms | 1.61 ms | -2.4% |
| Cidade Nevada | 59.16 ms | 27.99 ms | 52.7% |
| Cidade Futurista | 57.93 ms | 21.97 ms | 62.1% |
| Deserto | 69.07 ms | 33.04 ms | 52.2% |

- Capturas e mapas técnicos com hash de pixels idêntico: **18/18 verificações**, incluindo qualidade normal e leve.
- Pico de memória no ensaio de cenários (normal + leve no mesmo processo): **269.03 → 271.02 MiB** (+1.99 MiB).
- Teste integrado: **2201** e **2201** quadros; pior intervalo **257.59 → 227.45 ms**, P99 **8.1 → 8.0 ms**; pico RAM **341.4 → 344.7 MiB**. Ambos sem exceção.
- **Atenção metodológica:** o teste integrado força a mesma ordem de biomas mas eventos e momentos exatos da troca não são idênticos; portanto o máximo isolado não é medida causal controlada. Para o ganho por bioma, utilizar a tabela de cenas isoladas.
- Tutorial: **1901 quadros**, seis etapas, corrida normal, Game Over e save recarregado: `{'tutorial_concluido': True, 'moedas_totais': 53, 'partidas': 1, 'recorde': 175}`.

## Preservação e limites

- Sem alterações nos módulos originais de física, colisões, gameplay, spawn, efeitos, partículas, shaders, transições, movimentos ou economia: originais byte a byte iguais aos da v3.277.6.
- A **Cidade** segue com seu desenho original; apenas os outros três biomas usam o cache por conteúdo. Qualidade leve mantém as mesmas imagens e pode não apresentar ganho, já que os acabamentos pesados nela não são aplicados.
- O cache cobre materiais já preparados; tiles novos ou não previstos são processados pelo código original. Ainda pode haver picos por carregamento de atlas, áudio, interface e GPU — não são considerados eliminados.
- Testes feitos em Linux com Pygame-CE 2.5.8, sem dispositivo Android real. Ainda falta APK/AAB, validação ARM64, salvamento em armazenamento Android e execução de shaders OpenGL ES.
- **Manter ambas as pastas `assets/atlas_prod_v32776/` e `assets/tiles_prod_v32777/` no pacote.** Não utilizar esses caches com outro código-fonte.
- O ramo DEV e os ZIPs das versões PROD anteriores foram mantidos intactos.
