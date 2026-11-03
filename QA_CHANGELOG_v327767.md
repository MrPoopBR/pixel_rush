# PIXEL RUSH — Changelog QA v3.277.67

Mesma branch de fechamento, base v3.277.66. Adicionado descarte seguro de `LivingWorld._qa_damage_layer` de 450×500 bytes RGBA quando o SDF não contém chunks de dano. A Surface usada durante dano permanece protegida; remoção apenas por limpeza parcelada ou RSS fallback após apresentação, nunca durante render ou no quinto quadro. Contagem integrada no inventário de Surfaces, sem duplicações. Rollback do escalonador e orçamento anterior permanece.

Testes: 3 gates novos `tests/test_qa_damage_memory_v327767.py` de inventário, SDF ativo/inativo e fallback RSS, além dos 41 gates v766. Resultado do CI ainda pendente antes de qualquer promoção da frente #25. A execução v766 #41726342467 passou 41/41 testes Pygame offline, validando RNG, sprites e RGBA do pooling de explosões/ambiente; #20 concluída no critério de implementação e teste offline. Placar vigente ao registrar: 19/32 offline, 13 parciais, 0 homologadas Android.

Sem APK/AAB, Android, merge main, alteração DEV, arte, física, efeitos, pets, saves, tutorial, controles ou workflows de produção. Motor QA alterado apenas na string de versão.
