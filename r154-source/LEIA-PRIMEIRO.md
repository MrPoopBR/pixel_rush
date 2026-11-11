# PIXEL RUSH R154 — APK debug por GitHub Actions

Este ramo é **isolado**. Ele não altera `main`, não publica AAB e não utiliza a chave da Play Store.

## Alternativa mais simples: envio automático pelo Windows

No ChatGPT, baixe **PIXELRUSH_R154_ENVIAR_GITHUB_UM_CLIQUE.zip**, extraia-o e dê dois cliques em **ENVIAR_E_COMPILAR_R154.bat**. O script verifica SHA-256 de todas as partes, usa Git for Windows e envia somente os quatro arquivos para esta branch. Se necessário, a autenticação do GitHub abre no navegador.

**O ChatGPT não consegue transferir diretamente os 38 MB de binários pelo conector conectado. O workflow ainda depende desse envio.** Nenhum APK existe antes da compilação concluída.

## Para iniciar a compilação

1. Baixe `PIXELRUSH_R154_PARTES_UPLOAD_GITHUB.zip` no ChatGPT e extraia no seu computador.
2. Abra a pasta [r154-source neste ramo](https://github.com/MrPoopBR/pixel_rush/tree/build/r154-debug-327906/r154-source).
3. Clique **Add file → Upload files**; envie os quatro arquivos `r154-source.part01`, `part02`, `part03` e `part04` **juntos**, diretamente neste ramo.
4. Confirme o commit. O workflow [R154 — APK DEBUG ARM64](https://github.com/MrPoopBR/pixel_rush/actions) deverá iniciar automaticamente.
5. Na execução, procure o artifact `PIXELRUSH_R154_APK_DEBUG_ARM64`. Caso falhe, baixe `PIXELRUSH_R154_BUILD_LOGS`.

O workflow só usa o ZIP cujo SHA-256 seja `2a27e23a55142b8ce1f707794be302f8470015f10591449c9a031f84396e47e9`.

**Não** envie saves, senha, chave de assinatura ou AAB. O APK debug é apenas para teste Android (instalação limpa). A compilação em GitHub Actions depende de Buildozer/p4a e pode falhar; sucesso e fluidez só serão afirmados depois da execução e dos testes no dispositivo.
