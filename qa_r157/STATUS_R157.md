# PIXEL RUSH R157 QA — status

Esta branch e isolada da R155 estavel e herda a R156 como ponto de partida.

O pacote R157 v3.279.09-QA ja foi gerado e validado localmente a partir da fonte R156 oficial, mas **a instrumentacao R157 completa AINDA NAO foi publicada nesta branch** e **nenhum APK R157 foi compilado ou validado**.

O ZIP de fonte R157 traz os 28 probes direcionados, controle de cProfile na corrida, identificador Android `com.bigheadmobile_pixelrush_qa_r157`, versionCode `327909`, changelog e testes. A comparacao com a antiga v3.60.0 foi somente leitura: nenhuma feature antiga foi copiada ou restaurada.

Para compilar, e necessario publicar exatamente os arquivos R157 desta fonte validada e acrescentar workflow QA com guardas de integridade, mantendo todas as alteracoes fora das branches estaveis.
