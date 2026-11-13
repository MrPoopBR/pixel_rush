# PIXEL RUSH R156 v3.279.08-QA — changelog

Base: fonte R154 SHA-256 2a27e23a55142b8ce1f707794be302f8470015f10591449c9a031f84396e47e9; patch R155 exato e verificado.

## Somente diagnostico

- Adiciona sondas de tempo real de parede e CPU por thread em funcoes selecionadas de desenho e morte.
- Acrescenta medida dos intervalos depois de chamadas reais a pygame.display.flip/update.
- Executa uma unica janela de cProfile de aproximadamente 10 segundos, separada e identificada como intrusiva.
- Exporta JSONL por intervalo de 10 segundos e arquivo .prof em armazenamento privado do app QA; limitado a 80 rotulos e ate 1024 duracoes recentes por rotulo.
- Redireciona as metricas para stdout/logcat se armazenamento falhar, sem afetar jogo.
- Incrementa o codigo apenas do APK QA: version 3.279.08, numeric_version 327908.
- Altera apenas o package.name da QA: com.bigheadmobile_pixelrush_qa, preservando os dados da R155 estavel.

## O que fica preservado

Assets, audio, RNG, fisica, gameplay, aparencia, RGBA, saves, tutorial, replay e o patch de boot .pyc da R155. Nenhuma alteracao intencional nessas funcionalidades; a propria instrumentacao adiciona sobrecarga apenas na QA.

## Validacao exigida

- Hash integral da fonte R154 e aplicador oficial R155.
- Testes pygame-ce com RNG e RGBA deterministico em fixture.
- Syntax/compile de todos os .py da fonte completa.
- Reversibilidade textual das insercoes de profiling em todo arquivo de producao instrumentado.
- Auditoria estatica da assinatura, Android package/versionCode, ARM64 e 16 KiB.
- Homologacao real em Galaxy A54 e MEmu so depois de teste em hardware.

**Nao afirmar que R156 melhora FPS. Ela mede as causas e pode ser mais lenta durante cProfile.**
