# PIXEL RUSH v3.277.91-QA — R21: classes com estado e auditoria estrutural

**Base:** QA790 commit `854f3906d31f15f4d4fe09d8212535ad835fa654` · **Branch:** `qa/r21-auditoria-classes-motor-v3.277.91`.

## Divisão controlada do motor
Foram separadas **3 classes completas**, com os métodos transcritos literalmente (sem alterar ordens, RNG, colisões ou desenho):
- `_FonteHindiComFallback` e `_FontePainelLocalizado` → `src/pixelrush/ui/i18n_fonts.py`;
- `Particula` → `src/pixelrush/entities/particles.py`.

O motor agora importa diretamente as classes nos seus locais anteriores, sem wrappers de atualização a cada quadro. A classe `Jogador`, os obstáculos, `Moeda`, `PoolManager`, tutorial obrigatório, pets, saves, loop principal e regras de jogo permanecem intactos.

## Auditoria da organização restante
A raiz da QA790 foi inventariada: **341 arquivos Python**, dos quais 50 QA, e **57 notas Markdown**. Nenhum módulo histórico que pode ser referenciado foi movido ou apagado. O mapa completo de pendências e critérios está em `docs/arquitetura/INVENTARIO_R21_v327791.md`.

## Versão e proteção
- `VERSAO` do motor: **v3.277.91-QA-ANDROID-RC**.
- `buildozer.spec`: versionName `3.277.91`, numeric `327791` (sem alterar receita).
- `main.py`, `JOGAR.py`, DEV, assets, pets, saves e workflows AAB: **nenhuma alteração**.
- Suíte de equivalência AST, pygame-ce/alpha, RNG, CI histórico e buffers RGBA 2.5D adicionada em branch isolada.
- **Nenhum APK/AAB compilado**. Ganho de FPS e homologação Galaxy A54 não alegados.
