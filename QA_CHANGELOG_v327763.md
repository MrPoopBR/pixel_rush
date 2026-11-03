# PIXEL RUSH — Changelog v3.277.63-QA

Continuidade na branch única qa/fechamento-32-v3.277.57.

Adicionado gate integrado dos três arquivos PROD oficiais de tiles (neve, deserto e cidade_futurista) em tests/test_qa_tiles_menu_v327761.py. Testa SHA-256 exato, bytes totais reais, limite de 64 KiB por bloco, RNG preservado, ausência de Surface e término em até 32 passos de menu. Todos os gates v762 anteriores permanecem. Evidência de céu e clima da v761/v762 será reconciliada no tracker conforme CI.

Metadados de engine, buildozer, preflight, tracker e changelog atualizados para 3.277.63-QA. Sem mudanças no gameplay, física, efeitos, assets, DEV, main, pets, saves nem workflows APK/AAB. Não executar Android ou homologação final. Pré-CI 15/32 concluídas offline e 17 parciais.
