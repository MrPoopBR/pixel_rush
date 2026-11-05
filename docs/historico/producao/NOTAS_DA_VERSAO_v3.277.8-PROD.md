# PIXEL RUSH v3.277.8-PROD — NOTAS DA VERSÃO

**Data:** 31/10/2026. **Ramo:** apenas PROD LIMPA alternativa para publicação, derivado de v3.277.7-PROD.

## Escopo: exatamente os três gargalos auditados

1. **Áudio procedural na primeira visita a um bioma:** `pixelrush_preparacao_prod_v32778.py` utiliza os buffers PCM das **mesmas fórmulas originais**, pré-gerados para Cidade, Neve, Cidade Futurista e Deserto. Existem variantes para mixagem 22.050 Hz e 44.100 Hz, estéreo PCM assinado 16 bits. Os buffers são validados por SHA-256 e convertidos em `pygame.mixer.Sound` no uso; o método original é utilizado quando o mixer tem outra configuração, o arquivo está ausente ou a assinatura falha. Os canais, volumes, tempos de crossfade e música não foram alterados.
2. **Restaurar atlas durante a troca de bioma:** um worker de **somente leitura de arquivos e SHA-256** aquece o cache de arquivos e valida antecipadamente os seis atlas normais/leves. No thread principal, a desserialização de cada cena usa a validação antecipada **somente se tamanho e data de modificação permanecerem iguais**; caso contrário, usa o carregador original que verifica o SHA. O código não cria `pygame.Surface` em threads e não retém as cenas inativas na RAM. Os próprios arquivos `.atlas` e `.tiles` das versões anteriores permanecem byte a byte idênticos.
3. **Geração sob demanda de marcos cinematográficos:** pré-geradas as mesmas 4 artes monumentais e 24 lâminas de animação, com RGBA original, sem alterar os métodos de desenho, opacidades, timings e condicionais. Arquivos validados por SHA-256; fallback ao algoritmo original quando necessário.

**Integração:** o arquivo principal teve apenas a atualização do número da versão, um import e a chamada única de instalação da preparação. Novos recursos em `assets/preparacao_prod_v32778/`, com manifesto e SHA-256. Lançadores e documentação atualizados.

## Comparação com Pygame-CE 2.5.8 (Linux, SDL dummy, GPU off)

| Indicador (corrida acelerada 3.201 quadros) | v3.277.7 | v3.277.8 |
|---|---:|---:|
| Máximo entre quadros | 156,28 ms | 77,34 ms |
| P95 | 5,81 ms | 4,28 ms |
| P99 | 9,55 ms | 6,32 ms |
| Intervalos >100 ms | 3 | **0** |
| Intervalos >50 ms | 8 | 2 |
| Pico de RAM RSS | 344,6 MiB | 344,7 MiB |
| Síntese de áudio no loop (maior chamada) | 81,53 ms | **0 ms** (buffer preparado) |

A repetição da v3.277.8 com 3.201 quadros apresentou máximo **72,43 ms**, P99 **7,25 ms**, RAM **345,0 MiB** e nenhum intervalo acima de 100 ms. As duas execuções da v3.277.8 não tiveram exceções. A rotação de cenários foi acelerada APENAS no harness de QA, com sequência fixa dos quatro biomas; o código de sorteio original não mudou.

### Primeiro desenho em isolamento (qualidade normal, ms)

| Cenário | v3.277.7 | v3.277.8 |
|---|---:|---:|
| Cidade | 4,05 | 3,48 |
| Cidade Nevada | 31,88 | 22,25 |
| Cidade Futurista | 24,92 | 16,52 |
| Deserto | 39,57 | 21,69 |

A execução isolada para modo leve também foi registrada no relatório de QA. **As 56 comparações** das imagens e mapas técnicos dos quatro cenários (normal/leve) foram idênticas; **4 áudios a 44.100 Hz + 4 áudios a 22.050 Hz** apresentaram bytes idênticos, bem como **28 imagens** dos marcos e lâminas (RGBA idêntico). O fallback sem arquivos preparados manteve o áudio e as artes originais.

### Regressão funcional

- Tutorial obrigatório: **seis lições concluídas**, corrida normal, Game Over e save recarregado com `tutorial_concluido: true`, 53 moedas, uma partida e recorde de 175 m. Execução de 1.801 quadros sem exceções.
- Sintaxe Python, integridade ZIP e inicialização fora da pasta de construção: verificar em `RELATORIO_QA_2778/` e registro de empacotamento.
- A comparação de origem confirma **nenhuma alteração** nos arquivos anteriores de física, colisões, personagens, IA, spawn, sons, shaders, texturas, atlas e efeitos.

## Restrições e pendências

- Os picos **não foram eliminados completamente**: máximo 72–77 ms nos testes de estresse; existem custos residuais de renderização e preparo de cena.
- Os tempos são do Linux com Pygame e SDL dummy, **não são FPS em dispositivo Android**. A compatibilidade OpenGL ES, APK/AAB assinado, ARM64, páginas de 16 KB, armazenamento Android e desempenho real precisam de validação antes de publicar.
- Os recursos `.pcmz`, `.rgbaz` e manifesto dessa versão precisam permanecer juntos. Não reutilizá-los em outra revisão sem regenerar as assinaturas.
- Não houve mudanças no ramo DEV nem nas versões PROD anteriores.
