# PIXEL RUSH — Changelog consolidado v3.277.59-QA

**Branch única:** qa/fechamento-32-v3.277.57, base v3.277.58-QA.

1. **CPU/RAM #2/#7/#10/#24**: no compositor QA de uso real, ativa o empréstimo do buffer de geometry de 450x500 que já pertence ao LivingWorld (sem a segunda cópia de aproximadamente 900 KiB por cena). Cidade e Modular já possuem o caminho de empréstimo; a flag padrão foi ligada sob guarda de identidade da Surface e método de oclusão presente. Fallback PIXELRUSH_QA_GEOMETRY_BORROW=0. Nenhuma outra rota, cena ou mapa é emprestado.
2. **Partículas #18/#20**: sementes inteiras de Neve/Deserto e constantes de flutuação de poeira/chuva da Cidade pré-calculadas em tuplas imutáveis. Equivalência depende de manter int, float, modulo, sequência SDL e RGB oculto do overlay. Fallbacks PIXELRUSH_QA_MODULAR_SEEDS=0 e PIXELRUSH_QA_CITY_PARTICLE_SEEDS=0.
3. **Testes**: acrescentada suite pygame-ce offline real de equivalência byte RGBA de Cidade, Neve/Deserto, oclusão acústica e transições climáticas; CI anterior permanece. Os testes ainda não são a homologação Android.
4. **Metadados**: versão engine, VERSAO_ATUAL e buildozer numerico atualizados. Sem invocar Buildozer nem alterar APP ID, main, DEV, pets, física, saves, clima visual ou arte.

**Contagem conservadora antes dos novos gates:** 14/32 concluídas offline, 18 parciais e 0 Android. Somente promova números mediante logs de testes integrados.

## Correção do bloqueador da Cidade na mesma branch/versão

A CI #41716396740 revelou AttributeError: CityPilotScene não possuía _qa_uniform_tech na hierarquia v3122→v3125, apesar de herdar o render v3118 que o exige. Para não alterar o construtor artístico real nem criar outra Cidade, o QA instala pixelrush_qa_city_bootstrap_v327759, que calcula os metadados originais de forma tardia e segura sobre as Surfaces já finalizadas, antes do primeiro render. O fallback só esvazia os índices, nunca desativa a existência dos atributos. Este patch foi acompanhado de comparação byte RGBA dos seis canais e restaurador de hooks no teste. **O bug foi comprovado no CI; a correção só será classificada validada quando a próxima execução passar.**

## CI e gate de integração adicional

A execução GitHub Actions #41717129303 confirmou 16/16 testes offline e hashes protegidos. Foi criado tests/test_qa_world_real_v327759.py, conectado ao mesmo workflow, para verificar o caminho LivingWorld real por meio de hooks instalados como no main QA, duas instâncias, troca de bioma e mediana de render geometry em CPU. Valores de benchmark serão informados somente após log; são da máquina do CI, não do Android. Sem APK/AAB/Android.

## Resultado do pacote v759

- Execução de integração [#41717619668](https://github.com/MrPoopBR/pixel_rush/actions/runs/41717619668): 18/18 testes offline e preflight estático aprovados. Casos adicionais percorrem World real, múltiplas instâncias, memo, aliases, cena de Neve e oclusão.
- **#2 Compositor 2.5D persistente:** concluído em implementação e gate offline, graças à prova do caminho World/QA (não #5 scroll incremental nem Android). Tracker vigente **15/32 concluídas offline**, **17/32 parciais**, **0/32 homologadas Android**.
- Medição de CPU da geometry no runner Linux: snapshot 0,577948 ms vs. empréstimo 0,613193 ms (mediana de 15); o empréstimo evita a Surface extra de 900 KB, **não se afirmou FPS superior**. A flag de fallback continua disponível.
- Preservação comprovada por preflight AST e arquivos protegidos; não houve recompilação ou teste Android, merge com main, modificação física, saves, pets, DEV ou jogabilidade.

## Refinamento após benchmark da areia

A primeira versão com acesso indexado aos pares de sementes estava mais lenta na areia em teste pygame local. Agora as partículas ativas são percorridas diretamente em tuplas pré-computadas (Neve: 18/6; Areia: 12/4); o fallback contém o loop aritmético original sem overhead adicional. Teste isolado de 12 linhas: 6,796 µs original vs 6,498 µs direto neste host; não extrapolar para aparelho. RGBA, clima, quantidades e timing sem alteração intencional. Placar permanece 15/32 concluídas offline, 17/32 parciais.
