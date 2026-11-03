# PIXEL RUSH — Changelog consolidado v3.277.62-QA

Branch única qa/fechamento-32-v3.277.57, continuidade da v3.277.61.

#23: pré-aquecimento QA dos tiles PROD mudou de SHA síncrono de arquivos inteiros no boot para leitura SHA parcelada nos menus: até 64 KiB por frame, limite de 40 MiB/arquivo e 125 MiB geral, validação da integridade e da estabilidade dos arquivos entre blocos. Sem pickle, SDL, pygame.Surface, file descriptor persistente, RNG ou adiantamento da escolha dos biomas. Atlas permanecem pré-verificados pela thread da produção original; o carregamento PROD e os seus fallbacks não foram alterados. Integração na instância QA existente PrecargaVisuaisQA, fila de skins/pet e intervalo de 8 quadros preservados. PetStudio segue placeholder, sem ativar pets. Rollbacks PIXELRUSH_QA_TILES_IO_MENU=0 e PIXELRUSH_QA_TILES_IO_PREWARM=0.

Adicionada suíte tests/test_qa_tiles_menu_v327761.py de 4 testes e workflow pygame-ce offline conserva todas as provas anteriores, incluindo geometria/sky v761. Aguardando evidência do CI antes de concluir #23.

Mudanças somente em QA prewarm, argumento da precarga QA na engine, versionamento, gates, tracker e changelog. Sem mudanças em main, DEV, sprites, efeitos, física, colisões, saves, pets, assets, HUD ou workflows Android. Nenhum APK/AAB ou homologação final. Placar conservador 15/32 offline, 17/32 parciais, 0 hardware.
