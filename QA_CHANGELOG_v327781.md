# PIXEL RUSH v3.277.81-QA — APK debug ARM64 e coleta R12

**Branch isolada:** `qa/r12-arm64-homologacao-v3.277.81`, criada a partir da `qa/homologacao-32-v3.277.80`.

## Mudanças exatas
1. **Versão:** `VERSAO = "v3.277.81-QA-ANDROID-RC"`, Buildozer `version = 3.277.81`, `android.numeric_version = 327781`. Arquitetura Android continua exclusivamente `arm64-v8a`.
2. **Telemetria R12 automática:** `QATelemetria` existente continua no caminho real do loop e exporta, periodicamente e ao encerrar, `pixelrush_qa_v327781_r12.json` e `pixelrush_qa_frames_v327781_r12.csv` no diretório privado externo do app (`pixelrush_qa/`). Exportação JSON/CSV fora do frame via worker e snapshots parcelados existentes.
3. **JSON:** FPS estimado por intervalo entre quadros, percentis p50/p95/p99 de tempo total, trabalho sem limitador, CPU de processo, simulacao, mundo 2.5D, renderização, pós-sprites, passes R11, zoom, apresentação, memória RSS e picos. Agrupamento por modo e bioma; contagem de travamentos acima de 33, 50 e 100 ms.
4. **CSV por quadro:** mantidos os sete campos originais e adicionados apenas em R12 os campos `mundo_2_5d_ms`, `world_total_r11_ms`, `pos_sprites_ms`, `pos_alertas_ms`, `pos_pets_ms`, `pos_efeitos_portais_ms`, `pos_particulas_ms`, `pos_gamefeel_ms`, `pos_clima_ms`, `swap_cpu_ms`. CSV de versões antigas inalterado.
5. **Diagnóstico de backends realmente observados:** novo `pixelrush_qa_r12_v327781.py` reporta contadores de frames GLES, fallback SDL, uploads PBO, execução C/NEON, acertos de scroll incremental, GC, VSync solicitado via EGL e p50/p95/p99 do intervalo de swap do presenter. `gpu_ms_real` permanece `null`: não inferir tempo de GPU do `pygame.display.flip`.
6. **GC:** corrigida a etiqueta do diagnóstico para fase 2 (a política efetiva 30k+2 já existia). Nenhuma física, cena, RNG ou jogabilidade alterada.
7. **APK QA:** novo workflow isolado `.github/workflows/qa-r12-apk-debug-v327781.yml` com pré-gates pygame-ce 2.5.8/NumPy, compilação ARM64 C/NEON via NDK, alinhamento ELF/ZIP 16 KiB, auditoria DT_NEEDED, ZIP_STORED e empacotamento exclusivo `buildozer -v android debug`. Não executa `android release` ou `aab`.
8. **Regressões:** `tests/test_qa_r12_telemetria_v327781.py` cobre JSON/CSV real, CPU/FPS, passes, compatibilidade com export anterior, backend mock, ausência de dados privados; suíte de testes QA e arquivos de versão revisados.

## Preservação
Nenhuma alteração intencional no algoritmo de corrida, física, hitbox, shader, arte, som, save, pets, tutorial, `main.py`, DEV ou workflow AAB. O Buildozer mantém `android.release_artifact = aab` como configuração histórica; este workflow chama **somente** o target debug APK.

## Limites de homologação
- Pygame-ce Linux/Mesa e auditoria do APK **não substituem** driver Mali no A54.
- C/NEON apenas disponível na ABI ARM64 não prova ganho no jogo; o runtime mantém gate de pixels e custo.
- Nenhum gate Android físico ou 32/32 homologadas é aprovado antes do relatório R12 real no Galaxy A54.
- Não instalar um APK com assinatura debug diferente do anterior por meio de desinstalação: isso pode apagar os saves. Usar `adb install -r`; se houver conflito de assinatura, interromper e preservar o app instalado.

## Arquivos R12 esperados
Dentro de `/sdcard/Android/data/com.bigheadmobile_pixelrush/files/pixelrush_qa/` (se o Android liberar acesso pelo ADB):
- `pixelrush_qa_v327781_r12.json`
- `pixelrush_qa_frames_v327781_r12.csv`

A localização real vem de `getExternalFilesDir(None)` do app, não de um caminho adivinhado. O layout pode variar por dispositivo.
