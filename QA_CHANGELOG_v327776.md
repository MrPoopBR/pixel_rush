# PIXEL RUSH v3.277.76-QA — R11 Galaxy A54, pós-sprites e 2.5D

**Escopo:** branch isolada `qa/r11-passes-v3.277.76`, base `qa/a54-fechamento-32-v3.277.75`. Não compilar APK/AAB. `main.py`, main, DEV, saves, física, tutorial, pets e assets permanecem inalterados.

## Evidência original R11 (hardware Galaxy A54 SM-A546E)
- Dois ZIPs reais de 04/11/2026; SHA-256 guardado em `qa_r11_a54_baseline_v327776.json`. ZIP tutorial isolado sem JSON/CSV; quadros de tutorial constam no CSV posterior.
- Corrida Cidade: 1.380 frames, 8,3 FPS estimados, frame p50 100,619 ms / p95 198,842 ms.
- Pós-sprites p50 **64,668 ms**, p95 73,936 ms: inclui alertas, pets, efeitos, partículas, GameFeel e transições. Causa detalhada de cada subpasse **ainda não medida no A54**.
- Mundo 2.5D p50 **88,631 ms por execução**, p95 126,448 ms, 297 amostras; composição interna p50 24,758 ms; world draw p50 65,426 ms. Não somar blocos inclusivos.
- GPU Mali-G68 identificada, mas sem timer real de GPU e PBO desligado.

## Código alterado de forma direcionada
1. **Vinheta GameFeel (intervenção comprovável):** `pixelrush_qa_r11_vinheta_v327776.py` substitui um blit RGBA de 450×800 por quatro regiões disjuntas somente no destino RGB32 opaco real da corrida. A área central é testada em C/SDL uma única vez com máscara de alfa: todos os pixels do centro devem ter alfa zero. Não muda cor, intensidade, coordenadas, efeito, ordem, jogabilidade ou física. Sem paridade assegurada, e sempre em destino SRCALPHA com RGB oculto, usa **exatamente o blit original**. Rollback: `PIXELRUSH_QA_R11_VINHETA=0`. Somente QA Android.
2. **Instrumentação de pós-sprites:** marcador original preservado, seis regiões observacionais para alertas, pets, efeitos/portais, partículas, frente/GameFeel e clima/transições, com GameFeel e vinheta medidos adicionalmente por dentro (inclusive).
3. **Instrumentação interna 2.5D:** `pixelrush_qa_r11_passes_v327776.py` instala 13 wrappers observacionais somente após os demais hooks: mundo total, cena, debris, City total/chunk/scale/train e City Life ponte/cabos/pombos/janelas/atmosfera/reflexos. Todas as chamadas, exceções e o retorno original são preservados, com rollback de wrappers para testes. Desligar com `PIXELRUSH_QA_R11_PASS_TRACE=0`.
4. **Telemetria:** campos R11 adicionados a `pixelrush_qa_android_v327728.SECOES`, com quantis por grupo modo/bioma. Campos são tempos **inclusivos**, sem somá-los a seus pais.
5. **Versão:** engine `v3.277.76-QA-ANDROID-RC`; `buildozer.spec`: `version = 3.277.76`, `android.numeric_version = 327776`.

## Gates e status
- Testes pygame-ce SDL dummy: paridade RGBA do GameFeel real no destino RGB32; fallback byte-exato de SRCALPHA incluindo RGB oculto; origem inesperada, rollback e benchmark de 350 quadros.
- Testes de cena City/LivingWorld real RGB e RGBA e restauração de hooks R11.
- Suíte offline QA A54 da v775 portada para versão v776 com gates SHA para `main.py` e módulos imutáveis; manter workflows pré-existentes intactos.
- **Ganho medido local em um microbenchmark do blit de vinheta: aproximadamente 1,7×, não significa 1,7× de FPS.** Pygame-ce 2.5.8 Linux SDL dummy; sem prova de impacto na Mali/CPU A54.
- Não há otimização de mundo 2.5D ainda com melhoria integral e paridade comprovadas; o novo perfil detalha exatamente onde agir na próxima rodada após R12. Proibido reduzir visual/alterar período do quinto quadro por suposição.
- **22/32 offline e 10/32 parciais**, sem homologação final das 10 no A54. Corrida R12 necessária para quantificar e decidir promoções.
- Não foi compilado APK nesta atualização. O APK v3.277.75 instalado no A54 permanece inalterado; não reinstalar ou apagar saves para coletar a evidência antiga.


