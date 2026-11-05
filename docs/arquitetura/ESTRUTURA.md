# Arquitetura proposta e situacao real (QA v3.277.90)

## Estrutura modular por etapas

```text
pixel_rush/
├── main.py                   # Entrada Android SDL2 ORIGINAL (inalterada)
├── JOGAR.py                  # Launcher desktop ORIGINAL (inalterado)
├── PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py # Motor real/monolito; nao reescrito
├── buildozer.spec            # Pacote Android e identidade preservados
├── src/
│   ├── main.py               # Nova entrada desktop opcional, delega ao JOGAR.py
│   └── pixelrush/
│       ├── game.py           # Fachada, nao um segundo game loop
│       ├── settings.py       # Somente caminhos; fisica ainda no motor
│       ├── entities/         # Etapas futuras: player/enemies/pets
│       ├── world/            # Etapas futuras: biomas/chunks/camera
│       ├── rendering/        # Etapas futuras: Pygame, atlas, GLES
│       ├── systems/          # Etapas futuras: fisica, input, audio, saves
│       ├── ui/               # Etapas futuras: menus/HUD/tutorial
│       ├── utils/
│       └── performance/city/ # Migrados de verdade QA785, QA786, QA787
│           ├── cache_budget.py
│           ├── opaque_overdraw.py
│           └── technical_maps.py
├── assets/                   # Mantidos no lugar: referencias relativas atuais
├── assets_android/           # Icone, presplash; NÃO MOVER
├── assets_i18n_v3247/       # Fontes/localizacao; NÃO MOVER
├── world_art_v3106/          # Atlas mundo; NÃO MOVER
├── world_parallax_v3112/     # Parallax; NÃO MOVER
├── qa_a54/                   # Instrumentacao Android (mantida)
├── qa_native/                # Biblioteca C/NEON (mantida)
├── tests/                    # Regressao e benchmarks (mantidos)
├── docs/                     # Arquivo de versoes e auditorias antigas
└── .github/workflows/        # CI/AAB original intocado
```

## Importacoes e compatibilidade

Os tres modulos da Cidade foram copiados **byte a byte** para seu pacote
canônico. Os tres arquivos originais na raiz tornaram-se adaptadores muito
pequenos, que devolvem a mesma instancia de modulo Python por `sys.modules`.
Imports antigos, patching de testes e os estados globais QA continuam
compatíveis. O Android usa `source.dir=.` e inclui `*.py` recursivamente,
por isso `src/` deve fazer parte do bundle; somente CI offline homologado.

Não foram migrados o motor de 16 mil linhas, assets e rotinas de saves:
é preciso seguir dependências e garantir paths/Android antes de realocá-los.
As pastas vazias são apenas destinos de migrações futuras, não versões
concorrentes da lógica do jogo.

## Regra de desempenho Android

Nenhum carregador genérico dinâmico por frame, nenhum plugin finder global,
nenhuma varredura de diretórios durante a corrida. Os adaptadores são
resolvidos uma vez, no import inicial, sem custo por quadro. Todo teste
futuro precisa preservar RGBA, fisica, arquivo de save, Android launcher,
DEV, AAB e os gates QA785/786/787.

## Segunda etapa QA789 — módulos do jogo realmente migrados

Além dos três aceleradores QA785/786/787, foram transferidos 25 arquivos Python (15 world, 10 rendering) preservando blobs Git originais. A raiz conserva adaptadores com a MESMA instância de módulo via sys.modules. Para conferir todos os nomes, consulte MANIFESTO_MODULOS_v327789.json.

Os módulos com SHA fixado em preflights históricos continuam intactos; detalhes em QA_RAIZ_PROTEGIDA_v327789.md. Isto inclui City v3118, City v3122, cenários v398, shader GLES e render QA. A física, o loop principal, os saves e o empacotamento não foram reescritos. Documentos Android independentes estão em docs/android/.

## QA790 — módulos reais de jogador, inimigos, sistemas, HUD e tutorial

- `entities/player/animation_state.py` e `skin_rules.py`: funções extraídas literalmente do motor.
- `entities/enemies/laser_collision.py`: hitbox central do laser sem alterar parâmetros.
- `systems/challenge_helpers.py`: semana e gerador de três missões, usando o mesmo `random` global.
- `world/day_night_math.py` e `rendering/color_helpers.py`: funções matemáticas puras do motor.
- `ui/hud/`: dois módulos HUD históricos ativos, migrados com aliases.
- `ui/tutorial/`: três módulos de texto/i18n/lições históricos, migrados com aliases.
- `systems/controls_v3171.py` e `challenges_v3212.py`, `entities/player/skins_v3188.py`: módulos integrais, sem edições internas.
- `archive/prototipos_tutorial/`: oito arquivos obsoletos sem referência de execução, arquivados por SHA.

O motor, as classes Sprite, o tutorial obrigatório e o loop principal não foram reestruturados. Os imports das dez funções mantêm o mesmo ponto de definição, sem criar chamadas intermediárias por quadro. A raiz perdeu oito scripts de protótipo; os arquivos QA com hash pinado foram preservados. Consulte `INVENTARIO_QA_v327790.md` e os manifestos R20.
