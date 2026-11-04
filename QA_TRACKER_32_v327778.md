# PIXEL RUSH — Tracker de fechamento v3.277.78-QA

Base: `qa/r11-passes-v3.277.76` em v3.277.77-QA; nova branch isolada `qa/fechamento-32-ui-v3.277.78`.

## Inventario real das 32 melhorias
- **22 frentes:** concluídas offline nas versões anteriores, conforme `QA_TRACKER_32_v327777.md`.
- **10 frentes:** ainda sem fechamento completo (#1 zoom GPU; #3 pipeline CPU/GPU; #5 scroll incremental; #7 alocações; #8 SIMD/NEON; #10 passes/cópias; #12 backend por dispositivo; #28 C/NEON; #29 PBO GLES3; #32 VSync/Perfetto).
- Seus protótipos, fallback, CI e instrumentação **já existem** em módulos QA; não confundir presença de código ou CI Mesa com integração validada no driver Mali/Android.
- Ainda **não há evidência R12 do A54 para declarar 32/32 homologadas**. Não depender de o usuário executar novo teste nesta etapa.

## Mudanças efetivamente integradas v3.277.78
1. Configurações enxutas: som, música, vibração, idioma e salvar/voltar; páginas de controle e acessibilidade permanecem em código por compatibilidade mas sem botão/rota visível.
2. Gráfico somente `completo` (padrão, migração de save antigo e função de modo leve). Sem seletor no menu.
3. Fundo do menu da Cidade recebe `bg_parallax.draw_chao` em todo frame após cache; a mesma superfície e textura já usadas na corrida.
4. Progresso pessoal preserva indicadores, recordes e maestria por bioma; elimina quatro botões e rotas: conquistas, base, relíquias, ranking local. Nenhuma exclusão de dados/recompensas do save.
5. Teste pygame-ce SDL dummy de desenho do piso e análise AST de navegação/UI.
6. VersionCode Android de teste: `327778`; nenhum APK compilado.

**Status nesta entrega:** alterações de menu reais, documentação atualizada. As dez frentes exigem implementação/medição específica adicional, portanto o placar de 22/32 offline não é maquiado.
