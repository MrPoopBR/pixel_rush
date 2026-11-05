# PIXEL RUSH — A54 R12 REAL, diagnóstico de regressão v3.277.81

**Fonte:** ZIP R12 fornecido pelo jogador em 04/11/2026, `pixelrush_qa_v327781_r12.json`, `pixelrush_qa_frames_v327781_r12.csv` e screenshot 945×2048. Não copiar saves ou dados pessoais para o repositório.

## Evidências reais, não bench Linux

| Modo/cenário | Quadros reais | FPS estimado | Quadro p50 | Quadro p95 |
|---|---:|---:|---:|---:|
| Corrida normal, Cidade | 1.358 | **3,56** | **272,816 ms** | **509,084 ms** |
| Corrida normal, Neve | 107 amostras estatísticas (70 no grupo recente) | **3,17** | 277,860 ms | 518,236 ms |
| Replay, Cidade | 326 | **27,39** | *Consultar JSON real* | *Consultar JSON real* |
| Tutorial, Cidade | 149 | **5,29** | 221,034 ms | 403,594 ms |

Cidade corrida normal: câmera `camera_smoothscale` **p50 214,966 ms** (1.355 amostras); `mundo_2_5d` **p50 116,154 ms** por execução (276 amostras periódicas); `r11_post_vinheta` **p50 21,446 ms**; `qa_render_apos_sprites` **p50 21,816 ms**; CPU de processo p50 **283,593 ms**; RSS pico observado **474,23 MiB**, não uma medição de VRAM. Comparar tempos com R11 somente considerando condições reais e versão.

## Estado hardware comprovado

- `gpu_bridge.fallback=criacao_ModuleNotFoundError`, `frames_gles=0`, `frames_fallback=2594`, GPU real não utilizada. Não identificar qual módulo está ausente sem traceback.
- `camera_neon.status=aguardando_preflight_fora_de_frame`, `frames_native=0`, `teste_real=false`: o teste de boot era inerte com `zoom=0` e aplicava apenas um micro-passo abaixo de 0,002. Não indica biblioteca inexistente; C/NEON sequer foi medida no boot.
- `gles_pbo_uploads=0`, `egl_vsync_aplicado=null`. Não inferir que as melhorias GLES3/PBO/VSync estejam ativas.
- `scroll_cidade_hits=0`, `cidade_sprite_direto=359`, `cidade_cobertura_direta=367`: caminho incremental não foi selecionado nesta coleta. A cidade desenhou via caminhos alternativos.
- `gc_coletas_0=72`, `coletas_1=12`, `coletas_2=2`: esta melhoria tem execução observada, mas ganho em FPS não foi provado.
- Coletor R12 V2 conseguiu obter JSON e CSV sem alterar saves, 2 exportações, 0 erros reportados.
- Screenshot evidencia apenas região de 347×~617 px no canto superior esquerdo de imagem 945×2048, com grande superfície preta: corresponde à janela lógica 450×800 apresentada sem upscale.
- O modo de replay ~27 FPS contra corrida ~3,5 FPS é consistente com gargalo em pipeline da corrida, não prova falha de física.

## Raízes verificadas no código v3.277.81

1. `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py` chamava `pygame.display.set_mode((450,800))` em Android. `pixelrush_qa_gles_bridge_v327749.py` reabria essa janela via `_reabrir_sdl()` sem `FULLSCREEN` ou `SCALED` após falha GPU. Logo não preenchia a tela física.
2. `pixelrush_qa_camera_native_auto_v327742.py` verificava geometria antes de o zoom atingir limiar `0.002`: o boot com zoom zerado retornava `None` sem executar prova RGBA nem benchmark. Resultado era fallback para `pygame.transform.smoothscale` (~215 ms).
3. O cálculo da área de toque Android assumia mapeamento full-screen sem letterbox; após consertar aspecto, deve acompanhar a escala visual.
4. Independentemente da câmera, a composição do mundo 2.5D ainda tem custo elevado a cada quinto quadro; nenhuma correção R12 foi integrada para este subsistema sem teste pixel-exato.

**Conclusão:** Regressão de fullscreen é comprovada por screenshot e código. Falha de instrumentação de boot nativo é comprovada por código e estado R12. Desempenho futuro permanece **não homologado** até novo APK e R13 real no Galaxy A54.
