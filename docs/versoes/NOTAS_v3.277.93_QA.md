# PIXEL RUSH v3.277.93-QA — R23 integração de tutorial, biomas e jogabilidade

**Branch isolada:** `qa/r23-integracao-gameplay-tutorial-v3.277.93`. **Base testada:** v3.277.92-QA, commit `d8f97adf246bc593da3bb049bef2f3a5c31dd698`.
**Versão:** `v3.277.93-QA-ANDROID-RC`; Buildozer `3.277.93 / 327793`. **APK/AAB: não compilados.**
**Estado:** implementação em QA; homologação Galaxy A54, comparação de FPS/memória e aprovação final de jogabilidade dependem de testes reais.

## Código implementado nesta versão
- Tutorial obrigatório original de seis lições foi preservado como base, estendido por `src/pixelrush/ui/tutorial/premium_v327793.py`, sem substituir a física, sprites ou saves. Abertura de 300 ticks (~5 s a 60Hz) sem obstáculos; indicadores visuais pulsantes durante gesto congelado; quadro congelado reutilizado para evitar recriação do mundo 2.5D; reset de partículas com `kill()` no rebobinamento; quatro lições extras (combo real de moedas, quase-colisões guiadas e febre demonstrativa, baú, descanso/moedas); apenas a transição final ativa `tutorial_inicial_concluido`. Touch residual não deve avançar popup recém-aberto.
- Corrida: controle de swipe para cima iniciando pulo longo, e swipe para baixo no mesmo contato para descida; clique no painel de missões abre a pausa e progresso completo; retomada com contagem 3-2-1 de ticks fixos e SFX sintético; sons de passos; novo ritmo de spawn gradual de 1500ms até 730ms e tolerância de terceiro perigo após 2500m; baús (5,5%→2,6%) e letras mais raros.
- Mundos: sete biomas existentes entram na seleção aleatória sem repetição consecutiva; órbita de sol/lua contínua com ciclo de **180 segundos de simulação**; paleta ambiental interpolada; Cidade Nevada com asfalto azul-claro gelado e faixas de neve no tile cacheado; sete trilhas instrumentais próprias geradas uma única vez; movimentos dedicados a rato C1, pombo C2 e pinguim N1 com poses já cacheadas; inimigo pula-pula limitado à Cidade Futurista; spawn aéreo da Cidade usa pombo C2; novo Boneco de Neve N5 cria um projétil por aparição em alturas alternadas; bola usa imagem cacheada.
- Qualidade gráfica: `modo_grafico_leve()` já retornava `False` na base; a configuração continua fixada em `completo`. Não reativar perfil automático/leve.

## Já existentes e reutilizados (sem duplicação)
- Sistema de câmera cinematográfica, poses de corrida, efeitos de aterrissagem e transições de bioma.
- Diretor de padrões `SALTO`, `PASSAGEM`, `ESCOLHA`, `REFLEXO_CURTO/LONGO/BAIXO`, `DESCANSO` e `TRILHA`; combos/febre reais e gerente de saves.
- Renderizador 2.5D pesado em processamento por passes e cache R12/R17/R20; permanece em uso e ainda precisa de medições em Android.

## Ainda parcial / NÃO declarar concluído
- Reescrita de alto desempenho do mundo 2.5D preservando qualidade visual; benchmarks R23 não substituem análise no A54.
- Migração em massa de todos os módulos antigos e exclusão definitiva dos arquivos inúteis: caminho de imports e preflights ainda pinam muitos.
- Refinamento final de toda a arte, animações de corrida e câmera cinematográfica, cenários em todos os biomas e novos adversários exclusivos para cada um; nesta versão há melhorias pontuais, não revisão artística integral.
- Tutorial com todas as dez etapas aprovado *em hardware*; a fase de swipe-down em duas etapas continua ancorada no sistema legado que salta automaticamente e solicita a descida.
- Testes de justiça/alcance dos baús, letras, densidade de perigos e controles multifinger em Android real. Sem alegar zero mortes e zero bugs sem validação.

## Proteções de escopo e evidência
`main.py`, `JOGAR.py`, DEV, código dos pets e arquivos de saves, todos os assets e workflows Android/APK/AAB devem permanecer byte-idênticos à QA792. Android `buildozer.spec` altera **somente os números de versão**. CI R23 confere sintaxe, pygame-ce 2.5.8, AST, RNG/objetos, 3 minutos de paleta, RGBA estável da UI, boneco de neve, integridade de arquivos e benchmark Cidade 2.5D. Não afirmar conclusão de CI antes de verificar resultado real.
