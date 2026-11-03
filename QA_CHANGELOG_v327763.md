# PIXEL RUSH — Changelog v3.277.63-QA

Continuidade na branch única qa/fechamento-32-v3.277.57.

Adicionado gate integrado dos três arquivos PROD oficiais de tiles (neve, deserto e cidade_futurista) em tests/test_qa_tiles_menu_v327761.py. Testa SHA-256 exato, bytes totais reais, limite de 64 KiB por bloco, RNG preservado, ausência de Surface e término em até 32 passos de menu. Todos os gates v762 anteriores permanecem. Evidência de céu e clima da v761/v762 será reconciliada no tracker conforme CI.

Metadados de engine, buildozer, preflight, tracker e changelog atualizados para 3.277.63-QA. Sem mudanças no gameplay, física, efeitos, assets, DEV, main, pets, saves nem workflows APK/AAB. Não executar Android ou homologação final. Pré-CI 15/32 concluídas offline e 17 parciais.

## Resultado integrado CI #41721393824

**29/29 testes offline pygame-ce 2.5.8 aprovados**, incluindo 5 testes de tile/menu (4 sintéticos + 1 nos binários oficiais) e toda a suíte anterior do céu/partículas/geometry/GC. O pré-aquecimento SHA incremental preparou 3/3 tiles reais em 13 passos, 720381 bytes, limite máximo 64 KiB por passo. O céu dos sete biomas passou 168 comparações completas com clima RGB/RGBA, complementado por 14 modos de clima clássico, nuvens opacas/translúcidas e clima modular. Pela evidência, **#18 cache de céu/clima e #23 prewarm de biomas estão concluídas na implementação e validação offline**. Permanecem pendentes de homologação Android. Estado consolidado **17/32 concluídas offline, 15/32 parciais, zero homologação Android**; nenhum APK/AAB e nenhuma mudança em main, física, pets, saves, DEV ou arte.
