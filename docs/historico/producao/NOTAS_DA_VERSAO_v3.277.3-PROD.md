# Pixel Rush — notas da v3.277.3-PROD (edição alternativa de publicação)

**Base:** v3.277.2-PROD. **Ramo DEV:** intocado. **Tipo:** correção dos bloqueios auditados + auditoria dirigida das seis lições. Esta revisão não é continuação da linha DEV.

## Alterações estritamente relacionadas à auditoria

1. **Tutorial — pulo curto e pulo longo:** o tempo de passagem dos obstáculos **exclusivos da lição** foi recalibrado. O cone didático avança 12 pixels por atualização de confirmação; a dupla cone + hidrante, 16 pixels por atualização de confirmação. Antes eram 6 pixels. Aceleração, gravidade, salto, hitboxes, posição do personagem, perigos do jogo normal e seus spawns **não foram alterados**. A lição ainda exige pulo real (pulo longo: comando segurado por pelo menos 19 atualizações); ações erradas não a concluem.
2. **Repetição segura:** preservada a regra não fatal de retroceder o desafio didático ao detectar colisão desprotegida, sem Game Over. O feedback de repetição agora está localizado nos 13 idiomas.
3. **Android — pausa e retomada:** eventos de ciclo de vida (`APP_WILLENTERBACKGROUND`, `APP_DIDENTERBACKGROUND`, `APP_WILLENTERFOREGROUND`, `APP_DIDENTERFOREGROUND` e `ACTIVEEVENT`) não são interceptados pelo tutorial. A rotina existente de pausa e save recebe esses eventos. Nenhuma alteração nas regras de salvamento fora desse encaminhamento.
4. **Instruções de controle:** os quatro comandos do tutorial apresentam dica + objetivo somente da plataforma: gestos Android ou teclado/clique no PC/emulador, nos 13 idiomas. Coletas preservaram seus textos originais. Removido o rótulo misto “TOQUE / MOUSE” do card Android; nada foi alterado no sistema de controles.
5. **Fim do tutorial:** corrigido erro de fonte nula na mensagem de conclusão em idiomas que não possuem fonte Unicode dedicada; passa a usar o fallback Pygame existente. Sem novos arquivos de fonte ou dependências.
6. **Mouse no PC/emulador:** corrigido o adaptador de coordenadas `screen_to_virtual` usado apenas pelo interceptador de eventos do tutorial; cliques e arraste do mouse deixaram de causar `TypeError` durante as lições.
7. **Versão e documentação:** identificação atualizada para `v3.277.3-PROD`, arquivo principal e inicializadores atualizados. A revisão mantém o histórico das notas anteriores.

## Testes realizados

- **Pygame-CE 2.5.8 + Python 3.13.5**, Linux x86_64, SDL vídeo/áudio *dummy*.
- **Sequência completa de seis lições por teclado e, separadamente, cliques/arraste do mouse**: pular → pular longo → agachar → swipe-down → moedas → letras, sem repetição forçada; término e save `tutorial_inicial_concluido=true` verificados.
- **Sequência completa de seis lições por eventos FINGER sintéticos** (modo Android simulado): todas concluídas; não é teste em aparelho físico.
- **Falha simulada de obstáculo didático**: contador de tentativas incrementou e obstáculo foi recolocado, com personagem vivo.
- **Evento de suspensão do aplicativo simulado** durante lição: salvamento foi chamado, o progresso congelou na pausa e retomou após CONTINUAR.
- **Texto e HUD**: 312 renderizações (13 idiomas × 6 lições × 2 modos × 2 larguras, 280 e 450 pixels), nenhum texto vazio ou estouro geométrico detectado; mensagem final verificada nos 13 idiomas.
- **Sintaxe Python e pacote ZIP**: verificação após empacotamento; execução isolada conforme relatório de QA.

## Limitações antes de publicar na Google Play

**O APK/AAB assinado e os testes em aparelho Android real continuam pendentes.** O arquivo entregue é **código-fonte Pygame**, não um aplicativo Android compilado. Esta revisão não contém `buildozer.spec`, assinatura, validação ARM64/API, páginas de memória de 16 KB, nem prova de FPS/consumo em celular. O caminho de armazenamento do save deve ser validado pelo empacotador em diretório privado gravável. **Não há liberação final da Google Play nesta etapa.**

## Garantia de escopo

Não foram alterados movimento ou física do jogador, hitboxes, IA, níveis, cenários, economia, skins, shaders, partículas, missões, APIs ou efeitos de corrida fora dos pontos de tutorial e pausa descritos. O pacote base v3.277.2-PROD e a v3.277.0 DEV permanecem inalterados no disco.
