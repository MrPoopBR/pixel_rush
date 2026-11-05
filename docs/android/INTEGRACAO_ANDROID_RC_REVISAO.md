# Integração PIXEL RUSH v3.277.11-PROD-ANDROID-RC — SOMENTE REVISÃO

**STATUS: INCOMPLETA. NÃO MESCLAR / NÃO PUBLICAR / NÃO INICIAR BUILD ASSINADO.**

Este branch `integracao/android-rc-v3.277.11-revisao` nasceu de `main` e preserva o código antigo do jogo, que continua em **v3.9.1**. A candidata v3.277.11-PROD-ANDROID-RC ainda **NÃO foi enviada integralmente** ao GitHub. Esta revisão entrega somente os arquivos de compilação e o mecanismo que **bloqueia** a assinatura se o pacote RC não estiver sincronizado.

## Ajustes propostos (sem mudar jogabilidade)

1. `buildozer.spec`: conserva `package.domain=com` e `package.name=bigheadmobile_pixelrush`, define `version=3.277.11` e um **numeric_version provisório** (327711), API 36, NDK 28c, min/NDK API 26, ARM64 e os formatos de recursos `.atlas,.pbuf,.tiles,.rgbaz,.pcmz,.png,.ttf`; adiciona NumPy às dependências.
2. `p4a-recipes/pygame-ce/__init__.py`: usa a receita experimental para pygame-ce 2.5.8, com SDL2, alinhamento máximo de páginas 16 KiB nas extensões próprias e módulo `pygame.system` para saves. **Não compilada em Android real**.
3. `.github/workflows/build-aab.yml`: verifica antes dos secrets que os principais arquivos da RC existem e batem com hashes conhecidos. Mantém disparo exclusivamente manual, restrição ao `main` e assinatura por secrets. Alinha a checagem de NumPy e Python/hostpython 3.12.12.
4. Nenhum arquivo de shaders, física, hitboxes, gameplay, fontes, moedas ou saves da versão PROD foi reescrito aqui.

## Bloqueios e itens de revisão

- **Fonte da RC ausente no GitHub:** devem ser sincronizados o `main.py` de entrada Android, `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py`, módulos auxiliares e todos os assets do ZIP da candidata (505 arquivos). Não copie os scripts experimentais de QA ou arquivos locais de assinatura.
- **Identidade Play:** o package ID existente `com.bigheadmobile_pixelrush` foi preservado; CONFIRMAR o applicationId da Play Console antes de qualquer publicação.
- **Versão Play:** `android.numeric_version=327711` é provisório; confirmar se é maior que todos os versionCodes já publicados.
- **Python/NumPy:** a receita upstream NumPy em `p4a/develop` aponta para NumPy 2.3.0, que precisa Python 3.11+. Foi proposta a dupla `python3==3.12.12,hostpython3==3.12.12`; compilação cruzada **não testada**.
- **Reprodutibilidade:** `p4a.branch=develop` é mutável; fixar revisão commit conhecida após validar a toolchain.
- **16 KiB:** testar cada `.so` ARM64 com `readelf`/verificador ELF; APK com `zipalign -c -P 16 -v 4`; AAB com `bundletool dump config` e `PAGE_ALIGNMENT_16K`.
- **GLSL:** shaders OpenGL 3.3 não estão homologados para OpenGL ES; caminho Pygame permanece preferível até testes em celular.
- **Assinatura:** jamais fazer commit do keystore, senhas, variáveis secretas ou log sensível. Não executar workflow manual assinado antes da revisão.
- **Limite operacional desta integração:** somente arquivos UTF-8 pequenos de configuração foram enviados pelo conector GitHub. Os recursos binários da RC não foram carregados por ele.

## Validação esperada antes de remover o bloqueio

Sincronizar integralmente a RC; comparar arquivos com ZIP original; testar a receita p4a com SDK 36/NDK r28c; compilar **APK debug primeiro**; inspecionar todas as libs nativas/16 KiB; testar tutorial, saves, quatro cenários, toque, áudio e RAM em Android; somente então considerar AAB assinado em `main`.

**Versionamento do PIXEL RUSH:** sem nova versão; esta revisão altera somente a preparação de integração. O ramo DEV não é modificado.
