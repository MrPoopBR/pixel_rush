# PIXEL RUSH v3.277.82-QA — corrigir tela pequena + gate de câmera A54

**Branch QA isolada:** `qa/r12-correcao-camera-tela-v3.277.82` a partir de `qa/r12-arm64-homologacao-v3.277.81`.

## Alterações efetivas e somente solicitadas

1. **Tela Android QA**: substituída a abertura lógica `450×800` sem flags por `pygame.SCALED | pygame.FULLSCREEN` via `pixelrush_qa_android_display_v327782.py`; superfície de desenho permanece 450×800, proporcional no display físico. Se SDL não entregar renderer lógico, fallback para resolução física `(0,0),FULLSCREEN` com letterbox, sem esticar sprites/HUD.
2. **Toque Android QA**: `FINGERDOWN/FINGERMOTION/FINGERUP` usa coordenada normalizada da janela física e conversão para área visível proporcional; mouse e desktop continuam na rota original. As regras de gesto, hitbox, movimento e física não mudaram.
3. **Ponte GPU**: nunca intercepta fullscreen ou SCALED sem prova de integração no dispositivo. Assim uma falha de import/contexto não abre janela 450×800 no canto. Não reativa GLES3/PBO por suposição; conservadoramente mantidos OFF.
4. **Câmera C/NEON**: no boot QA, o benchmark de pré-teste força **apenas a geometria de amostra** para zoom 0,025 caso a câmera ainda esteja parada em zoom inicial zero. Restaura zoom/foco antes do frame real. A otimização só é habilitada mediante pixels RGBA idênticos e ganho medido no A54 por pelo menos 15% e 0,1ms. Sem prova o smoothscale original permanece.
5. **Telemetria R12**: v3.277.82 detectada, diagnóstico inclui Surface e janela física e modo de apresentação. Mantidos os nomes `pixelrush_qa_v327781_r12.json` e `pixelrush_qa_frames_v327781_r12.csv` para o coletor Windows V2 já instalado.
6. **Versão:** `VERSAO = "v3.277.82-QA-ANDROID-RC"`, Buildozer `version = 3.277.82`, `android.numeric_version = 327782`. Debug ARM64 somente.
7. **Testes:** `tests/test_qa_r12_a54_viewport_v327782.py` (pygame-ce, aspect ratio, eventos, flags, fallback GPU), `tests/test_qa_r12_camera_preflight_v327782.py` (pré-teste real pixel-exato com zoom zero, restituição da câmera, fallback), regressões históricas, verificador de sintaxe AST, CI offline e GLES/Mesa.

## Arquivos/sistemas preservados
Sem mudanças no `main.py`, DEV, workflow AAB, saves, pets, tutorial, física, colisões, assets, geração procedural, biomas, shader, GameFeel, regras de scroll e simulação. A apresentação muda somente para preencher proporcionalmente o display Android QA e mapear o toque. O código de câmera não altera o zoom visual durante gameplay; valida backend diferente apenas no boot com rollback garantido.

## Limitações
- R12 real veio da **v3.277.81**, antes destas correções. Comparação offline não comprova FPS ou fullscreen no Mali.
- A seleção nativa é condicional: uma falha RGBA, SONAME ou benchmark mantém a câmera lenta; o progresso não é sinônimo de ganho futuro.
- 32/32 continuam NÃO homologadas; especialmente GPU/PBO/scroll não foram selecionados no A54 v781.
- Save preservado na branch; nunca desinstalar o app instalado no A54 para contornar erro de assinatura debug.
