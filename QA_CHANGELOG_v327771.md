# PIXEL RUSH v3.277.71-QA — câmera adaptativa e regressão do tutorial de letras

**Branch isolada:** qa/fechamento-32-v3.277.57. **Escopo:** desempenho da câmera e diagnóstico do fechamento na sexta lição. Não alterar arte, física, input, textos, colisão, word gameplay, saves, pets, main, DEV ou AAB.

- O gate de câmera existente agora testa também o backend `GENERIC` quando o Android reporta `NEON`, relevante para a tradução ARM64→x86_64 do MEmu. Duas verificações de pixels em tamanhos independentes e mediana de quatro pares de tempo. Só troca com igualdade da imagem de teste e ganho >=20% e >=0,10ms; caso contrário SDL original. `PIXELRUSH_QA_CAMERA_AUTOTUNE=0` desativa. Executa uma vez no boot Android QA, ANTES do loop, sem autotune por frame.
- Captura picos da câmera, zoom e resolução em contadores, sem cópia de imagens nem I/O por quadro; telemetria `camera_backend_autotune_qa` já integrada.
- Nova regressão pygame-ce baseada na implementação v3274 real, percorrendo coleta de PIXEL e transição para corrida, sem modificar lógica das letras. Não é prova de que o crash Android foi corrigido.
- **Crash nas letras v70**: R8 perdeu traceback por `logcat --pid` inválido; coletor Windows R9 separado registra logs sem PID e troca de processos. NÃO atribuir causa ao jogo sem traceback.
- R8: menu fundo p50 68,3ms (15 amostras); 2.5D tutorial p50 93,4ms (17); câmera p50 0,072ms/p95 160,862ms (111). No MEmu virtual x86_64 com ARM64 traduzido. Sem evidencia de equivalência/ganho para ligar GLES/scroll/PBO. Status das 32 frentes permanece **22 offline / 10 parciais / 0 homologadas ARM64 físico**.
- Nenhum APK/AAB ou hardware aprovado sem execução real do CI/Android.

### Gate adicional de paridade na mesma v3.277.71

Incluído vetor determinístico 37x53 em RGB opaco e SRCALPHA com canais RGB ocultos sob alfa zero, escalado para 43x61 por backend. Reprova qualquer diferença byte RGBA antes da seleção/benchmark. Padrões RGB+RGBA de estresse detectaram divergência SSE2/GENERIC em pygame-ce 2.5.8 Linux; este caso não deve ativar backend alternativo. Não altera visual nem física.