## Revisão final do gate 2.5D e evidências CI

- **Composição da Cidade 2.5D, melhoria integrada:** `pixelrush_qa_r11_world_bounds_v327776.py` e alteração QA condicional em `pixelrush_world_v3130.py`. Apenas para **Cidade + destino RGB16 opaco**, `pygame.Surface.get_bounding_rect(min_alpha=1)` identifica o retângulo com algum alfa; desenha apenas essa região da cena no destino original. Os pixels, o cenário e a ordem de demais operações permanecem iguais. `RGB24`, `RGB32`, destino `SRCALPHA` (inclusive RGB oculto), colorkey, cena de outro bioma ou superfície incompatível usam exclusivamente o `surface.blit(layer,(0,TOP))` original. Rollback no QA: `PIXELRUSH_QA_R11_WORLD_BBOX=0`.
- **Prova real da textura City em pygame-ce:** `tests/test_qa_r11_world_bands_v327776.py` renderiza 3 condições de noite/clima da Cidade, com 9 combinações formato/condição. Nas 3 cenas **22,8% das linhas** estavam transparentes; ROI sem detecção aumenta a velocidade do blit isolado em ~1,10–1,30×. Medindo **bbox + blit juntos**, RGB16 melhora **1,146–1,148×** (~14,6–14,8% mais rápido no blit). RGB24 piora (~0,93×), RGB32 piora muito (~0,20×), por isso esses formatos são **vetados pelo gate**.
- **Teste de render 2.5D realmente integrado:** `tests/test_qa_r11_world_bounds_v327776.py`, 3 testes, compara `LivingWorld.draw` em Cidade, leve/normal, climas limpo/chuva/tempestade, alfa de destino 0/1/99/255 e 16/24/32/RGBA, com paridade **byte-a-byte RGBA** inclusive RGB oculto no alpha=0 e fallback intacto para outros biomas.
- **Vinheta GameFeel ampliada:** gate para RGB16, RGB24 e RGB32 opacos, com fallback SRCALPHA, colorkey, geometria diferente ou máscara inesperada. Paridade byte-exata RGB/RGBA oculto nas 4 classes de superfície. Benchmark da vinheta real no CI final: **1,995×** mais rápido no passe isolado, sem alegação de ganho equivalente no frame completo.
- **CI final comprovado:** [offline #41896813021](https://github.com/MrPoopBR/pixel_rush/actions/runs/41896813021) passou **134/134 testes, 36 grupos**, SDL dummy pygame-ce 2.5.8. [GPU Mesa #41896812974](https://github.com/MrPoopBR/pixel_rush/actions/runs/41896812974) passou 720 cenários GLES2/3, 288 imagens reais Cidade/Neve e 6 cenários PBO. Esses gates são offline e não avaliam a Mali do Galaxy A54.
- **Impacto real R12 ainda NÃO medido:** o hardware pode renderizar o mundo em RGB32 e, nesse caso, a segunda otimização não é ativada. Mesmo quando ativa, 1,148× se refere **somente ao blit final da cena**, não aos 88,631 ms da renderização inteira. Os 13 cronômetros adicionados são a evidência necessária para localizar os 65 ms do mundo antes do blit. Sem alteração da cadência de 5 quadros.
- **Proteção:** apenas a branch QA. Saves, física, aparência, jogador, gestos, tutorial, pets, shaders, colisões, `main.py`, DEV e workflow AAB de publicação não foram alterados. Nenhum APK/AAB compilado nesta versão; a instalação v3.277.75-QA do Galaxy A54 permanece intocada. **22/32 offline concluídas, 10/32 parciais, sem homologação das dez pendências no A54.**
