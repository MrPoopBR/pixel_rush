# Pixel Rush v3.277.10-PROD — Edição LIMPA para publicação

Esta é uma **ramificação alternativa** de `PixelRush_v3.277.0_LIMPA.py`, destinada somente à publicação. Não é a sucessora da linha de desenvolvimento futura, e **a v3.277.0 DEV original não foi alterada**.

## Rodar no PyCharm

Abra esta pasta como projeto, selecione **Python 3.13+**, instale `requirements.txt` (Pygame-CE e NumPy, que já era utilizado pelos inimigos) e execute `JOGAR.py`. No Linux também há `JOGAR_LINUX.sh` e, no Windows, `JOGAR_WINDOWS.bat`. A versão tem 13 idiomas e usa recursos originais incluídos na pasta. O renderizador OpenGL é opcional; instale `requirements_gpu_opcional.txt` apenas quando necessário.

## Restrições importantes da edição

- **Skins**: padrão `AZUL`, dinossauro `VERDE`, coelho `ROSA` ativas. Demais skins aparecem com a faixa “EM BREVE” e não podem ser equipadas nem compradas. Compras previamente salvas de skins futuras permanecem no save, mas a skin ativa retorna para a padrão nesta edição.
- **Cenários**: somente Cidade, Cidade Futurista, Cidade Nevada e Deserto. Rotação aleatória, sem sorteio do cenário atual, a cada 80–140 s aproximadamente.
- **Mecânicas temporariamente suspensas**: lasers com desafio de reflexo estilo Jetpack Joyrider, obstáculos móveis direcionados ao jogador e perseguições de captura. A ação desses sistemas foi bloqueada, preservando o código para o ramo DEV.
- **Missões**: desafios semanais limitados aos 4 cenários e missões por corrida que dependiam de recursos suspensos filtradas; eventos diários continuam válidos.
- **Interface**: card de letras oculto fora das coletas, aparece por 300 frames (~5 segundos a 60 FPS), pisca, partículas de coleta e celebração de palavra. Rastro de personagem desativado e opção removida das configurações.
- **Primeira partida**: tutorial obrigatoriamente no cenário real Cidade, obstáculos reais da Cidade, seis lições, sem morte, com repetição de desafio quando a ação iniciada não protege o personagem; mensagem de conclusão e início da corrida normal. Controle exibe teclado/mouse no PC e gestos no Android.
- **Visual**: entrada correndo, efeitos de passagem para cada um dos quatro cenários, transições do céu dia/noite suavizadas.
- **Economia**: skins adquiríveis ×8, upgrades ×6, pets compráveis ×8; recompensas preservadas.
- **Fontes**: botões ajustados ao espaço; para CJK e Hindi o jogo prioriza fontes nativas completas do sistema (Windows/Linux/Android) quando presentes, com fallback às fontes já existentes no jogo.

## Refinamento visual v3.277.2-PROD (itens 11 e 12)

O novo módulo `pixelrush_polimento_atores_prod_v32772.py` ajusta somente valores RGB de pixels já opacos: relevo e iluminação em cada pose das skins `AZUL`, `VERDE` e `ROSA`, e acompanhamento dos quadros dos 15 inimigos animados de todos os biomas já existentes. Mantém o alpha, os estados, a duração dos quadros, os atlas originais, o cache, a física, as posições, as hitboxes e as colisões. Não adiciona loops por frame nem dependências externas: usa NumPy que o código de inimigos já utilizava. As skins bloqueadas continuam intactas.

## Validação e limitações

- Testado com Pygame-CE 2.5.8 em modo SDL sem interface física. Teste de execução: menu, iniciar partida, mundo real e tutorial, 113 quadros sem exceção.
- Auditoria do tutorial: **78 telas (seis etapas × treze idiomas)**, com texto dentro das áreas disponíveis. Teste de seleção de controle de toque Android por simulação de plataforma.
- O pacote foi reduzido retirando versões históricas, relatórios e imagens antigas de QA, **sem retirar efeitos ou shaders da implementação**. Não é uma medição de FPS real em Android; recomenda-se teste adicional em aparelhos reais antes do envio.
- **Os itens 11 e 12 receberam refinamento visual dos 3 personagens ativos e dos 15 inimigos animados**, com sombras internas, volume de materiais e reflexos por pose, pré-computados na entrada dos atlas. A animação mantém os quadros, a frequência, a física e as hitboxes existentes; não houve remodelagem anatômica, nem alterações de movimento físico.
- A opção “API desativada” está documentada com sinalizador falso; o módulo principal entregue trabalha com ranking local e nenhuma integração HTTP foi encontrada nele. A configuração da API de publicação externa, caso exista, deve ser conferida no painel de distribuição.
- Fontes CJK incompletas no dispositivo que não disponha de fontes Unicode do sistema ainda podem apresentar glifos ausentes. A validação de 13 idiomas ocorreu no Linux com fontes Noto do sistema.
- **Esta entrega é um código-fonte Pygame para publicação**, não é APK/AAB assinado. Antes de publicar, compile em seu empacotador Android, teste toque/resolução/memória/FPS e assine o AAB/APK.

