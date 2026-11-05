# Organização QA R19 — regras de preservação

## Arquivos intencionalmente retidos na raiz

A organização da v3.277.89 não apaga todo arquivo Python histórico.
Os antigos workflows `.github/scripts/qa_preflight_*.py` possuem
**listas de arquivos e hashes SHA1 de conteúdo exato**. Mover tais módulos
e deixar apenas um adaptador alteraria seus hashes e quebraria gates
históricos (além de impactar os builds APK/AAB que rodam esses scripts).
Exemplos protegidos:
- `pixelrush_city2_v3118.py` (blits do núcleo Cidade)
- `pixelrush_city2_v3122.py` (workflows legados)
- `pixelrush_cenarios_v398.py` (cenários tradicionais)
- `pixelrush_qa_render_v327729.py` (bootstrap QA)
- `pixelrush_qa_gles_exact_v327736.py` (shaders GLES)
- `pixelrush_qa_city_tiles_v327749.py`,
  `pixelrush_qa_incremental_scene_v327750.py`
- `QA_TRACKER_32_v327782.md`, `QA_CHANGELOG_v327782.md` e
  outras notas referenciadas pelos preflights antigos.

**Não são lixo**: arquivos com nome antigo também podem ter
importação indireta por cadeias de herança/caches, ou serem referenciados
por validações de pacote. Foram mantidos intactos.

## Duas frentes desta entrega

**1. Código do jogo:** 25 módulos originais foram transferidos sem
reescrita para `src/pixelrush/world/` e `src/pixelrush/rendering/`,
mantendo adaptadores de `sys.modules` na raiz. Consulte
`docs/arquitetura/MANIFESTO_MODULOS_v327789.json` para paths e SHAs.

**2. Organização de QA/documentos:** foram arquivados sem alterar conteúdo
três documentos independentes antigos para `docs/historico/qa/auditorias/`
e `docs/android/`. Os nomes/SHAs estão em
`docs/arquitetura/MANIFESTO_DOCUMENTOS_v327789.json`.
Ferramentas QA já estão agrupadas por função em
`qa_a54/`, `qa_native/`, `tests/`, `tools/` e
`.github/scripts/`, portanto não receberam cópias duplicadas.
Os workflows antigos não foram editados.

## Regras para próximas migrações

Antes de remover um arquivo raiz, auditar *todas* as referências de
nome literal, `runpy`, `importlib`, `__file__` e SHA em CI; migrar
seu código, atualizar importações e empacotamento de forma atômica;
validar no Android real antes de eliminar a compatibilidade.
Os adaptadores têm pequeno custo de importação inicial, **zero
chamadas por quadro**.

A melhoria QA785/786/787 e a câmera/GLES continuam regidas por seus
gates e fallbacks anteriores. Nenhuma otimização nova de CPU/GPU
ou experiência visual foi introduzida pela reorganização.
