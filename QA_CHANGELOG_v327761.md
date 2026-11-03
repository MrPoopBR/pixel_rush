# PIXEL RUSH — Changelog de integração v3.277.61-QA

Branch única: `qa/fechamento-32-v3.277.57`; base v3.277.60-QA.

**CPU/RAM #7/#10/#25:** novo módulo QA de descarte de alias `geometry` aposentado na troca de bioma, integrado ao instalador real de QA. Remove somente ponteiros da cena anterior após `LivingWorld.switch` limpar as Surfaces, e exclusivamente quando a ponte aponta para o buffer persistente anterior; não desaloca geometria ativa nem snapshots externos. Pode eliminar uma Surface RGBA 450×500 que ficaria retida por causa da referência `scene._geometry_view`. Rollback `PIXELRUSH_QA_GEOMETRY_RETIRE=0`.

**#18 Cache de céu e clima:** teste integrado sobre o desenho real do céu em sete biomas, quatro fases do dia, três estados noturnos, RGB/SRCALPHA, incluindo estrelas/nuvens e RGB oculto. Compara cache ligado com o método original integral, somando aos gates climáticos existentes; não troca gradientes nem quantidade de nuvens.

**Offline:** workflow ampliado com 4 testes novos (3 de retirement + 1 de céu completo); preservados 21 testes anteriores e preflight AST/SHA. Status de validação a preencher pelos logs, não afirmar sucesso antecipado.

**Preservação:** `main.py`, DEV, física, colisões, gameplay, sprites, assets, pets, saves, câmera e efeitos não foram alterados. Engine recebeu exclusivamente versão; Buildozer apenas versionName/versionCode, não executado. Sem APK/AAB/Android e sem homologação final. Placar de partida 15/32 offline, 17/32 parciais.
