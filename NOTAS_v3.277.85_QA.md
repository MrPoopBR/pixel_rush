# PIXEL RUSH v3.277.85-QA — R15 Cidade 2.5D / quinto quadro
Data: 5/11/2026
Branch: `qa/r15-city-fifth-cache-v3.277.85`
Base: v3.277.84-QA — commit `3ff714a6b7182d56e7ace7b74c6ad1961f801547`

## Problema demonstrado
O LRU `CityPilotScene._scaled` tinha capacidade de 14 superficies 900×500 RGBA.
O mundo utiliza a imagem principal + `fxmask`, `normal`, `geometry`, `material`
e `flow` no redesenho periódico do quinto quadro. Com 14 entradas o LRU
repetidamente expulsava mapas ainda necessários, recomputando escalas
`pygame.transform.scale` no quinto quadro e os atlas de imagem logo depois.

## Alteracao integrada
Somente no bootstrap QA da Cidade, `pixelrush_qa_city_scaled_budget_v327785.py`
aumenta o teto de 14 para **20** entradas, respeitando LRU, formato de pixel,
identidade de atlas e trim original para cenas inativas. Nenhum cache de sprites,
técnicas gráficas, coordenadas de scroll, frames, física ou visuais é alterado.
Caso a capacidade preexistente seja diferente de 14, nenhuma mudanca e aplicada.
Rollback: `PIXELRUSH_QA_CITY_SCALED_BUDGET=0` antes do bootstrap da QA.
Aumento máximo teórico de armazenamento: 6×900×500×4 = 10.800.000 bytes,
equivalente a 10,30 MiB. RSS real observado em Linux: +2.196 a +2.752 KiB
nas duas variantes da bateria, nao sendo previsao para Android.

## Comprovacao pygame-ce 2.5.8 (GitHub Actions Linux)
`LivingWorld('cidade')` e `CityPilotScene v3125`, 130 quadros por perfil;
mapas tecnicos `fxmask`, `normal`, `geometry`, `material` e `flow`
desenhados a cada quinto quadro (26 redesenhos por perfil), incluindo
qualidade normal/leve, dia/chuva/tempestade, alpha, travessia de chunks.
Comparados integralmente **260 buffers RGBA por perfil**, todos idênticos.
- Falhas de cache (imagem + mapas): **435 → 25** em ambos os perfis.
- Mundo completo, quinto quadro, p50: normal **9,9036 → 6,9424 ms** (29,90%).
- Mundo completo, quinto quadro, p50: leve **9,7083 → 6,8895 ms** (29,03%).
- P95 normal: **11,7727 → 7,7165 ms**.
- P95 leve: **11,4850 → 7,9230 ms**.
O tempo contabiliza `world.draw` + cinco mapas, nao apenas uma micro-rotina.
Os valores medidos se aplicam ao CI Linux, **não são FPS do Galaxy A54**.
`tests/test_qa_r15_city_fifth_budget_v327785.py` exige
hashes RGBA idênticos, >=70% menos misses e >=10% de ganho p50,
com cap de memoria e rollback testados.
`qa_a54/benchmark_city_fifth_v327785.py` gera evidências por perfil.
O CI isolado `.github/workflows/qa-r15-city-fifth-v327785.yml` não tem
etapa Android/APK/AAB.

## Fora do escopo / preservacao
`main.py`, DEV, AAB, assets, sprites, skins, luzes, shaders GLES, desempenho
de outros biomas, saves, pets, tutorial, física, velocidades e jogabilidade
não foram alterados. No arquivo `PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py`
mudou **apenas a string VERSAO**. `buildozer.spec` teve somente número de
versão e código numérico ajustados; nenhuma compilação foi solicitada.
A v3.277.85-QA **não está homologada no A54**: validar FPS, RSS e P95 reais
com JSON/CSV depois de um APK solicitado explicitamente.
