# Notas de versão — v3.277.1-PROD

Ramo **LIMPA publicação**, separado do desenvolvimento v3.277.0 DEV. Alterações concentradas somente nos itens pedidos.

| Item solicitado | Situação implementada |
|---|---|
| 1. Três skins | AZUL, VERDE (dino), ROSA (coelho) desbloqueáveis; restantes desativadas com faixa EM BREVE |
| 2. Quatro cenários | Cidade, futurista, nevada, deserto no sorteio |
| 3. Lasers Joyrider | Geradores de lasers de desafio desativados, código mantido |
| 4. Missões | Sorteio compatível sem QUEBRAR, POWERUPS, SLOW; desafio semanal de quatro biomas |
| 5. Letras | Card temporário de 5 segundos após coleta; piscada, partículas e círculo de celebração de palavra |
| 6. Pulo automático | Resíduos de MOUSE/FINGER da entrada ignorados no início da corrida |
| 7. Entrada | Personagem surge correndo por interpolação visual de 70 frames |
| 8. Otimização Android | Pacote sem histórico e QA, cache de fonte da abertura; renderização leve/automática já existente conservada. **Benchmark real pendente** |
| 9. Rastro | Opção removida e efeito forçado desligado |
| 10. Tutorial | Repetição segura de perigos, sem morte, final com aviso e retorno à corrida normal |
| 11. Movimento | Física base e quadros de movimento premium existentes preservados. **Sem retuning físico adicional** |
| 12. Aparência | Sprites e atlas existentes preservados. **Sem nova arte de personagens/inimigos nesta entrega** |
| 13. Perigos que avançam | Obstáculos móveis, eventos raros móveis e perseguidores bloqueados |
| 14. Dia/noite | Curva smoothstep entre fases de amanhecer/crepúsculo/noite para mudanças de cor graduais |
| 15. Economia | Skins ×8, upgrades ×6, pets ×8 e simulação de 10.000 partidas |
| 16. API | Indicador `API_ONLINE_ATIVA_PROD=False`; ranking permanece local |
| 17. Trocas de cenário | Portal futurista, neve em movimento, tempestade de areia e iluminação urbana animados |
| 18. Rotação | Sorteio dentre os outros 3, intervalo 80–140 s |
| 19. Fontes | Rótulos recalculados nos botões, sem extrapolar caixa; fallback Unicode do sistema; teste parcial de dispositivos |
| 20. Cards tutorial | Quebra de linha e tamanho adaptativo, validado em 78 capturas |
| 21. Controles | Android só gestos; PC/emulador só teclado+mouse. Simulação de Android validada |

## Testes realizados

- `compileall` nos módulos alterados e importação direta do principal.
- 113 quadros jogáveis SDL dummy, com clique no menu e tutorial iniciado.
- Loja real com faixas EM BREVE fotografada no teste integrado.
- 13 idiomas × 6 etapas = 78 capturas, sem invasão de área medida; CJK corrigidos com fontes completas nativas.
- Testes de sorteio para 4 cenários sem auto-repetição.
- Estimativa monetária com sementes fixas; sem alteração em ganhos ou probabilidade de moeda.

**Aviso**: Android/emuladores físicos e compilação APK/AAB não foram testados no ambiente atual. A revisão profunda de arte/movimentos (itens 11/12) permanece pendente, por segurança de publicação. Esta versão não deve ser confundida com a sequência de versões DEV.
