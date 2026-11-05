# PIXEL RUSH v3.277.95-QA — R25: desempenho e acabamento/organização

**Branch isolada:** qa/r25-performance-arte-organizacao-v3.277.95
**Base estável:** v3.277.94-QA, commit a531cab1ba34b373c64298b75d98cc98875fa5c7 (CI #42076361960 SUCCESS)
**Metadados Android:** versionName 3.277.95, numeric_version 327795. Nenhuma compilação APK/AAB.

## 1. Pós-sprites — apresentação direta
src/pixelrush/performance/unified_post_v327750.py escala diretamente para a região do framebuffer SDL, sem Surface de tela inteira temporária e sem blit final adicional, apenas em RGB32 opaco, formato/máscaras iguais, sem SRCALPHA/colorkey/alpha parcial e com retângulo contido na tela. Erro SDL ou qualquer formato inesperado usa o caminho anterior.
- Rollback: PIXELRUSH_QA_R25_DIRECT_PRESENT=0.
- Mantidos o HUD, nearest-neighbor, proporção/letterbox, câmera, ordem dos efeitos, apresentação e limitador FPS.
- Medições locais isoladas Linux pygame-ce: 900x1600 p50 -46%; 1080x1920 com barras -36%; 360x640 -26%, com RGBA idêntico.
- Benchmark QA795 compara 6 cenários (3 RGB compatíveis, SRCALPHA, colorkey e sem escala), 36 quadros cada, 60 hashes RGBA por execução, counters reais e custo por caso. Somente ganhos em testes reprodutíveis autorizam integração, sem extrapolar FPS Android.

## 2. Mundo 2.5D — instrumento interno real
qa_a54/benchmark_city_internal_v327795.py: 120 quadros, 24 quintos, 240 hashes RGBA e métricas por passe image/fxmask/normal/geometry/material/flow. Instrumentação dos métodos render_scene, _render_chunk, _draw_sprite, _scaled_surface e cache de texturas scaled hits/misses (limite 20). Não altera gameplay nem motor; inclui perfis de 2.5D e mapas com qualidade Completa.
- Preservadas otimizações QA793/QA794 de preclear, FLOW e trem encoberto.
- Os 88,6ms do quinto quadro e 64,7ms pós-sprites do A54 seguem sem comprovação de correção no aparelho.

## 3. Acabamento visual discreto dos sete biomas
O sistema existente aplicar_friso em src/pixelrush/rendering/material_friezes_v327794.py foi REUTILIZADO, não duplicado. Acrescenta microacentos fixos e específicos à tinta opaca da Cidade, Neve, Deserto, Vulcão, Floresta, Cidade Futurista e Ilhas Celestes.
- Só no carregamento dos tiles near; zero novas Surfaces ou passes por quadro, sem RNG, sem alterar alfa, posições, sprites, física, mapas técnicos ou colisões.
- Intensidade máxima de 3 canais RGB; prova de pixels limitados e preservação absoluta do alfa com teste para sete biomas e rollback.
- Coordenadas de broadcasting 1D no lugar de np.indices evita aproximadamente 450 KiB temporários por variante 225x250 durante inicialização e mantém a arte QA794 idêntica quando microacentos estão desabilitados.
- Rollback dos acentos: PIXELRUSH_QA_R25_ART_DETAILS=0; rollback de toda camada R24: PIXELRUSH_QA_R24_FRISOS=0.
- Acabamento artístico total ainda exige etapas adicionais, sem prometer conclusão integral.

## 4. Organização de módulos
Dois backends QA da câmera migrados byte-identicamente desde a base QA792:
- pixelrush_qa_camera_v327733.py -> src/pixelrush/performance/camera/backend_v327733.py
- pixelrush_qa_camera_native_auto_v327742.py -> src/pixelrush/performance/camera/native_auto_v327742.py

Wrappers com sys.modules na raiz mantêm compatibilidade e estado global único; carregamento nativo libpixelrush_camera_crop_v327741.so permanece inalterado. Manifesto e testes de SHA/import passaram de 40 para 42 módulos. Não remover entrypoints ou códigos que dependam de caminhos __file__/assets sem auditoria.

## 5. Gates e proteção
CI offline R25 verifica motor pygame-ce/AST, tutorial real, 42 imports, benchmarking de 2.5D, seis biomas modulares e City, sete materiais com alfa invariável, replay RGB 288 amostras e regressão de câmera.
Preservados main.py, JOGAR.py, DEV, pets, saves, física, controles, colisões, imagens, p4a-recipes, main e workflows Android. Nenhum APK/AAB compilado, sem alegação de ganho geral de FPS ou homologação A54/MEmu.


## R25 — rastreabilidade estrita da otimização pós-sprites
O módulo canônico unified_post_v327750.py foi migrado como byte-idêntico na QA794, mas na R25 recebeu uma alteração explícita. O manifesto mantém **41 módulos byte-idênticos** à base QA792 e **um módulo com alteração aprovada**, bloqueado pelo Git blob SHA 0bc183651a8f3d8f0281e581cb62a7bf70710f0d. CI verifica o SHA exato, import como mesmo módulo e as 60 amostras RGBA do benchmark. Não representar esse módulo como byte-idêntico após a otimização.

### CI — contador de diagnóstico da escala direta
O primeiro CI R25 identificou KeyError de escala_direta no benchmark por ausência da chave inicial e do reset. Corrigidos exclusivamente os contadores estatísticos, sem alteração do algoritmo RGB. SHA canônico de auditoria atualizado para cee6487af8cde079b825dac701c4976d71326ae5.

### CI e correção final do profiler
GitHub Actions #42081558998: SUCCESS, escala RGB direta 60 hashes RGBA iguais, p50 900x1600 -52,0% e 1080x1920 -44,3%; cache/replay/módulos/arte também passaram. Quinto quadro City p50 Linux 3,21186ms; sem prova no A54. Ajustada apenas a posição do argumento map_kind em _draw_sprite para indexar corretamente as métricas de image/fxmask/geometry/material, sem tocar no código do jogo.
