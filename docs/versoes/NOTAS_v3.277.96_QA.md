# PIXEL RUSH v3.277.96-QA — R26: Cidade 2.5D, acabamento e organização

Branch isolada: qa/r26-both-performance-art-v3.277.96
Base estável: v3.277.95-QA, commit e0f350c37d2dc792bc93e6f2e7bfbc9be5796d69 (GitHub Actions #42081877479, SUCCESS).
Build Android: versionName 3.277.96, versionCode 327796; metadados somente, nenhum APK ou AAB gerado.

## Performance Cidade 2.5D
Novo candidato no pixelrush_city2_v3124.py: evitar enumerar tiles das camadas far e mid nos mapas NORMAL/FLOW somente se a auditoria opaca QA786 provar que near cobre integralmente cada pixel, com formato/identidade e ordem de camadas preservados. Mantidas as chamadas de iluminação, trem e vida urbana no IMAGE. Qualidade visual, colisoes e geometria intactas.

Flag PIXELRUSH_QA_R26_SKIP_OCCLUDED_LAYERS=0 até aprovar benchmark A/B e regressão pixel-exata; após comprovada, pode-se ativar por padrão com opt-out =0. Com PIXELRUSH_QA_CITY_OPAQUE_OVERDRAW=0 o mecanismo recua ao caminho original por falta do marcador de segurança. O script qa_a54/benchmark_city_skip_layers_v327796.py instrumenta 130 frames, 260 hashes RGBA, 26 quintos, p50/p95 por passe, limite do cache e contadores de enumeração das camadas. Não extrapolar Linux para 88,6ms históricos do Galaxy A54.

## Arte premium de sete biomas
Em src/pixelrush/rendering/material_friezes_v327794.py: pequenos traços de contorno nos materiais opacos near existentes, com intensidade máxima de 5/255, variação por bioma e fase fixa. São pintados uma vez ao carregar atlas, sem novo sprite, Surface, processamento a cada quadro ou variação de física, hitbox, alpha, material técnico, normal/flow/geometry. PIXELRUSH_QA_R26_EDGE_RIM=0 restaura somente a camada nova.

Reescrita da consulta aos quatro vizinhos na preparação para usar views NumPy em vez de oito np.roll grandes por atlas, com validação 35 casos RGB/RGBA idênticos à função R25 quando a borda é desativada; mais sete verificações de alfa preservado com contornos ativados. Preservar canais ocultos alpha 0, inclusive no teste, é obrigatório. Não representa reconstrução artística total.

## Organização
Mais seis módulos QA migrados para pacotes canônicos: gc_cooperative_v327757, hotpath_v327753, cache_policy_v327758, city/geometry_retire_v327761, rendering/scene_qa_v327733 e city/r11_passes_v327776. Wrapper histórico sys.modules mantém o objeto único; conteúdo canônico SHA/bytes idênticos à base QA792. O manifesto cobre 48 módulos no total, sendo 47 byte-idênticos à base e um (unified_post) intencionalmente otimizado com SHA fixo desde R25. Nenhum arquivo histórico removido.

## Pós-sprites e testes
Manter escala direta SDL RGB32, fallback seguro, replay pooled e paletas existentes. Workflow R26 testa os 60 hashes RGBA de apresentação, 288 amostras RGBA de replay, QA793 câmera, benchmark Cidade 240 buffers RGBA, teste tutorial e maratona dos sete biomas. Mais benchmark A/B do novo culling por camadas, incluindo modo sem auditoria para prova de fallback.

Preservados main.py, JOGAR.py, DEV, pets, saves, assets, física, controles, regras de spawn e workflows APK/AAB. Não compilar Android nem declarar gargalos de 64,7ms pós-sprites ou 88,6ms do mundo 2.5D resolvidos sem telemetria Galaxy A54/MEmu.
