# PIXEL RUSH — jogo 2D em Python / pygame-ce

**Linha de desenvolvimento:** v3.277.93-QA (branch R23 isolada: tutorial, biomas e corridas).
**Base funcional:** v3.277.87-QA. Nao publicar nem compilar AAB a partir desta
branch sem novos testes de hardware. O Android real usa CPython 3.12, SDL2,
pygame-ce e Buildozer.

Novidade QA791: classes de fontes localizadas em `src/pixelrush/ui/i18n_fonts.py` e classe de partículas em `src/pixelrush/entities/particles.py`. Demais sistemas e caminhos legados mantidos.

QA792: classes Moeda, PoolManager e MonitorQualidadeVisual separadas sem mudar seus metodos; seis modulos historicos migrados byte a byte para src com aliases em raiz. Consulte docs/arquitetura/INVENTARIO_R22_v327792.md.

QA793: tutorial cinematográfico, novos perigos da neve, movimento do pombo/rato, sete biomas, dia/noite de 180s, áudio e controles integrados em QA. Confira `docs/versoes/NOTAS_v3.277.93_QA.md` e `docs/arquitetura/AUDITORIA_R23_v327793.md`. Desempenho Android real ainda não homologado.

## Entradas — nao confundir

- **Android:** `main.py` na raiz. Mantido literalmente como no QA787.
  Ele ativa a instrumentacao de QA e chama o motor atual.
- **Desktop/PyCharm:** `JOGAR.py`, sem alteração, ou `src/main.py`, que
  delega ao launcher anterior (nao cria um segundo loop).
- **Motor atual:** `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py`.
  O nome historico nao indica versao real: consulte `VERSAO_ATUAL.txt`.

## Diretorios

```text
pixel_rush/
├── src/
│   ├── main.py                       # Launcher opcional para PyCharm
│   └── pixelrush/
│       ├── game.py                   # Fachada de entrada (transicao)
│       ├── settings.py               # Apenas caminhos; nenhuma fisica duplicada
│       ├── entities/                 # Etapas futuras: player, obstaculos, pets
│       ├── world/                    # Cidade, biomas e runtime reais em migracao
│       ├── rendering/                # Efeitos, ceu e iluminacao reais migrados
│       ├── systems/                  # Etapas futuras: audio, input, saves
│       ├── ui/                       # Etapas futuras: HUD, tutorial, menus
│       ├── utils/
│       └── performance/city/
│           ├── cache_budget.py      # QA785 migrado; codigo identico
│           ├── opaque_overdraw.py   # QA786 migrado; codigo identico
│           └── technical_maps.py    # QA787 migrado; codigo identico
├── assets/                            # Recursos originais no caminho original
├── assets_android/                    # Icone e splash; Buildozer depende daqui
├── assets_i18n_v3247/                # Idiomas e fontes
├── world_art_v3106/                   # Atlas de mundo
├── world_parallax_v3112/              # Parallax
├── qa_a54/                            # QA do dispositivo Android
├── qa_native/                         # Biblioteca ARM64 de camera
├── tests/                             # Suites e regressao
├── docs/
│   ├── arquitetura/                   # Plano de migracao e limitacoes
│   └── historico/                     # Notas antigas arquivadas sem exclusao
├── .github/workflows/                 # Workflows originais preservados
├── main.py, JOGAR.py                   # Entradas antigas obrigatorias
├── PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py
├── buildozer.spec
├── requirements.txt
└── VERSAO_ATUAL.txt
```

**Esta e a primeira etapa da migracao, nao a modularizacao completa.**
Centenas de modulos da raiz ainda pertencem ao motor antigo. Os tres imports
publicos de QA785/786/787 na raiz sao adaptadores que encaminham exatamente
para os novos pacotes, preservando os nomes existentes e as variaveis globais.
Nenhum arquivo foi removido por parecer antigo.

## Instalar e executar no PyCharm

Selecione Python 3.13 no ambiente de testes ou o Python instalado no projeto.
Instale `pip install -r requirements.txt` e execute `JOGAR.py`. Opcionalmente
execute `src/main.py`, que chama o mesmo launcher. O projeto preserva
os caminhos e nao depende de copiar arquivos de imagem para `src/`.

## Relatorios historicos e rastreabilidade

As notas antigas nao utilizadas nos gates estaticamente identificados foram
realocadas para `docs/historico/`. O manifesto
`docs/historico/MANIFESTO_MOVIMENTOS_v327788.json` lista cada caminho
anterior, novo caminho e SHA Git do **mesmo conteudo**. As notas que os
preflights QA antigos precisam ainda permanecem na raiz. O README original
de publicacao Android foi guardado em
`docs/historico/README_ANDROID_AAB_ORIGINAL.md`.

Confira `docs/arquitetura/ESTRUTURA.md` e
`docs/arquitetura/PLANO_MIGRACAO.md` antes de mover novos modulos.

## Android, desempenho e seguranca

`buildozer.spec` continua com `source.dir=.` e ID do pacote
`com.bigheadmobile_pixelrush`, e os scripts existentes nao foram movidos.
Nao alterar assets, imports de Android, caminho de saves, physics, DEV
nem workflows AAB durante esta etapa. Os adaptadores sao resolvidos
uma unica vez no import e nao adicionam trabalho a cada quadro.

O ganho das otimizacoes de Cidade QA785/786/787 foi aprovado somente no
CI offline Linux; Galaxy A54 ainda requer homologacao real. Este commit
de organizacao nao deve ser interpretado como melhoria de FPS.

Arquivo historico de instrucoes AAB: `docs/historico/README_ANDROID_AAB_ORIGINAL.md`.

## Segunda etapa de organização (QA789)

Foram migrados 25 módulos de código reais, sem modificar os bytes: 15 de mundo e Cidade para src/pixelrush/world/ e 10 de efeitos e renderização para src/pixelrush/rendering/. O manifesto dos SHAs e caminhos está em docs/arquitetura/MANIFESTO_MODULOS_v327789.json. Os nomes antigos permanecem como adaptadores, para não quebrar imports ou duplicar estados.

Outros módulos e documentos da raiz são verificados por hash em preflights antigos e permaneceram em seus caminhos originais. Consulte docs/arquitetura/QA_RAIZ_PROTEGIDA_v327789.md. Os três documentos Android independentes foram organizados em docs/android/ e docs/historico/ com manifesto específico. Nenhuma funcionalidade foi removida, nenhum APK compilado e o Galaxy A54 ainda não homologou esta estrutura.

## Etapa QA790 — organização de QA e começo da divisão do motor

Foram extraídas dez funções independentes do motor para módulos em `src/pixelrush/entities/`, `src/pixelrush/systems/`, `src/pixelrush/world/` e `src/pixelrush/rendering/`, preservando o código e os imports no ponto original. Oito módulos de HUD, tutorial, controles, desafios e skins também foram migrados, mantendo adaptadores antigos. Oito arquivos históricos não ativos saíram da raiz para `archive/prototipos_tutorial/` com integridade Git comprovável.

Os demais módulos `pixelrush_qa_*.py` da raiz ainda são protegidos por scripts antigos de preflight ou por compatibilidade: consulte [inventário QA](docs/arquitetura/INVENTARIO_QA_v327790.md). A classe Jogador, inimigos completos, física e tutorial obrigatório seguem no motor original nesta etapa. Não houve reescrita desses subsistemas nem compilação Android.
