# Arquivo historico PIXEL RUSH

Este diretório **não é lixeira**. Todas as notas migradas preservam o blob
Git original, seu SHA e o histórico do repositório. Nada foi apagado do
histórico e nenhuma save foi alterada.

- `producao/`: notas antigas PROD.
- `versoes/`: notas anteriores da linha 3.277.
- `qa/changelogs/`: changelogs QA antigos não referenciados diretamente.
- `qa/trackers/`: trackers QA antigos não referenciados diretamente.
- `qa/auditorias/`: laudos antigos não utilizados como gate de execução.
- `README_ANDROID_AAB_ORIGINAL.md`: documentação original da assinatura/AAB.
- `MANIFESTO_MOVIMENTOS_v327788.json`: destino e SHA de cada documento movido.

Os arquivos históricos que `.github/scripts`, `tests/` ou workflows ainda
usam não foram movidos e continuam na raiz. Para voltar a uma versão
antiga do repositório, utilize o histórico Git: os blobs são iguais.

**Não usar estes documentos para declarar uma melhoria implementada ou
homologação no Galaxy A54.** A versão ativa é indicada em
`VERSAO_ATUAL.txt`.

### Documentos adicionais QA789

Três documentos originais foram realocados para docs/android e docs/historico/qa/auditorias. A relação com seus SHAs encontra-se em docs/arquitetura/MANIFESTO_DOCUMENTOS_v327789.json. Os documentos antigos com referências diretas no CI permanecem intocados.
