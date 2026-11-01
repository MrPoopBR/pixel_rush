# Notas da versão — Pixel Rush v3.277.2-PROD

**Edição alternativa e isolada para publicação.** Base: `v3.277.1-PROD` (preservada). **Esta revisão modifica apenas os itens 11 e 12.** A linha `v3.277.0 DEV` permanece intacta.

## Item 11 — Animações e leitura de movimento

- Complementados os **153 quadros existentes** das três skins publicáveis (AZUL/padrão, VERDE/dinossauro e ROSA/coelho) com reflexos internos que acompanham os estados de corrida, impulso, subida, salto, queda, agachamento, swipe-down e pouso.
- Complementados os **105 quadros existentes** dos 15 inimigos animados dos biomas com detalhes luminosos por fase da animação (patas, asas, corpos e superfícies). O brilho acompanha a sequência original de cada atlas.
- Mantidos o mesmo número, a mesma ordem e a **mesma duração** dos quadros, assim como a frequência das animações, a trajetória, a velocidade, os temporizadores, os controles, a física e a detecção de colisão. Não foram criados novos movimentos nem modificada a lógica dos estados.
- O pré-processamento acontece **uma vez por atlas**, no cache existente. Não foi acrescentado processamento por frame ou novo sistema de animação.

## Item 12 — Aparência de personagens e inimigos

- Adicionadas sombras internas, realces de borda **dentro** da silhueta já existente, contraste seletivo dos materiais e pequenos reflexos pixelados no corpo e nos acessórios das 3 skins ativas.
- Adicionada variação de luz/sombra por bioma aos 15 inimigos animados para maior leitura de volume sem descaracterizar a arte aprovada.
- As superfícies mantêm **exatamente a mesma transparência pixel a pixel**, as mesmas dimensões e a mesma forma visual externa. Nenhum sprite físico, obstáculo, hitbox, projétil ou atlas de arte externa foi redesenhado.
- Skins "EM BREVE", cenários, partículas, efeitos, shaders e todas as funções publicáveis estabelecidas pela v3.277.1-PROD foram preservados.

## Arquivos alterados nesta revisão

1. `PixelRush_v3.277.2_PRODUCAO.py` — renomeação do principal, número da versão e chamada única de polimento do atlas das skins, sem mudança de lógica de jogo.
2. `pixelrush_inimigos_v3221.py` — chamada única de polimento RGB no carregamento dos quadros existentes.
3. `pixelrush_polimento_atores_prod_v32772.py` — **novo módulo exclusivamente visual**, responsável por pré-processar RGB; usa NumPy já usado pelo motor de inimigos.
4. `JOGAR.py`, `VERSAO_ATUAL.txt`, `LEIA_ME_PUBLICACAO.md` e este documento — entrada e documentação da nova revisão de publicação.
5. `requirements.txt` — explicita dependência NumPy **já utilizada pelo jogo original**, sem introduzir novo recurso ou tecnologia.

## Testes e garantias

| Teste | Resultado |
|---|---|
| Sintaxe de todos os módulos Python do pacote | Aprovado (`compileall`) |
| Comparação dos 153 quadros de personagens | **153/153** com RGB refinado; 153/153 com alfa e dimensões idênticos |
| Comparação dos 105 quadros de 15 inimigos | **105/105** com RGB refinado; 105/105 com alfa e dimensões idênticos |
| Mesma contagem e ordem dos frames/estados | Aprovado |
| Comparação do `Jogador` e `obter_hitbox()` em inicialização, pulo e agachamento | Aprovado (atributos e hitboxes idênticos) |
| Inicialização e atualização dos 15 inimigos | Aprovado (sem exceções) |
| Teste de menu e tutorial, SDL/Pygame-CE em 113 quadros | Aprovado |
| Cache de sprites: sem nova alocação de superfícies por frame | Confirmado por integração; o polimento roda no preparo de atlas |

**Limites dos testes:** a revisão melhora a leitura de animação **sem mudar a cinemática nem os frames**; portanto não cria novas poses anatômicas. A validação foi em Pygame-CE 2.5.8/Linux/SDL dummy, não em aparelho Android real, e não é um APK/AAB assinado. O teste de FPS/memória deve ser repetido em dispositivos de destino antes de publicar.

**Confirmação:** esta revisão não modifica a física, as hitboxes, os controles, as colisões, os cenários, o comportamento dos inimigos, as missões, a economia ou quaisquer funcionalidades fora dos itens 11 e 12. A v3.277.1-PROD anterior e o ramo DEV não foram alterados.
