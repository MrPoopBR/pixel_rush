# PIXEL RUSH v3.277.90-QA — organização R20, mundo/QA e motor

**Base:** QA789 commit `c968515568f02375565fe132ba35c1987bd88df2`.
**Branch:** `qa/r20-organizacao-qa-motor-v3.277.90`.
**Escopo:** organização/refatoração conservadora. Sem APK/AAB.

## Primeira opção — organização de QA/raiz
- Movidos oito arquivos antigos de apresentação e protótipos de tutorial
  das variantes 3264,3270,3271,3272 para `archive/prototipos_tutorial/`,
  sem mudanças de conteúdo. Redução física da raiz: **8 arquivos Python**.
- A variante 3273 usada pelo motor foi preservada byte a byte.
- Movidos oito módulos de suporte ativo (HUD3131/3133, textos e i18n de
  tutorial, tutorial corrida 3275, controles, desafios e skins) para
  `src/pixelrush/`. Seus nomes antigos continuam como adaptadores.
- **47 de 50 módulos QA na raiz** são citados pelos preflights históricos
  (vários com SHA fixado); não foram alterados. Os outros três são aliases
  Cidade QA785/786/787 migrados na QA788. Inventário:
  `docs/arquitetura/INVENTARIO_QA_v327790.md`.

## Segunda opção — extração inicial do motor
Dez funções independentes foram copiadas **literalmente** para seis
módulos canônicos:
- Jogador: `_estado_skin_jogador`, `jogador_invencivel_por_velocidade`,
  `raridade_de_skin`, `nivel_visual_skin`.
- Inimigos: `hitbox_disparo_laser`.
- Sistemas: `chave_periodo_semanal`, `gerar_missoes_rodada`.
- Mundo: `_suavizar_intervalo`.
- Renderização/cores: `saturar_cor`, `misturar_cores`.

O código de cada função permanece byte a byte equivalente à QA789.
O arquivo motor passa a importar a função exatamente no ponto onde a
declaração original existia; **não existem wrappers no caminho por
quadro**. Os imports de `pygame`/`random` e `date` reutilizam os
mesmos módulos Python, preservando RNG, geometria e estados.

O motor de 16 mil linhas continua sendo a fonte da física, do loop,
tutorial obrigatório, obstáculos, HUD com estado e saves. Não foi
movido nenhum destes corpos complexos.

## Proteções e gates
- SHA Git igual para oito módulos migrados e oito protótipos arquivados.
- AST idêntica para as dez funções e importações nas posições originais.
- Testes comparativos de resultado de jogador/laser/RNG/cores.
- Pygame-ce 2.5.8: 260 buffers RGBA por perfil do mundo Cidade,
  comparando QA789 e QA790 no mesmo seed.
- Regressões QA785, QA786, QA787, viewport e testes antigos pertinentes.
- Motor e buildozer só mudaram nas partes descritas.
- main.py, JOGAR.py, assets, DEV, p4a-recipes, AAB, pets,
  saves, tutorial obrigatório, física, colisões e jogabilidade preservados.

**Homologação Android no A54 ainda pendente.** Esta mudança é organização,
não comprovação de melhoria de FPS. Não criar APK até solicitação explícita.
