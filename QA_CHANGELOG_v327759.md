# PIXEL RUSH — Changelog consolidado v3.277.59-QA

**Branch única:** qa/fechamento-32-v3.277.57, base v3.277.58-QA.

1. **CPU/RAM #2/#7/#10/#24**: no compositor QA de uso real, ativa o empréstimo do buffer de geometry de 450x500 que já pertence ao LivingWorld (sem a segunda cópia de aproximadamente 900 KiB por cena). Cidade e Modular já possuem o caminho de empréstimo; a flag padrão foi ligada sob guarda de identidade da Surface e método de oclusão presente. Fallback PIXELRUSH_QA_GEOMETRY_BORROW=0. Nenhuma outra rota, cena ou mapa é emprestado.
2. **Partículas #18/#20**: sementes inteiras de Neve/Deserto e constantes de flutuação de poeira/chuva da Cidade pré-calculadas em tuplas imutáveis. Equivalência depende de manter int, float, modulo, sequência SDL e RGB oculto do overlay. Fallbacks PIXELRUSH_QA_MODULAR_SEEDS=0 e PIXELRUSH_QA_CITY_PARTICLE_SEEDS=0.
3. **Testes**: acrescentada suite pygame-ce offline real de equivalência byte RGBA de Cidade, Neve/Deserto, oclusão acústica e transições climáticas; CI anterior permanece. Os testes ainda não são a homologação Android.
4. **Metadados**: versão engine, VERSAO_ATUAL e buildozer numerico atualizados. Sem invocar Buildozer nem alterar APP ID, main, DEV, pets, física, saves, clima visual ou arte.

**Contagem conservadora antes dos novos gates:** 14/32 concluídas offline, 18 parciais e 0 Android. Somente promova números mediante logs de testes integrados.
