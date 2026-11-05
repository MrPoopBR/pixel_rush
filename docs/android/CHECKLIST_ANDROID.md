# Pixel Rush Android — checklist de habilitacao (nao homologado)

**IMPORTANTE:** ESTE ZIP NAO CONTEM APK OU AAB; e uma versao candidata Android.

1. Escolha o identificador definitivo do aplicativo em `package.domain` e `package.name` (nao use `org.exemplo.substitua`). Confira o `versionCode` no Google Play Console e configure um numero *maior* que o publicado.
2. Utilize Linux com JDK 17, Android SDK 36, NDK r28c (ou atualizado e suportado pelo python-for-android) e Buildozer/p4a atualizados; configure a receita ARM64 especifica de **pygame-ce 2.5.8**, cuja disponibilidade **nao foi comprovada**. A recipe de pygame antiga nao equivale a pygame-ce moderno.
3. Gere primeiro APK debug no ambiente de compilacao, abra o jogo em ARM64 e verifique `pygame.version.ver` e as dependencias (NumPy, PyJNIus). Confirme que a vinculacao SDL2 de pygame nao conflita com SDL2 do bootstrap.
4. Valide ARM64 com APK Analyzer. Inspecione todas as `.so` com readelf/llvm-readelf e os segmentos ELF em multiplos de 0x4000; execute `zipalign -c -P 16 -v 4 app.apk`.
5. Use emulador ou aparelho configurado para paginas de 16 KB: `adb shell getconf PAGE_SIZE` deve retornar `16384`; rode tutorial, quatro biomas, saves e suspender/retomar.
6. Os shaders desktop GLSL 330 nao sao OpenGL ES; `PIXELRUSH_GPU=off` preserva o fallback Pygame original. Se quiser shaders acelerados no Android, sera preciso portar e validar separadamente (nao incluido nesta candidata).
7. `pygame.system.get_pref_path` e usado para salvar no diretorio privado persistente. Teste reinicio, forcar parada, atualizacao de APK, backups, permissao e uninstall/reinstall. Nenhuma migracao de saves antigos foi adicionada.
8. Avalie FPS, RSS/PSS, LMK, bateria, tempo de transicao, 16 KB, DPI/notch e entrada multitouch em aparelho real; o limite de 400 MiB comprovado em Linux nao vale automaticamente em Android.
9. Confira licencas dos TTF e demais recursos; nao presuma direito de redistribuicao.
10. Gere AAB release, assine com chave sob seu controle, teste em track interno, revise politicas e ficha da Play. Nao inclua sua chave dentro do ZIP.

Refs oficiais: https://developer.android.com/guide/practices/page-sizes e https://support.google.com/googleplay/android-developer/answer/11926878?hl=en
