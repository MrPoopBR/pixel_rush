# PIXEL RUSH v3.277.89-QA — organização R19

Base: v3.277.88-QA, commit 17774a8d9e8b5d9df256ddc4ec1c1effa389ac6a
Branch: qa/r19-mundo-render-qa-organizacao-v3.277.89
Escopo: organização estrutural, sem alterações de jogabilidade, sem build Android.

## 1. Mundo, Cidade e renderização

Foram migrados **25 módulos reais**, com conteúdo byte a byte idêntico ao
Git original: 15 para src/pixelrush/world (Cidade, biomas, runtime) e
10 para src/pixelrush/rendering (efeitos, céu, iluminação, render legado).
Os imports antigos na raiz agora usam adaptadores sys.modules que devolvem
a mesma instância. A medida conserva caches, objetos e estados globais; não
cria trabalho por quadro nem um loop de jogo duplicado.

Manifesto de caminhos e SHAs:
docs/arquitetura/MANIFESTO_MODULOS_v327789.json

O pipeline de otimização Cidade QA785, QA786 e QA787 continua preservado.
Os arquivos City v3118/v3122, cenários v398, QA de GLES e outros SHA-pinned
por preflights foram deixados intactos: movê-los sem atualizar seus testes
historicamente quebraria gates offline/Android.

## 2. Organização de QA, ferramentas e documentação

Três documentos históricos independentes foram arquivados, sem alterar os
bytes e mantendo seus SHAs Git: auditoria GPU Android antiga e os arquivos
CHECKLIST_ANDROID/INTEGRACAO_ANDROID_RC_REVISAO. Seus novos caminhos estão
em docs/android e docs/historico/qa/auditorias.
Manifesto: docs/arquitetura/MANIFESTO_DOCUMENTOS_v327789.json

As ferramentas existentes continuam organizadas em qa_a54, qa_native,
tests, tools e .github/scripts. Arquivos usados diretamente por preflights
não foram realocados por conveniência, evitando cópias duplicadas e
dívida de compatibilidade. O README, árvore e plano foram atualizados.

## Proteção de sistemas e versão

- main.py e JOGAR.py mantidos idênticos.
- Motor principal com mudança exclusiva na string VERSAO para
  v3.277.89-QA-ANDROID-RC.
- buildozer.spec: apenas version 3.277.89 e android.numeric_version 327789.
- Sem alterações na jogabilidade, física, sprites, arte, câmera, som, HUD,
  tutorial, saves, pets, DEV, AAB, receitas e demais biomas.
- Não removidos arquivos por parecerem antigos; há 25 adaptadores legados
  que precisam permanecer até validação Android de empacotamento.
- Nenhum APK/AAB compilado nesta etapa.

## Gates previstos / verificações

1. SHA Git da QA788 versus os 25 módulos transferidos, byte a byte.
2. Mesma instância importada pelo nome antigo e pelo novo.
3. Documentos QA788 (71) e QA789 (3) com conteúdo original preservado.
4. Hash RGBA da mesma sequência de 130 quadros da Cidade, imagem e
   cinco mapas a cada quinto quadro, normal e leve, QA788 vs QA789.
5. Regressões pygame-ce QA785/QA786/QA787 e viewport.
6. Integridade dos arquivos com hash hard-coded nos preflights antigos.

A organização é real, mas **não está completa**: o motor de 16 mil linhas,
entidades, saves e muitos QA continuam na raiz até migração segura.
Não se declara ganho de FPS nem homologação no Galaxy A54 com esta etapa.
