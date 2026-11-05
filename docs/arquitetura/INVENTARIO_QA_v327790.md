# Inventário de QA na raiz — v3.277.90

A auditoria de referências de `.github/scripts` do snapshot base R19
encontrou **47 dos 50 módulos `pixelrush_qa_*.py` da raiz** citados em
testes/preflights históricos. Alguns scripts verificam até o **SHA1
exato do texto**, e não apenas a API importada. Portanto, substituir
esses arquivos por adaptadores quebraria gates, inclusive no caminho
de validação Android. Por segurança, **não foram alterados**.

Os três restantes são os adaptadores QA785, QA786 e QA787 que já foram
migrados e homologados offline no R18. Não há outros módulos `pixelrush_qa`
da raiz disponíveis para remover sem mudar as políticas de preflight.

## Organização por responsabilidade (sem duplicação de código)

| Responsabilidade | Local canônico existente | Compatibilidade |
|---|---|---|
| Cidade 2.5D (QA785/786/787) | `src/pixelrush/performance/city/` | Três adaptadores na raiz |
| Benchmarks de CPU/RGBA A54 | `qa_a54/` | Inalterado |
| Câmera C/NEON | `qa_native/` | Inalterado |
| Regressões e fixtures | `tests/` | Inalterado |
| Preflights SHA de Android | `.github/scripts/` | **Não mover** |
| Workflows QA e AAB | `.github/workflows/` | AAB intocado |
| Documentação e versões | `docs/` | Manifests R18/R19/R20 |
| Protótipos históricos não ativos | `archive/prototipos_tutorial/` | 8 arquivos arquivados (sem alias) |

Para realmente reduzir mais os 50 nomes QA da raiz será preciso
modificar atomicamente todos os preflights legados e verificar novamente
o pacote Android, o que está fora do escopo de segurança desta etapa.

## Motor em refatoração

Nesta etapa foram separadas **10 funções reais** dos 16 mil versos do
arquivo principal para `src/pixelrush/entities/`, `systems/`,
`world/` e `rendering/`. O texto de cada função foi preservado
exatamente, e cada nome é importado na posição original, sem wrappers
chamados a cada frame. Os controladores completos de `Jogador`,
obstáculos, HUD e o loop principal permanecem originais.

Foram migrados por SHA do blob Git **8 módulos adicionais** de HUD,
skins, tutorial, controles e desafios; seus nomes originais continuam
como adaptadores para preservar o Android.

A raiz perdeu exatamente **8 arquivos .py de protótipos não ativos**:
arquivados, nunca eliminados do repositório. Manifests:
`docs/arquitetura/MANIFESTO_QA_R20_v327790.json` e
`docs/arquitetura/MANIFESTO_FUNCOES_MOTOR_v327790.json`.

Este inventário **não marca** GPU/PBO/NEON como homologados no A54 e
**não apresenta limpeza de arquivo como ganho de FPS**.
