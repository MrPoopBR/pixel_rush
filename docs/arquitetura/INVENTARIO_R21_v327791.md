# PIXEL RUSH QA791 — auditoria da organização restante (R21)

Base validada: commit `854f3906d31f15f4d4fe09d8212535ad835fa654` da QA790. Branch: `qa/r21-auditoria-classes-motor-v3.277.91`.

## Inventário do repositório antes da alteração
- **1.009 arquivos** rastreados; **597 arquivos Python** no total.
- **341 arquivos Python na raiz**, sem redução artificial nesta etapa.
- Classificação dos Python na raiz: **50 QA**, **58 world**, **44 biomes2**, **39 ameaças**, **12 city2**, **134 outros pixelrush**, **3 entradas/outros** e **1 protótipo 3273 ativo/referenciado**.
- **57 Markdown na raiz**, **88 itens em docs/** e **101 testes Python em tests/**.
- Os 50 arquivos QA da raiz incluem 47 citados por preflights históricos e 3 adaptadores já migrados. Não mover os 47 sem migrar todas as referências SHA/prefight e revalidar empacotamento Android.
- `src/pixelrush/game.py` ainda é apenas uma fachada desktop; o loop original permanece no motor da raiz. Não criar segundo motor de jogo.

## Alterações controladas da R21
- Extrair classe `_FonteHindiComFallback` e `_FontePainelLocalizado` para `src/pixelrush/ui/i18n_fonts.py`. Seus métodos permanecem com o mesmo texto/AST; dependência `_i18n247` aponta para o mesmo módulo Python.
- Extrair classe `Particula` para `src/pixelrush/entities/particles.py`; `pygame`, `Sprite` e `random` apontam para os mesmos objetos, sem wrappers no `update`/ `reset`.
- Três imports diretos ocupam exatamente os locais das definições antigas do motor. Nenhuma função de física ou aleatoriedade foi reescrita.

## Dívida restante e riscos
1. **Motor monolítico ~947 KB / >16 mil linhas:** classes `Jogador`, `SistemaClima`, `Moeda`, `PoolManager`, obstáculos e loop referenciam globais. Migrá-las exigirá um mapa de dependências e validação de estado/RNG/ordem do loop; não movê-las automaticamente.
2. **Centenas de módulos versionados na raiz:** nomes são usados por imports estáticos, importlib, testes ou Android. Não assumir que versões antigas sejam lixo. Inventariar por grafo de dependências + testes antes de arquivar qualquer código.
3. **57 relatórios Markdown na raiz:** reavaliar referências por workflows e manifests antes de mover, sem apagar o histórico.
4. **Empacotamento Android:** `buildozer.spec` mantém `source.dir = .`, entradas e recursos originais. Não alterar a receita de build.
5. **Desempenho:** a limpeza organizacional não é evidência de aumento de FPS; não há teste no Galaxy A54 nesta etapa.

## Gates exigidos
- AST classe a classe e AST do motor completo vs QA790 após substituição por imports e versão.
- Regressão pygame-ce de estados, superfícies RGBA e ordem das chamadas `random`.
- Regressões anteriores QA788–QA790 e buffers RGBA Cidade 2.5D em 2 perfis.
- Auditoria de escopo: nenhuma alteração em `main.py`, `JOGAR.py`, física não extraída, assets, saves, DEV, AAB e protótipos arquivados.
- Sem compilação APK/AAB; hardware pendente de validação futura.
