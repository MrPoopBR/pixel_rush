# PIXEL RUSH v3.277.94-QA — R24: desempenho, acabamento e arquitetura

**Branch isolada:** qa/r24-duas-frentes-v3.277.94
**Base segura:** v3.277.93-QA, commit ee4fff6d6844e36c42d8b6fecbe58babca8eec9f (laboratorio A/B aprovado)
**Objetivo:** integrar apenas ganhos pixel-exatos e ampliar acabamento em atlases sem custo por quadro.

## 1. Mundo 2.5D — sem limpeza duplicada
- Em pixelrush_world_v3130.py, todos os seis mapas que o compositor de Neve e Deserto grava com pygame.transform.scale(low,(450,500),target) passam a dispensar o fill anterior em World._city_surface (foreground permanece intocado). Condicional limitado aos dois biomas e renderizadores conhecidos; PIXELRUSH_QA_MODULAR_ALL_PRECLEAR=0 oferece rollback para a politica anterior, que ja omitia apenas o normal.
- Laboratorio GitHub Actions #42073803819: 160 RGBA exatos. Ganhos p50 Linux por passe (Neve / Deserto): image -5,15%/-6,95%, fxmask -10,68%/-8,15%, geometry -7,96%/-7,93%, material -7,64%/-4,85%, flow -9,54%/-10,21%. Valores isolados e sujeitos a variacao. Nao comprovam melhoria de FPS Android.
- CI R24 acrescenta comparacao bloqueante entre experimento e metodo REAL, opt-out e maratona dos sete biomas sem diminuir a qualidade. Qualidade completa, escala, periodicidade do quinto quadro, GPU fallback e pixels RGBA preservados.

## 2. Pos-sprites — replay sem novas superficies apos aquecimento
- pixelrush_extras_v3174.py: apos preencher as 72 amostras do replay, reutiliza a Surface mais antiga do deque no mesmo formato RGB32 opaco, escrevendo a escala diretamente nela, preservando 225x400, ordem, amostragem a cada cinco ticks, seis segundos, congelamento e efeito final.
- Verifica formato, bits, alpha e colorkey; formato inesperado usa caminho historico. PIXELRUSH_QA_R24_REPLAY_RECYCLE=0 desativa a melhoria.
- Benchmark independente de 180 capturas verifica 288 hashes RGBA, 108 reutilizacoes no candidato e compara p50/p95. A RAM residente do replay permanece igual; evitam-se alocacoes repetitivas na coleta apos o cache cheio.
- Camera zoom otimizada na QA793, vinheta em bordas e passes meteorologicos preservados. Nenhum efeito removido; o diagnostico residual dos 64,7 ms no A54 segue aberto.

## 3. Acabamento artistico dos sete biomas
- Novo modulo src/pixelrush/rendering/material_friezes_v327794.py, integrado exclusivamente na preparacao dos materiais premium de cada bioma (City via pixelrush_world_v3185 e outros seis via pixelrush_biomes2_v3185). Frisos pixel-art curtos variam de espacamento, orientacao e intensidade entre Cidade, Neve, Deserto, Vulcao, Floresta, Cidade Futurista e Ilhas Celestes.
- Pintura restrita a pixels solidos, homogeneos e longe de bordas, maximo +/-5 de RGB, sem alterar alpha, sprite, hitbox, mapa de colisao, rotas, RNG, pose ou frame. Reaproveita as paletas noturnas ja existentes, sem alocar superficies extras no loop. PIXELRUSH_QA_R24_FRISOS=0 restaura o visual anterior.
- Teste direcionado de 7 materiais comprova que houve refinamento localizado, com bytes de alfa identicos e sem modificar planos mid. A imagem completa naturalmente difere da QA793 porque o polimento foi solicitado; os mapas tecnicos A/B permanecem pixel-exatos entre candidatos da mesma versao.
- Trata-se de polimento localizado, nao uma reconstrução artistica integral dos sprites e cenarios.

## 4. Organizacao e compatibilidade
- Migrados mais dois modulos: pixelrush_qa_unified_post_v327750.py -> src/pixelrush/performance/unified_post_v327750.py; pixelrush_qa_city_bootstrap_v327759.py -> src/pixelrush/performance/city/bootstrap_v327759.py.
- Conteudo canonico byte-identico a QA792 comprovado por SHA do GitHub; wrappers sys.modules preservam imports, estado global de instrumentacao e dependencia Android. Manifesto e gate de imports passam de 38 para 40 modulos. Nenhuma remocao na raiz, sem duplicar sistemas.
- Nova branch e CI QA794 sem modificar workflows Android/APK/AAB; alterados apenas identificador VERSAO do motor, metadados versionName/versionCode do buildozer, documentacao e arquivos de arte/performance previstos. main.py, JOGAR.py, DEV, saves, pets, assets e receitas Android protegidos.

## 5. Validacao e limites
- Requer SUCCESS do CI R24 completo para confirmar regressao sintatica, imports, memoria, rgba, replay, tutorial e sete biomas.
- Nenhum APK, AAB ou teste no Galaxy A54/MEmu foi realizado. Ainda nao se pode declarar travamentos ou 88,6/64,7 ms Android resolvidos, nem acabamento integral finalizado.