## Simulação de economia (hipotética)

A simulação reprodutível de 10.000 partidas experientes — duração média modelada de 4 min, 0,42–0,58 conjuntos de moedas/s, 2–7 moedas/conjunto, eficiência de coleta 57–83% e bônus simples — produziu **~555 moedas por partida** (mediana 552, faixa central P10–P90 382–732). Isto **não é telemetria real**. Sem gastar nada, o modelo requer aprox. **43 corridas para o dinossauro** (24.000), **86 para o coelho** (48.000), **19 para o primeiro ímã** (10.800). Detalhes: `SIMULACAO_ECONOMICA_v3.277.1-PROD.json`.

## Integridade do ramo

Só o arquivo principal da LIMPA foi usado como ponto de partida, com módulos extras de apresentação e configuração exclusivas de produção. Nenhum arquivo `PixelRush_v3.277.0_DEV.py` está neste pacote. Mecânicas e física do corredor fora das funcionalidades explicitamente solicitadas permaneceram como no original.

## Notas de manutenção

Consulte `NOTAS_DA_VERSAO_v3.277.2-PROD.md` para as mudanças exatas dos itens 11/12. O histórico da v3.277.1-PROD segue no pacote como referência. A v3.277.1-PROD e o ramo de desenvolvimento não foram alterados.

## Correções de bloqueio da v3.277.3-PROD

O roteiro das seis lições foi testado por teclado e gestos Android **simulados**. Os obstáculos *didáticos* do cone e do cone + hidrante tiveram a cadência ajustada para que o pulo correto não cause repetição injusta; física/hitboxes do personagem não mudaram. O aviso da tentativa errada foi localizado para os 13 idiomas, as descrições da ação mostram só os controles da plataforma e a mensagem “Tutorial concluído!” não falha por fonte nula. Eventos de suspender/retomar Android passam à rotina de pausa e save mesmo durante o tutorial. Leia `NOTAS_DA_VERSAO_v3.277.3-PROD.md`.

**Distribuição Android:** ainda é código-fonte; não é APK/AAB assinado e necessita build e testes Android físicos antes da loja.

## Gerenciamento de memória — v3.277.4-PROD

O módulo `pixelrush_world_prod_v32774.py` conserva o renderizador completo, mas faz coleta de objetos exclusivamente quando um cenário modular é removido da memória e quando retorna à Cidade. Isso elimina referências cíclicas dos callbacks dos caches de geometria e libera superfícies SDL que não são mais usadas. **Não são removidos shaders, partículas, efeitos, atlas, recursos nem detalhes de cenário.** A rotina não altera algoritmos, períodos de cenários, física, hitboxes ou RNG. O custo de uma coleta ocasional pode ocorrer durante as transições; execute teste adicional em Android físico.

Relatório de comparação e diagnóstico acompanha a entrega separada da versão.

## Gerenciamento de memória sem pausas de GC — v3.277.5-PROD

O novo módulo ativo `pixelrush_world_prod_v32775.py` libera as referências cíclicas de cenários modulares **somente depois que eles deixam de ser usados**. Substitui as coletas integrais síncronas da revisão anterior sem desligar o coletor automático do Python. A cadeia de desenho original, a física, as hitboxes, os efeitos, os shaders e a imagem das transições permanecem intactos. O módulo `pixelrush_world_prod_v32774.py` é apenas histórico e não é carregado pela versão atual. Consulte `NOTAS_DA_VERSAO_v3.277.5-PROD.md`. É necessário testar em aparelhos Android reais antes da publicação.

## Preparação gráfica rápida — v3.277.6-PROD

