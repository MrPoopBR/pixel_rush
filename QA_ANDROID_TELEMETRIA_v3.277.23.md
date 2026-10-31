# PIXEL RUSH QA Android v3.277.23 — instrumentação isolada

Branch: \`qa/android-telemetria-v3.277.23\`
Pacote Android independente: \`com.bigheadmobile_pixelrush_qa\`.
Não compartilha o caminho de saves da produção; não muda física, sprites, UI,
shaders, efeitos, controles ou ritmo. Instalação apenas para QA interno.

Ao iniciar:
- PIXELRUSH_PROFILER=1; amostragem a cada 5 frames; \`profiler/profiler_v3204_LIMPA.json\`.
- PIXELRUSH_PERF_BIOMAS=1; captura cada frame JOGANDO; \`perf_biomas.json\`.
- PIXELRUSH_DIAGNOSTICO=1; média, picos 33/50/100 ms, RSS; \`diagnostico.json\`.
- Dados dentro de \`ANDROID_PRIVATE/qa_desempenho_v327723/\`; reporte caminho em logcat
  via \`PIXEL_RUSH_QA_PERF_PATH\`.
- Monitor de biomas salva a cada 900 frames JOGANDO, e ao fechar normalmente;
  profiler v3204 salva a cada 1.200 frames; diagnostico v3154, a cada 600.
- Não use a telemetria como FPS sem interferência; compare com uma build
  sem instrumentação no mesmo aparelho, mesmas opções e cenários.

Plano de reprodução:
1. Instale apenas APK debug QA obtido do workflow de QA desta branch.
2. Corrida de 5 minutos, sem extras, em cada aparelho/emulador.
3. Repetir corrida com efeitos altos, chuva e transição cidade/deserto/neve.
4. Guardar 3 execuções; medir p50/p95/p99 e pior frame, RSS e picos por bioma.
5. Inspecionar \`adb logcat\` pelo marcador QA e copiar os JSON usando \`run-as\`
   para o pacote QA ou Android Studio Device Explorer. Caminhos podem variar.
6. Não aprovar produtividade nem ganho de FPS sem logs coletados.

Workflow: \`.github/workflows/build-apk-qa-perf.yml\`. Somente debug APK;
sem AAB, sem assinatura release, sem alterações em produção ou DEV.
