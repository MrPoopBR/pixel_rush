# Pixel Rush v3.277.5-PROD — Notas da versão

**Ramo:** edição alternativa LIMPA para publicação. **Base:** v3.277.4-PROD. **Data:** 31/10/2026.

## Alteração funcional única: pausas de GC nas trocas de cenário

- Adicionado `pixelrush_world_prod_v32775.py` como gerenciador ativo do ciclo de vida de biomas.
- Quando um cenário modular deixa definitivamente o cache, suas referências internas (inclusive callbacks vinculados à própria cena) são desligadas com `cena.__dict__.clear()`. Isso rompe ciclos que anteriormente exigiam `gc.collect()` integral e permite ao contador de referências liberar as superfícies SDL do cenário aposentado imediatamente.
- No retorno à Cidade, o cache modular antigo é esvaziado e o mesmo descarte é aplicado à cena que não será reutilizada. A imagem de transição já foi capturada antes dessa operação pelo mundo original.
- A v3.277.5-PROD **não invoca `gc.collect()` nas mudanças de cenário**. A coleta automática normal do Python continua ativa, como de costume; não foi desativada.
- Ajustado exclusivamente o import no arquivo principal para o novo gerenciador e o identificador da versão. Inicializadores, leitura inicial e notas atualizados.

O antigo `pixelrush_world_prod_v32774.py` permanece no pacote apenas como artefato de histórico/compatibilidade e **não é importado pela versão ativa**.

## Testes pareados (Pygame-CE 2.5.8, Python 3.13.5, Linux, SDL vídeo/áudio dummy)

Mesma semente e roteiro externo de 4.201 quadros, com 16 mudanças de cena (o RNG coincide nos primeiros 3.666 quadros; o cenário diverge nas últimas trocas pela mudança no comportamento do GC):

| Medida | v3.277.4-PROD | v3.277.5-PROD |
|---|---:|---:|
| GC integral explícito | 13 | 0 |
| Maior evento GC durante quadros | 78,55 ms | 2,43 ms |
| Máximo no método `LivingWorld.switch()` | 71,06 ms | 1,61 ms |
| Pico RSS | 356,3 MiB | 355,3 MiB |
| P95 dos intervalos de quadros | 4,97 ms | 4,91 ms |
| P99 dos intervalos de quadros | 8,06 ms | 7,65 ms |
| Exceções | 0 | 0 |

**Teste longo na v3.277.5-PROD:** 5.801 quadros, 22 trocas registradas, 358,9 MiB de pico, 0 coletas explícitas de GC, sem exceções. Este teste não prova estabilidade por horas.

**Testes adicionais:** tutorial → corrida → Game Over → save (1.901 quadros, concluído), loop real de 421 quadros com limite de 60 FPS (sem exceções), quatro capturas em quadros equivalentes (180, 600, 2100, 3900) idênticas pixel a pixel. Versões antigas de QA e DEV não foram modificadas.

## Preservação de escopo

**Não houve mudança na física, hitboxes, colisões, movimento, inimigos, spawns, jogabilidade, HUD, shaders, partículas, efeitos, fontes, economia, missões ou assets.** O mundo original `pixelrush_world_v3232.py` e demais módulos históricos estão byte a byte idênticos à v3.277.4-PROD. Apenas o gerenciamento de objetos gráficos aposentados foi alterado.

## Limites e publicação

As medições acima são de Pygame no Linux, sem GPU e vídeo físico. A criação de cenas ainda é cara e pode gerar quadros longos não relacionados ao coletor. É obrigatório testar no Android real, principalmente celulares de 2–3 GB, alternância de app, FPS e picos de RAM. O ZIP continua sendo fonte Python para PyCharm, não APK/AAB assinado.

Os resultados completos (roteiros, logs, JSON de telemetria, gráfico, manifesto e comprovação visual) estão no pacote separado `RELATORIO_GC_PIXEL_RUSH_v3.277.5-PROD.zip`.
