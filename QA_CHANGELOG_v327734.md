# PIXEL RUSH — v3.277.34-QA: gate da camera GPU / GLES2

**Branch:** `qa/android-gles-gate-v3.277.34`
**Base:** `qa/android-camera-scene-v3.277.33`
**Status:** investigação experimental, sem GPU de produção ativada.
**NÃO homologada em Android. NÃO publicar.**

## Perfil medido anteriormente
Dados reais Android v3.277.30-QA: 2.400 frames (665 corrida normal);
corrida normal 4,8 FPS estimados, replay 26,28 FPS;
p95 camera_smoothscale 187,89 ms; mundo 2.5D 95,24 ms.
São medidas inclusivas; não somar os percentis. Nenhuma medição
nativa de GPU do aparelho está disponível.

## Auditoria de arquitetura
1. O jogo usa pygame `pygame.display.set_mode()` SEM OPENGL,
   apresenta por `tela.blit(...)` + `pygame.display.flip()`.
2. A SDL2 proíbe combinar `SDL_GetWindowSurface` com renderer/GL
   na mesma janela. Não é seguro acoplar um renderer 3D à janela atual.
3. `pixelrush_moderngl_v3107.py` é backend OpenGL 3.3 desktop,
   cria contexto offscreen, faz upload de diversas texturas completas
   e `framebuffer.read()` GPU→CPU a cada frame; NÃO resolve o
   problema de apresentar câmera no Android sem readback.
4. Android garante GLES2, enquanto GLES3 depende do fabricante e
   do driver. É preciso implementar EGL/swap direto e fallback
   original para aparelhos fracos e emuladores.
5. Mesmo um shader bilinear que pareça semelhante pode diferir do
   algoritmo de arredondamento `pygame.transform.smoothscale`.
   A comparação RGBA deve preceder qualquer ativação.

## Experimentos GLES locais (Linux, Mesa llvmpipe, não celular)
Protótipos EGL/GLES2 e EGL/GLES3 com quadros RGBA 450×800:
- Cópia sem zoom: 0 pixels RGB diferentes de 360.000.
- Zoom .025: 360.000 pixels RGB diferentes.
- Zoom .034: 359.998 pixels RGB diferentes.
- GLES2 upload+draw de 1 frame, Mesa software: ~1,0–1,7 ms;
  leitura de volta ~0,2–0,3 ms.
- `smoothscale` SSE2 do Linux na mesma fixture: ~0,5–0,7 ms.
  Estes valores não são equivalentes a FPS, não medem GPU móvel.
- **Resultado:** shader bilinear genérico REPROVADO para
  substituição visual; ativação GLES NÃO AUTORIZADA.

## Arquivos alterados APENAS nesta branch QA
1. `pixelrush_qa_camera_v327733.py`: conserta comparação de
   RGBA na segunda prova do autotune de backend; antes o esperado
   podia estar em RGBA e o recebido em RGB, rejeitando mesmo um
   backend idêntico. Não muda interpolação nem física.
2. `pixelrush_qa_gles_gate_v327734.py`: registra um diagnóstico
   passivo da janela SDL e **bloqueia explicitamente GPU** por
   falta de equivalência e prova no Android. Não abre janela,
   não importa ModernGL, não cria GL context no jogo.
3. `pixelrush_qa_android_v327728.py`: inclui o status do gate
   nos relatórios, exportando `pixelrush_qa_v327734.json`
   e `pixelrush_qa_frames_v327734.csv` sem sobrescrever
   versões anteriores.
4. `.github/scripts/qa_gles_camera_probe_v327734.py`:
   teste OFFSCREEN, executado apenas no CI Linux, em EGL/GLES2
   através de ctypes; verifica cópia, zoom, diferenças de pixels
   e custos de upload/desenho/readback. Não integra o APK.
5. `tests/test_qa_gles_gate_v327734.py`: asserts de ausência
   de ativação GPU, backend SDL inalterado, branch QA, física,
   telemetria, bugfix RGB/RGBA e build exclusivamente debug.
6. Atualiza apenas identificação `v3.277.34-QA-ANDROID-RC`,
   `buildozer.spec` (versão e numeric_version 327734),
   testes dependentes de versão, preflight e workflow dedicado.

## Gates
- [x] Prototipação local OpenGL ES2/3 offline concluída.
- [x] Cópia sem zoom equivalente em pixels no EGL llvmpipe.
- [x] Diferenças no zoom detectadas e alternativa GPU recusada.
- [x] Preservado caminho CPU `smoothscale`, sem novas dependências.
- [x] Preflight estático de hashes, branch e workflow preparado.
- [ ] GitHub Actions regressões pygame com código de branch final.
- [ ] APK debug ARM64 construído e auditado, 16 KiB/DT_NEEDED.
- [ ] Telemetria v327734 no mesmo celular e emuladores.
- [ ] Perfetto/gfxinfo e comparação de custo/temperatura/memória.
- [ ] Pipeline OpenGL ES com apresentação SDL diretamente na GPU.
- [ ] Prova de equivalência em todos os biomas, zooms, tutoriais.

## Próxima arquitetura candidata — NÃO implementada
Migrar **a janela inteira** para EGL/OpenGL ES 2, receber o quadro
final via upload RGB na textura e apresentar por EGLSwapBuffers,
sem `glReadPixels`, preservando entrada e orientação. Isso elimina
a etapa CPU `smoothscale` quando comprovadamente compatível, mas
precisa de um shader que reproduza os mesmos pixels e de testes
de integração Android. Uma troca parcial com readback e o modo
`pygame.display.flip()` atual são incompatíveis.
Se não for possível equivalência visual, manter o renderizador CPU.

## Garantias
NENHUMA mudança direta em main, DEV, saves, pets, compras, AAB,
física 60 Hz, colisões, geração de obstáculos, tutorial, partículas,
sprites, cenários, assets ou resolução de tela. A única diferença
de jogo da QA atual é o número de versão; o gate é observacional.
**Nenhum ganho FPS Android é alegado nesta versão.**
