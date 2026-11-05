# Auditoria GPU Android — PIXEL RUSH v3.277.22 (somente leitura)

## Evidências no código de v3.277.21
- PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py configura \`GpuPostProcessor\` com \`PIXELRUSH_GPU=off\` por padrão e inicia \`pygame.display.set_mode\` sem \`pygame.OPENGL\`.
- pixelrush_moderngl_v3107.py declara shaders \`#version 330\` e requer contexto OpenGL 3.3. O pipeline usa diversos mapas e texturas e realiza transferências CPU/GPU, além do retorno GPU/CPU para uma Surface de Pygame.
- Android utiliza OpenGL ES (EGL) e suporte ES 3.x não é garantido em todos os dispositivos. Não há no código um backend GLES e shaders \`#version 300 es\` equivalentes.
- O APK debug incluído v3.277.20 contém bibliotecas Android/SDL e o caminho GPU opcional, mas não demonstra renderização ModernGL ativa.

## Conclusão
Não forçar \`PIXELRUSH_GPU=on\` ou substituir a janela SDL por \`OPENGL\` nesta revisão: risco de tela preta, incompatibilidade com GLES, perda do compositor pygame e diferença de pixels nos efeitos. Manter o caminho Pygame/SDL estável. Esta é uma auditoria de viabilidade, não uma implantação de GPU.

## Próxima prova antes de migrar
1. Protótipo isolado GLES 3.0/3.1 com shaders equivalentes, fora da produção.
2. Capturar paridade visual por quadros em biomas, clima, zooms, HUD, tutorial e pets.
3. Medir FPS p50/p95/p99, RAM/RSS, uploads e readbacks GPU em telefones/emuladores ARM64.
4. Definir fallback SDL por capacidade real da GPU, incluindo perda/restauração de contexto ao pausar Android.
5. Aprovar somente após equivalência visual e ganhos medidos. Nenhuma alteração de shaders foi realizada.

Referências: https://github.com/moderngl/moderngl (requer OpenGL 3.3); https://source.android.com/docs/core/graphics/implement-opengl-es (GLES no Android); https://wiki.libsdl.org/SDL2/README-android (restauração de contexto).
