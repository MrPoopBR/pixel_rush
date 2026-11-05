# PIXEL RUSH v3.277.70-QA — correção direcionada de encerramento no tutorial Android

**Branch isolada:** `qa/fechamento-32-v3.277.57`; base v3.277.69-QA. **Motivo:** evidência real MEmu R7 (2026-11-04, PID 7298, 00:40 local / 08:40 log do Android), que mostrou `PermissionError: [Errno 13] Permission denied: 'fc-list'` em `pygame.font.SysFont` ao desenhar o primeiro card do tutorial. A sequência real passa por `pixelrush_tutorial_prod_v32771._calcular_linhas` e `pixelrush_tutorial_corrida_v3277._fonte`.

## Implementado

- Exclusivamente em `pixelrush_tutorial_corrida_v3277._fonte`, a versão Android evita `pygame.font.SysFont` e, portanto, o subprocesso `fc-list`. Usa `pygame.font.Font` diretamente no arquivo de sistema `Roboto-Bold.ttf`, depois `Roboto-Regular.ttf` com negrito; se indisponíveis, fonte SDL padrão com negrito. A fonte desktop `SysFont('arial', ..., bold=True)` e os idiomas com TTF Unicode próprio permanecem originais.
- Nenhuma alteração de tutorial, câmera reversa, jogabilidade, física, colisões, progressão, UI de outros estados, saves, pets, assets, shaders, cache, flags de desempenho, `main.py`, DEV, produção ou workflow AAB.
- Versão do QA e pacote debug atualizada para v3.277.70 / Android `327770`; integração na CI offline e receita debug ARM64 isolada. Nenhum APK aprovado como homologado sem execução real.

## Evidência

- Log R7 contém traceback completo do processo Android no momento do encerramento; o buffer `crash` do sistema não contém exceção nativa e o `events` marca `app died`.
- Testes QA770: simulação exata do `PermissionError` de `fc-list`, fallback Roboto-Bold/Regular/SDL, desktop original e idioma Unicode sem alteração. Esses testes validam a correção da fonte, não FPS ou GPU.
- Estado das 32 otimizações preservado: **22/32 implementadas e testadas offline, 10/32 parciais, 0/32 homologadas no hardware real**. O gargalo de menu medido no MEmu permanece investigação separada (antes da corrida: renderizacao/UI elevada). Não atribuir a queda a OOM ou GPU neste relatório.
