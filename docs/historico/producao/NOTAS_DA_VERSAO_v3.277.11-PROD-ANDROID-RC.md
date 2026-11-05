# Notas — Pixel Rush v3.277.11-PROD-ANDROID-RC (CANDIDATA, nao homologada)

Base: v3.277.10-PROD, preservada integralmente no ZIP original. Criada somente uma copia para investigacao Android.

## Alteracoes estritamente necessarias
- Novo `main.py` para entrada esperada pelo bootstrap SDL2 do python-for-android.
- `ARQUIVO_SAVE` no Android passa a usar `pygame.system.get_pref_path(...)` em vez de caminho relativo; desktop continua **exatamente** igual. Sem alterar dados, politica transacional ou backups.
- Identificador de versao da candidata e launchers atualizados.
- `buildozer.spec.template` experimental com API 36, ARM64 e artefato AAB; NAO significa receita C-extension validada.
- Checklist e testes de compatibilidade; nenhum som, textura, shader, fisica, hitbox ou recurso de gameplay alterado.

## Bloqueios
- Ainda nao foi gerado nem assinado APK/AAB; Android SDK/NDK/Buildozer ausentes no ambiente auditor.
- Compilacao de pygame-ce 2.5.8, NumPy e PyJNIus em ARM64 com paginas de 16 KB nao demonstrada.
- Contexto OpenGL ES e sensores/touch/haptics nao testados em Android fisico.
- Sem garantia de armazenamento persistente ate execucao no aparelho.
- Candidato **nao deve substituir** a v3.277.10-PROD aprovada em Linux ate homologacao.
