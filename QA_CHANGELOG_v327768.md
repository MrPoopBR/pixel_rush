# PIXEL RUSH — Changelog v3.277.68-QA

Mesma branch isolada qa/fechamento-32-v3.277.57, base v3.277.67.

**#24**: módulo `pixelrush_qa_city_intern_v327768.py` introduz deduplicação de atlas técnicos *imutáveis* da Cidade já finalizados, inclusive entre diferentes instâncias de LivingWorld. Garante igualdade por tipo, dimensões, pitch, SDL flags, masks, alpha, digest BLAKE2b e bytes completos do buffer. Usa WeakValueDictionary para não reter cenas/Surfaces aposentadas e mantém estado de animação, imagens e instâncias separados. Instalação automática no wrapper QA do bootstrap da Cidade antes da criação dos índices estáticos. Desliga via PIXELRUSH_QA_CITY_GLOBAL_INTERN=0.

Novos 3 testes em tests/test_qa_city_intern_v327768.py cobrem RGB oculto na transparência, duas Cidades reais em 6 canais RGB/RGBA e fallback/weakrefs. Status da nova suíte ainda sujeito ao CI. #25 orçamento agregado de cache é considerado implementado e validado offline após execução CI #41727086275 sucesso 44/44 testes; **não afirmar limite absoluto RSS Android nem FPS**. Placar de código offline 20/32 completas, 12 parciais, 0 homologadas em Android.

Versão da engine QA e Buildozer sincronizadas sem compilar Android; não alterados main.py, produção, DEV, assets, sprites, câmera, física, controles, pets, saves, tutorial, efeitos, áudio ou workflows APK/AAB.
