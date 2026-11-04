# PIXEL RUSH — QA v3.277.82 — plano R13 após evidência real R12

**Fonte:** `PIXEL_RUSH_R12_20261104_202855.zip`, coletado no Galaxy A54. Arquivo traz JSON/CSV. Todos os números abaixo referem-se à v3.277.81, **não** ao código ainda não testado v3.277.82.

## Resultado A54 R12
- Corrida normal / Cidade: **3,56 FPS estimados** (1.358 quadros), p50 272,816 ms; câmera p50 **214,966 ms**.
- Neve: 3,17 FPS estimados; câmera p50 224,11 ms, mundo 2.5D p50 por chamada 133,821 ms.
- Replay / Cidade: 27,39 FPS estimados, sem smoothscale de câmera na maioria dos quadros.
- GLES/PBO: 0 frames, `criacao_ModuleNotFoundError`; C/NEON: 0 frames, `aguardando_preflight_fora_de_frame`.
- Memória: 474,23 MiB RSS de pico observado; 0 erros de gravação da telemetria. O sintoma de tela reduzida é relato do usuário; a resolução física da janela não existia no R12, por isso o novo gate R13 registra a dimensão real.

## Frentes pendentes de hardware
O tracker da QA781 registra 22 frentes offline aprovadas historicamente, e 10 frentes que ainda precisam de A54 real (#1, #3, #5, #7, #8, #10, #12, #28, #29, #32). **Nenhuma dessas dez é aprovada por introdução de código da QA782.** Validações offline do próprio novo head ainda devem ser executadas.

## Gates futuros de R13
1. **Viewport:** `r12_runtime.execucao_observada.tela_cheia_fisica=true` e `resolucao_janela_px` retornando dimensão física válida do A54. Confirmar enquadramento na tela do aparelho, incluindo menu, tutorial e botões.
2. **Câmera:** `r12_runtime.modulos.camera_neon.status`, `frames_native>0` e RGBA aprovado, senão motivo de fallback explícito. Comparar p50/p95/p99 da câmera e FPS entre R12/R13.
3. **2.5D e vinheta:** comparar `mundo_2_5d`, `qa_fundo_cache_chao`, `qa_render_apos_sprites` nos mesmos biomas; verificar visual e periodicidade 5:1 sem diminuir efeitos.
4. **GLES/PBO:** sem falso positivo: se desabilitado por segurança, indicar `frames_gles=0`, `gles_pbo_uploads=0`. Opcional apenas laboratório futuro; não ligar sem prova do driver.
5. **Regressão:** todas as letras do tutorial, morte/rewind, replay, pet, saves, HUD, lojas, física, hitbox, input e ROM SDL. Executar pygame-ce/RGBA/AST no CI e instalar em A54 sem remover save existente.

**Estado final:** integração offline ≠ homologação de hardware. `32/32 homologadas` = **NÃO**.