Esta revisão usa atlas gráficos originais pré-preparados para Neve, Cidade Futurista e Deserto, em duas qualidades, evitando reconstruí-los a cada visita. O arquivo `pixelrush_world_prod_v32776.py` preserva os acabamentos existentes; `pixelrush_atlas_prod_v32776.py` verifica a integridade e restaura os mesmos pixels e o nevoeiro da sessão. A Cidade permanece no sistema anterior. **Não mover nem excluir a pasta `assets/atlas_prod_v32776`.** Os recursos somam aproximadamente 104 MiB descompactados. Leia `NOTAS_DA_VERSAO_v3.277.6-PROD.md` para os números da comparação, limites de Android e alterações exatas.


## Refinamento de carregamento dos acabamentos — v3.277.7-PROD

`pixelrush_tiles_prod_v32777.py` verifica e reutiliza sprites de acabamento já produzidos pelas funções originais, evitando processamento pesado na primeira renderização quando os dados correspondem. Mantém todos os efeitos e shaders e possui fallback para o código original. Não excluir `assets/tiles_prod_v32777`. Veja `NOTAS_DA_VERSAO_v3.277.7-PROD.md`.

## Preparação de recursos v3.277.8-PROD

Os sons ambientes e marcos cinematográficos mantêm os bytes/quadros originais, agora carregados de recursos preparados. A leitura e verificação dos atlas ocorre antecipadamente em uma thread de I/O, **sem criação de superfícies SDL fora do thread principal**. A versão anterior continua disponível separadamente. Ver `NOTAS_DA_VERSAO_v3.277.8-PROD.md`.

## Preparação de recursos v3.277.8-PROD

Os sons ambientes e marcos cinematográficos mantêm os bytes/quadros originais, agora carregados de recursos preparados. A leitura e verificação dos atlas ocorre antecipadamente em uma thread de I/O, **sem criação de superfícies SDL fora do thread principal**. A versão anterior continua disponível separadamente. Ver `NOTAS_DA_VERSAO_v3.277.8-PROD.md`.

## Preparação de recursos v3.277.8-PROD

Os sons ambientes e marcos cinematográficos mantêm os bytes/quadros originais, agora carregados de recursos preparados. A leitura e verificação dos atlas ocorre antecipadamente em uma thread de I/O, **sem criação de superfícies SDL fora do thread principal**. A versão anterior continua disponível separadamente. Ver `NOTAS_DA_VERSAO_v3.277.8-PROD.md`.


## v3.277.9-PROD: buffers incrementais compactos (31/10/2026)

Camada nova `pixelrush_buffers_prod_v32779.py` e seis buffers `.pbuf` pré-gerados dos atlas **originais**, para preparar gradualmente 38% das superfícies candidatas na thread principal e conservar as demais como dados compactados. Uma thread de I/O faz apenas leitura e SHA-256, sem SDL. O próximo bioma continua sorteado no instante original. Buffers temporários são descartados assim que ativados, sem reter quatro cenas residentes. Falhas nos buffers preparados usam o carregador da v3.277.8. Nenhuma alteração nos atlas, shaders, som, transições, física, hitboxes ou regras de jogo.

**Testes Linux / Pygame-CE 2.5.8:** 144/144 comparações de pixel/mapas idênticas nos modos normal e leve; teste de 6.502 quadros com pico de 396,9 MiB e 46,7 ms no pior intervalo; 3 extrações independentes do ZIP experimental com máximos de 57,85 / 61,11 / 48,83 ms e picos de RAM 355,6 / 355,0 / 355,7 MiB. Esses testes não simulam um boot totalmente frio nem substituem ensaios em Android real. Não é APK/AAB.

Consulte `NOTAS_DA_VERSAO_v3.277.9-PROD.md` e o relatório de QA entregue separadamente.


## Correção de RAM v3.277.10-PROD

A versão mantém todos os recursos da v3.277.9, mas evita pré-preparo repetido de cenas e realiza limpeza leve de memória após os quadros. Consulte `NOTAS_DA_VERSAO_v3.277.10-PROD.md`. Validação de RAM e fluidez aprovada apenas em Linux/Pygame; Android real permanece pendente.


## Candidata Android v3.277.11-PROD-ANDROID-RC
Nao homologada, nao contem AAB/APK. Consulte `CHECKLIST_ANDROID.md` e suas notas especificas.
