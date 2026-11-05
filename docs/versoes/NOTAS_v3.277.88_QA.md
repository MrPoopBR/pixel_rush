# PIXEL RUSH v3.277.88-QA — Organização segura, primeira etapa

**Data:** 05/11/2026. **Base:** v3.277.87-QA commit `73e1997144ee29f3f0dde5fa9a1420507ecfa9ef`. 
**Branch:** `qa/r18-organizacao-modular-v3.277.88`.
**Natureza:** organização do projeto, **nenhuma alteração de física/visual/gameplay**
e nenhuma alegação de melhoria de FPS. **Nenhum APK/AAB compilado**.

## Feito de verdade
- Código-fonte canônico de três acelerações Cidade QA785/786/787 movido
  **byte a byte** para `src/pixelrush/performance/city/`:
  `cache_budget.py`, `opaque_overdraw.py` e `technical_maps.py`.
- Mantidos os três nomes legados `pixelrush_qa_city_*_v32778*.py`
  como *adaptadores curtos* que devolvem a mesma instância de módulo via
  `sys.modules`. Imports antigos, estados globais, wrappers, testes e
  a ordem de instalação/rollback do QA não precisam mudar.
- Criados pacotes `src/pixelrush/{entities,world,rendering,systems,ui,utils}`
  como destinos de migrações futuras. **Nenhum sistema falso ou duplicado**
  foi implementado nessas pastas.
- Entrada opcional `src/main.py` delega ao launcher DESKTOP `JOGAR.py`;
  `main.py` Android e `JOGAR.py` permanecem byte a byte idênticos.
- Arquivados **71 documentos históricos** sem modificar seus blobs;
  `docs/historico/MANIFESTO_MOVIMENTOS_v327788.json` lista os caminhos
  antigos e novos, além do SHA exato de cada arquivo.
- Notas necessárias aos `tests/`, preflights antigos e GitHub workflows
  permanecem na raiz por compatibilidade.
- README anterior sobre AAB arquivado integralmente em
  `docs/historico/README_ANDROID_AAB_ORIGINAL.md`, e README principal
  substituído por mapa atual. Documentados os passos futuros e as restrições
  em `docs/arquitetura/`.
- Incluídos auditor de integridade somente-leitura em `tools/` e
  teste de importação/identidade de módulos.

## Limites importantes
O motor monolítico atual tem cerca de 16 mil linhas e **não foi desmembrado
nesta etapa**. Mudar imediatamente centenas de imports, nomes de módulos,
caminhos relativos a assets e empacotamento ARM64 seria regressivo antes de
testes em aparelho. A primeira etapa estabelece a arquitetura e migra um
subconjunto funcional comprovável.

O `buildozer.spec` mantém source.dir, exclusões, identificador do pacote,
permissões, bibliotecas e assinatura iguais; mudaram apenas versionName
e versionCode `3.277.88/327788`. `main.py`, DEV, assets, tutorial, física,
HUD, sons, saves, pets, recursos, receitas e workflows AAB intactos.

## Gates exigidos
- Compatibilidade de imports: raiz legada e src canônico devolvem o mesmo
  objeto Python, incluindo estados, privates e funções.
- SHA Git original: conteúdo de cada um dos 71 documentos arquivados.
- Bytes dos três módulos fontes canônicos idênticos ao base QA787.
- Compare `main.py`, `JOGAR.py`, assets, workflows AAB e motor:
  no motor muda somente a string VERSAO.
- Regressões QA785/QA786/QA787 pygame-ce (buffers RGBA, 130 quadros,
  clima e quinto quadro) + smoke integrado e diagnóstico de import.
- Ainda não há prova de FPS no Galaxy A54 após esta organização.

**Política:** só retirar os adaptadores antigos após homologação de
cada nova família de módulos, sem alterar os saves nem o conteúdo dos
recursos artísticos.
