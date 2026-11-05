# Notas da versão — Pixel Rush v3.277.10-PROD

**Data:** 31/10/2026. **Base imutável:** v3.277.9-PROD. **Ramo:** somente alternativa de publicação PROD. O DEV não foi alterado.

## Alterações restritas à RAM

- Novo módulo `pixelrush_buffers_prod_v327710.py`: reutiliza os dados `.pbuf` da v3.277.9 **sem alterar seus bytes**, evita preparar novamente superfícies de biomas e qualidades já visitados na sessão e libera referências do último pacote mantidas pela thread de leitura.
- A cada 150 quadros apresentados, executa **coleta apenas da geração jovem** (`gc.collect(0)`) e, somente quando disponível no alocador nativo, solicita a devolução de páginas livres (`malloc_trim(0)`). A limpeza ocorre junto à apresentação do quadro, nunca durante a construção do atlas. Não executa coleta integral do GC.
- Mantém prefetch original de 38% dos quadros para a primeira visita e o fallback de carregamento gráfico da versão anterior para revisitas, **sem alterar sorteio, cadência de troca, texturas, materiais, geometria, transições, partículas ou shaders**.
- `pixelrush_buffers_prod_v32779.py` permanece **idêntico** ao arquivo da v3.277.9, preservado por compatibilidade com a serialização dos buffers. A única mudança funcional no inicializador é a referência para o novo módulo e o número da versão.
- `JOGAR.py` passa a apontar para `PixelRush_v3.277.10_PRODUCAO.py`.

## Testes controlados — Linux/Pygame-CE 2.5.8, SDL dummy, PYTHONHASHSEED=0

| Execução | Quadros | RAM máxima | Pior intervalo | Intervalos ≥100 ms |
|---|---:|---:|---:|---:|
| NOVO_MODULO_A | 6503 | 357.43 MiB | 44.70 ms | 0 |
| NOVO_MODULO_B | 6503 | 359.95 MiB | 49.11 ms | 0 |

- Comparação independente anterior v3.277.9: 494,32 e 480,29 MiB em ensaios de 6.502 quadros; mesmo tipo de roteiro acelerado, mas não medidos novamente no mesmo processo.
- Fidelidade visual: **144 de 144** renderizações e mapas técnicos RGBA idênticos ao carregador gráfico original, em qualidade normal e leve (Neve, Futurista e Deserto). Cidade mantém renderizador original.
- Tutorial: seis lições concluídas, corrida normal, Game Over e recarga de save, sem exceções. RAM: 299.63 MiB, pior intervalo 34.36 ms.
- Verificação estrutural: módulos de física, hitboxes, sons, shaders, efeitos, inimigos, regras e algoritmos existentes não foram alterados.

## Limitações e atenção Android

- A rotina `malloc_trim` não existe em todos os alocadores; quando ausente, a implementação mantém a coleta geracional e continua executando, **mas o teto de 400 MiB não foi comprovado nesse ambiente**.
- Testes com 6.502 quadros usam transições aceleradas e SDL dummy no Linux, não são medições de um dispositivo Android real. Nem essa revisão nem a anterior representam um AAB/APK assinado.
- O uso de RAM, as bibliotecas nativas, o ciclo de vida do app e o frame pacing precisam ser validados em aparelhos Android antes de publicar.

## Repetição com o ZIP definitivo extraído em duas pastas independentes

| Execução | Quadros | Pico de RSS | Pior intervalo | P99 | Frames ≥100 ms |
|---|---:|---:|---:|---:|---:|
| FINAL_ZIP_A | 6503 | 360.62 MiB | 50.95 ms | 6.71 ms | 0 |
| FINAL_ZIP_B | 6503 | 363.04 MiB | 44.53 ms | 6.77 ms | 0 |

Os ZIPs foram extraídos independentemente e executados em processos diferentes, com transições aceleradas por instrumentação externa. O cache de arquivos do kernel Linux pode continuar aquecido: não se trata de boot frio de Android.
