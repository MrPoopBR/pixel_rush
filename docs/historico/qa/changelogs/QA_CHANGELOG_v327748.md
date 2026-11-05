# PIXEL RUSH v3.277.48-QA — limpeza RSS parcelada e clima sem temporarios repetidos

Branch isolada: `qa/android-full-performance-v3.277.48`.
Base exata: `qa/android-full-performance-v3.277.47`, commit `40cb1bf328c57f8d326d94f9a2e54113a2614c8c`.
Nova versão: `v3.277.48-QA-ANDROID-RC` e `buildozer.spec 3.277.48 / 327748`.
Sem APK, sem AAB, sem Android/ADB.

## Integrado no caminho real QA

1. `pixelrush_qa_performance_integrated_v327742.py`: a limpeza de caches frios antes executada como um bloco apos cada 180 flips passou a ser agendada no 180o flip e processada nos seguintes frames que nao coincidam com o redesenho do fundo a cada cinco quadros. Maximo de 12 chaves visitadas por passo; evita remover cache do bioma que estiver ativo no momento do passo. Varias instancias vivas sao protegidas. So ativa sob RSS maior que o teto existente. O loop original nao recebe alteracoes de fisica ou render.
2. `pixelrush_qa_cache_trim_v327748.py`: escalonador com referências fracas, LRU da cidade preservado enquanto a cidade estiver ativa, cache de origem global conserva todos biomas de mundos vivos. Fallback para o limpador antigo se falhar import/alguma exceção, e flag `PIXELRUSH_QA_STAGGER_TRIM=0` desativa a novidade.
3. `_weather_cached`: chuva, neve, areia, cinzas e vento mantêm valores de cada partícula mas não repetem multiplicações iguais dentro dos laços. Duas tuplas de 26 sementes foram pré-computadas, evitando slicing de tuplas em frames de clima normal.
4. `tests/test_qa_stagger_trim_v327748.py`: regressão RGBA contra o método real de mundo antes do wrapper, 252 combinações bioma/clima/frame, 180-flip sem varrer no quinto, múltiplos mundos, mudança de bioma durante limpeza, fallback legado e ausência de mudanças no RNG.
5. `.github/scripts/qa_benchmark_performance_v327748.py`: benchmark SDL dummy de 48 quadros RGBA adicionais, CPU da rotina meteorológica, duração por frame da limpeza parcelada, RSS observado e sinalizadores explícitos de que não se mediu gameplay integral, GPU, FPS Android nem APK.
6. `.github/workflows/qa-offline-v327748.yml`: execução isolada sem ações Android, todas as suites offline herdadas, novos testes, preflight de SHA/versão e benchmark com artefatos JSON.

## Limitações e estados honestos

A limpeza sob pressão RSS é real, mas não melhora automaticamente o desenho pesado do 5º quadro: só remove a colisão periódica da antiga coleta de caches e limita quanto ela faz por apresentação. O verdadeiro compositor 2.5D e as copias de buffer permanecem inalterados, bem como a cadência do fundo em 5 quadros. Não se ativou offscreen, PBO, GLES, novos shaders nem otimização cuja paridade integral não foi comprovada. A mudança de clima evita operações Python, mas o impacto em FPS depende do tempo gasto nessa camada na corrida.

Veja `QA_TRACKER_32_v327748.md`. **Estado mantido: 12/32 concluídas offline, 15/32 parciais, 5/32 pendentes** até testes comprovados e integração adicional. Resultado do benchmark não pode ser descrito como ganho de FPS Android.

## Integridade

Somente branch QA v3.277.48. Arquivos do código do jogo alterados: identificador `VERSAO` na cópia Android QA; implementação isolada no módulo de desempenho QA; Buildozer apenas número de versão (sem build). Nenhuma alteração na main, DEV, pets, saves, física, tutorial, configurações de qualidade visual, assets, lógica de biomas ou workflow AAB. O ambiente offline utiliza pygame-ce 2.5.8.

## Evidências
Os resultados CI devem ser preenchidos somente depois de execução confirmada; não afirmar regressões aprovadas a partir de código não testado.
