# Pixel Rush v3.277.4-PROD — Notas da versão

## Escopo

Otimização exclusivamente do ciclo de vida de superfícies gráficas em trocas de cenário. Base: v3.277.3-PROD, em cópia independente.

## Alterações

1. Criado `pixelrush_world_prod_v32774.py`: coleta explícita de ciclos de referência após a remoção de um bioma modular do cache original.
2. Ao retornar à Cidade, descarta a referência ao cenário modular que deixou de ser usado e coleta o ciclo, pois o fotograma da transição já está preservado.
3. Arquivo de inicialização e marcador da versão atualizados para v3.277.4-PROD.
4. Nenhum cache gráfico foi desabilitado ou reduzido, nem foram alterados algoritmos de renderização, física, colisões, hitboxes, movimentos, inimigos, HUD, economia, tutorial, transições, clima ou cronômetro.

## Limitações

Somente benchmarks Pygame Linux e SDL simulado; confirmar estabilidade de RAM, taxa de quadros e travamentos de GC em Android real antes da publicação. O pacote continua sendo fonte Python, não APK/AAB.
