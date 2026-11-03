# PIXEL RUSH — Tracker auditado das 32 melhorias (v3.277.46-QA)

**Fonte inicial:** `QA_AUDITORIA_32_v327738.md`; reavaliação com código até v3.277.45 e ensaios de v3.277.46.  
**Critério:** *concluída no código/QA offline* significa técnica presente e com testes focados; **não implica FPS Android comprovado nem todas as 32 homologadas**. *Parcial* significa atuação limitada a alguns cenários, flag OFF, falta de teste integral ou pré-carregamento não integrado; *pendente* significa proposta ainda não integrada ao render real.

**Resultado: 12/32 concluídas em código/QA offline (37,5%); 15/32 parciais (46,875%); 5/32 pendentes (15,625%). Total 32/32.**
**Homologação de ganhos em aparelho Android para esta versão: 0/32 novos gates comprovados na v3.277.46.**

| # | Melhoria das 32 | Estado | Evidência e ressalva |
|---:|---|---|---|
|1|Zoom por GPU|Pendente|GLES experimental OFF; nenhuma prova no Android|
|2|Compositor 2.5D persistente|Parcial|surfaces/caches reutilizados; redraw de fundo a cada 5 quadros ainda custoso|
|3|CPU/GPU híbrido|Pendente|caminho GPU não homologado|
|4|Unificação zoom/posprocessamento|Pendente|independentes, preservar comportamento|
|5|Scroll incremental de pixels|Pendente|pré-ensaio desligado por padrão; cache temporal não equivale a scroll|
|6|Recorte de transparências|**Concluída (offline)**|wrapper Fase B; culling RGBA testado|
|7|Evitar grandes alocações|Parcial|buffers reutilizados em SDF/profundidade, outros temporários|
|8|SIMD para smoothscale|Parcial|preflight offline/opt-in, fallback ativo, sem Android|
|9|Pré-composição de texturas|**Concluída (offline)**|atlas e superfícies estáticas presentes, testes de paridade|
|10|Remover cópias/passes|Parcial|algumas removidas; cópia para cache do quinto quadro permanece|
|11|Cache de menus|**Concluída (offline)**|fundo e prévias limitados, sem remoção de UI dinâmica|
|12|Backend por dispositivo|Parcial|sondas, autodetecção incompleta; GPU OFF|
|13|Sprites espelhados|**Concluída (offline)**|cache de props integrado|
|14|Alpha overlays|**Concluída (offline)**|reuso de masks/transições implementado|
|15|FABRIK/deformação|**Concluída (offline)**|buffers QA integrados e limitados|
|16|Culling fora da tela|Parcial|várias camadas; cobertura integral não comprovada|
|17|Agrupar blits|**Concluída (offline)**|Fase B/SDF/strips; modular atual opcional OFF, sem afirmar ganho dele|
|18|Cache céu/clima|Parcial|alguns caminhos reais não usam a otimização de `_weather`|
|19|Vinheta noturna|**Concluída (offline)**|cache de faixas 12 entradas em v3192|
|20|Pool chuva/neve/partículas|Parcial|algumas famílias, sem cobertura para todos os climas|
|21|Fontes/labels|**Concluída (offline)**|caches limitados com atualização por necessidade|
|22|Pré-carregamento skins/pets|Parcial|previews e caches existentes, pets não validados integralmente|
|23|Pré-aquecer biomas|Parcial|**atlas PROD já integrado**; API v746 apenas fora da corrida, sem disparo automático|
|24|Deduplicar Surfaces|Parcial|algumas duplicações eliminadas, não toda VRAM/RAM|
|25|Limites globais de cache|Parcial|LRUs e RSS, sem prova de pressão real Android|
|26|Pausas GC|Parcial|sonda existe, picos observados; não elimina pausas|
|27|Telemetria assíncrona|**Concluída (offline)**|worker JSON/CSV, snapshot parcelado, flush final preservado|
|28|Native/Cython seletivo|Parcial|câmera C/NEON experimental disponível, OFF até prova Android; sem Cython geral|
|29|Evitar uploads GPU|Pendente|depende GPU; PBO OFF|
|30|Apresentação final/SDL|**Concluída (offline)**|swap/cópias instrumentados; não comprova taxa de atualização Android|
|31|Atlas pré-aquecido|**Concluída (offline)**|atlas PROD SHA-256 verificados v32776 + tiles PROD v32777|
|32|VSync/driver/Perfetto|Parcial|sondas instrumentadas, Perfetto Android não coletado|

## Regra de aprovação definitiva
**A taxa 37,5% é de implementação/cobertura offline, NÃO uma taxa de otimizações validadas por desempenho no Android.** Para encerrar as 32 como pacote, falta a rodada única de homologação Android, mais gates de gameplay completo/performance/cadência. Não declarar resultados de testes de atlas base `world_v3130` como equivalentes a `world_prod_v32777`, nem confundir cenário Linux com frame real Android. Nenhum APK compilado nesta tarefa.
