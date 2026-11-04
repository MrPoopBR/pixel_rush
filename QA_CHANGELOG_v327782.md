# PIXEL RUSH v3.277.82-QA — correção de tela pequena + diagnóstico e aceleração C/NEON

**Branch QA:** `qa/r13-camera-tela-cheia-v3.277.82`, criada da `qa/r12-arm64-homologacao-v3.277.81`. **Nenhum commit em main, DEV ou AAB**.

## Base: relatório real R12 do Galaxy A54

ZIP R12 recebido em 2026-11-04: 2.594 quadros observados, 2.400 linhas CSV recentes e 0 falhas de exportação.

| Indicador (corrida Cidade) | R12 real A54 |
|---|---:|
| Cadência média estimada | 3,56 FPS |
| Tempo total por quadro, p50 | 272,816 ms |
| Câmera smoothscale, p50 (1.355 amostras) | 214,966 ms |
| Render antes do zoom, p50 `renderizacao_e_ui` | 41,368 ms |
| Render mundo 2.5D, p50 por chamada (276 amostras) | 116,154 ms |
| Fundo/cache chão, p95 | 232,681 ms |
| Pós-sprites, p50 | 21,816 ms |
| Simulação, p50 | 5,204 ms |
| Apresentação swap, p50 | 3,786 ms |
| RSS pico observado (toda sessão) | 474,23 MB |

A câmera é o maior custo recorrente. O fundo 2.5D continua caro a cada quinto quadro. Replay sem câmera custou p50 ~32,9 ms e teve cadência ~27,39 FPS. No R12: 0 frames GLES e 1 falha de inicialização `criacao_ModuleNotFoundError`; 0 frames C/NEON, status `aguardando_preflight_fora_de_frame`. **Não existe evidência de 32/32 Android homologadas**.

## Mudanças delimitadas

1. **Janela Android QA em tela cheia física:** na entrada do engine, somente com `E_ANDROID && PIXELRUSH_QA_ANDROID=1`, chamar `pixelrush_qa_android_display_v327782.criar_tela((450,800))` solicitando `pygame.display.set_mode((0,0), pygame.FULLSCREEN)`; se o driver recusar ou retornar resolução inferior ao canvas, retornar a `set_mode((450,800))` da v781. A superfície lógica de 450×800, desenho, ordem de passes, `screen_to_virtual` e controles não mudam. Testes podem simular a janela, mas o tamanho exibido no A54 exige homologação visual.
2. **Não provocar a falha GLES por padrão:** perfil QA Android não solicita mais automaticamente a ponte GLES falha no aparelho (`PIXELRUSH_QA_GLES_BRIDGE=0` por default). O experimento segue disponível com override explícito e com todos os gates antigos. PBO/GLES não serão marcados ativos sem counters no R13.
3. **C/NEON com resolução segura do SONAME:** também corrige a causa do gate inerte vista no R12: a primeira simulação com zoom 0 ficava abaixo do limiar 0,002 e retornava `None` antes de sequer comparar pixels. O gate QA782 simula a convergência até atingir zoom efetivo **fora do frame**, restaura `zoom` e `foco_y` exatamente ao estado anterior e só então mede RGB/RGBA e CPU nativo, mantendo fallback.

3. **C/NEON com resolução segura do SONAME:** o pré-teste existente da câmera pode resolver `libpixelrush_camera_crop_v327741.so` via SONAME ou, se necessário, pelo `getApplicationInfo().nativeLibraryDir` do APK obtido via Pyjnius fora do frame. **Mantido** o requisito anterior de RGBA pixel-exato e microbenchmark com ganho ≥15% e 0,10 ms; sem aprovação, mantém o `smoothscale` original. Falhas na inicialização agora aparecem no relatório em vez de serem silenciosas.
4. **R12 V2 preservado:** a v782 continua gerando `pixelrush_qa_v327781_r12.json` e `pixelrush_qa_frames_v327781_r12.csv`, para o coletor Windows V2 existente. JSON identifica `v327782_camera_tela_cheia`, grava o modo e as dimensões reais da janela, além dos counters GLES/NEON.
5. **Versão e regressões:** engine `v3.277.82-QA-ANDROID-RC`, Buildozer `version = 3.277.82`, `android.numeric_version = 327782`; testes `tests/test_qa_r13_camera_tela_v327782.py` de fullscreen/fallback, perfil Android, carregamento nativo, preservação de 450×800 e compatibilidade R12, além de suítes antigas pygame-ce e RGBA/zoom.

## Escopo protegido
Não alterar `main.py`, arquivos de skins, HUD, sprites, física, tutorial, pets, saves, RNG, colisões, shaders, qualidade de imagem ou workflows AAB. Nunca desinstalar automaticamente um APK ou limpar dados. A v781 continua disponível para rollback.

## Gates ainda pendentes
Esta revisão **não foi executada no Galaxy A54**; uma compilação e testes CI não provam que a tela foi corrigida no hardware nem que C/NEON acelerou. O renderer SDL segue o fallback garantido; o mundo 2.5D ainda precisa de outra otimização pixel-exata se continuar ~116 ms por chamada. Não aprovar 32/32.
