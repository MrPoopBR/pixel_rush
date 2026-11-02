# PIXEL RUSH — v3.277.35-QA: janela SDL + OpenGL ES, swap EGL direto

**Branch:** `qa/android-gles-direct-v3.277.35`
**Base:** `qa/android-gles-gate-v3.277.34`
**Status:** PROTÓTIPO EXPERIMENTAL ISOLADO, NÃO integrado ao jogo.
**Decisão:** shader de zoom REPROVADO para substituição por diferenças de pixels.
Nenhum ganho real de FPS Android foi demonstrado.

## Contexto: telemetria REAL Android da v3.277.30-QA
- Corrida ~4,8 FPS versus replay ~26,28 FPS (mesmo dispositivo).
- p95 do `camera_smoothscale`: ~187,89 ms; mundo 2.5D: ~95,24 ms.
- O profiler mede CPU e tempo de parede; não mediu GPU nativa.
- A v3.277.34-QA já descartou shaders lineares simples porque
  divergem do `pygame.transform.smoothscale()` em vários pixels.

## Arquivos implementados nesta branch

1. `pixelrush_qa_gles_present_v327735.py`: renderizador STANDALONE
   que CRIA sua própria janela SDL com `pygame.OPENGL | DOUBLEBUF`
   e solicita contexto **OpenGL ES2**, sem tocar no entrypoint do jogo.
   Usa textura RGBA atualizada via `glTexSubImage2D`, shader de zoom
   com crop/foco e apresenta a imagem por **`eglSwapBuffers`**
   quando SDL forneceu superfície EGL corrente (caminho Android).
   Em desktop X11/GLX, usa `pygame.display.flip()` →
   `SDL_GL_SwapWindow` como fallback. O renderizador **não chama
   `glReadPixels`** nem recupera quadros da GPU.
   O upload de uma textura RGBA 450×800 ainda custa ~1,37 MiB
   por quadro e exige benchmarking em GPU real.
2. `tests/test_qa_gles_direct_v327735.py`: suite independente
   testa 3 padrões RGB, zoom 0, .012, .025 e .034 com foco,
   12 cenas de 360.000 pixels cada. O **único**
   `glReadPixels` está no teste de equivalência, NUNCA no
   caminho de renderização/apresentação. Verifica pixels RGB
   por pixel, presença de artefatos, diferenças e tempo.
   Gera `qa-gles-direct-v327735.json`.
3. `.github/scripts/qa_preflight_v327735.py`: hashes de blobs Git
   de código/recursos, invariantes de 60Hz, main intacto e GPU
   ausente do entrypoint do jogo; buildozer preservado exceto
   metadados de versão experimental.
4. `.github/workflows/qa-gles-direct-v327735.yml`: CI **somente
   protótipo**, usa pygame-ce 2.5.8 + Xvfb/Mesa em Linux;
   NÃO compila APK/AAB, não altera main, DEV ou produção.
5. `VERSAO_ATUAL.txt`, código QA e `buildozer.spec`: atualizados
   para v3.277.35-QA-ANDROID-RC, numeric_version 327735.
   Os identificadores de APK e fluxo de publicação permanecem intactos;
   esta versão QA NÃO foi homologada como publicação.
6. Testes existentes específicos que verificam o identificador
   de versão atualizados apenas nesta branch.

## Evidências locais: pygame-ce 2.5.8, Python 3.13, Xvfb/Mesa llvmpipe

- Protótipo em **janela real SDL OpenGL ES** abriu e apresentou 12 frames.
- **GLX** foi escolhido pelo SDL no desktop Linux. O caminho
  Android `eglSwapBuffers` está implementado, **mas NÃO foi
  testado no aparelho**.
- **0 leituras GPU→CPU no pipeline do renderer**.
  12 leituras somente no teste de comparação pixel-a-pixel.
- Cópia sem zoom (3 padrões): 0 divergências em 360.000 pixels.
- Zoom aplicado (9 casos): TODAS as imagens tiveram divergências.
  Exemplo com padrão checker: 116.650 pixels distintos a zoom 0.025;
  gradient: 360.000 / 360.000 distintos; outro padrão: 342.965.
- Cronometragens curtas de Linux não medem tempo de execução GPU,
  nem equivalem a FPS real Android ou emuladores.
- Sintaxe Python/SDL testes locais executados no espelho de trabalho.
  Suíte e preflight **exatos do GitHub** só podem ser aprovados
  após logs CI da nova branch.

**Conclusão de homologação:** qualidade visual NÃO equivalente,
portanto NÃO habilitar shader, NÃO substituir a câmera existente.
O protótipo é uma referência de arquitetura para futuras versões;
não altera a jogabilidade.

## Critérios de aprovação FUTURA (ainda não atendidos)

[ ] Reproduzir `smoothscale` byte-identicamente para zoom/foco/cenas
    em ambos os formatos RGB/RGBA e nos sete biomas.
[ ] Validar swap EGL no APK ARM64 real, Android 16, emuladores,
    rotacionamento, lifecycle/pause/resume, touch e apresentação.
[ ] Medir upload textura CPU→GPU, tempo GPU e vsync real com Perfetto.
[ ] Comparar frames p95/p99 de corrida/tutorial/replay no mesmo aparelho.
[ ] Verificar saves históricos e todas as funções desativadas.
[ ] Regressões de física, tutorial, UI, pets, compras, AAB
    somente após o pipeline passar nos gates.
[ ] Integrar SOMENTE com ganho estável de FPS e
    zero diferença visual, mantendo fallback CPU obrigatório.

## Preservação
NENHUM arquivo foi alterado diretamente nos branches main, DEV e
release. A física, câmera atual do jogo, áudio, obstáculos, moedas,
tutoriais, saves, pets, conquistas, compras, assets, recursos
desligados, shaders preexistentes e workflow AAB não foram alterados.
O novo renderizador não é importado por `main.py`, pelos módulos
de renderização QA já ativos ou pelo jogo de produção.

**Não foi gerado APK debug desta branch:** teste isolado de
arquitetura antes de integração, sem impacto nos instalados.
