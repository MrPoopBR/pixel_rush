# PIXEL RUSH v3.277.72-QA — correção R9 do fechamento na conclusão das letras

**Base:** v3.277.71-QA na única branch isolada `qa/fechamento-32-v3.277.57`.

### Evidência real
O logcat R9 mostra `PermissionError: [Errno 13] Permission denied: 'fc-list'` no PID 27540 em `pixelrush_producao_fx_v32771._fonte`, chamado por `desenhar_mensagem_tutorial` ao completar o tutorial. O pacote instalado era v3.277.71 (versionCode 327771) apesar do título R9 v3.277.70. Sem indicação de OOM ou SIGSEGV.

### Alterações pontuais
1. `pixelrush_producao_fx_v32771._fonte`: preservar fontes Unicode disponíveis; Android sem fontes recebe fallback já existente de `pixelrush_tutorial_corrida_v3277._fonte`, evitando `pygame.font.SysFont`; desktop conserva Arial e cache por idioma/tamanho.
2. `pixelrush_fontes_prod_v32771._caminho_sistema`: Android não usa `pygame.font.match_font` (que também aciona `fc-list`); mantém caminho nativo Noto ou subset local.
3. Atualizar versão **3.277.72 / 327772**, preflight, testes e CI offline e somente workflow APK DEBUG QA ARM64.
4. Testar pygame-ce: exceção PermissionError idêntica R9; CJK sem fc-list, fontes Unicode existentes, desktop Arial, cache e vinculação da tela real.

**Não alterado:** física, jogabilidade, letras e bônus, HUD e texto, arte, zoom, 2.5D, menu, saves, pets, RNG, main, DEV, AAB e geração release.

**Situação das 32 melhorias:** 22/32 concluídas offline; 10 parciais; homologação ARM64 físico pendente. A lentidão no MEmu permanece separada e não é resolvida por esta correção de crash.
