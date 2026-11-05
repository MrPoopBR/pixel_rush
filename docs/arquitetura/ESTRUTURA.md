# Arquitetura proposta e situacao real (QA v3.277.89)

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
