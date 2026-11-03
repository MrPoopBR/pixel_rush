# PIXEL RUSH v3.277.46-QA — Pré-aquecimento seguro e benchmark de buffer integral

**Nova branch isolada:** `qa/android-full-performance-v3.277.46`  
**Base:** `qa/android-full-performance-v3.277.45`, commit `4e6681ec28f82c55fed0b8ed3c686a8b23b5aa22`.

## A. Pré-aquecimento sem duplicar o carregador
- Auditoria comprovou que a classe REAL do jogo é `pixelrush_world_prod_v32777.LivingWorld`, que já usa os atlas SHA-256 de `pixelrush_atlas_prod_v32776.py` e libera a cena modular anterior. Benchmarks antigos contra `pixelrush_world_v3130` não podiam ser extrapolados para a produção.
- Nova API `pixelrush_qa_biome_preheat_v327746.py`: `preparar_fora_da_corrida(world, proximo_bioma, estado, teto_rss_mib=384, max_aumento_mib=32)`. Permite apenas estados INICIO/CARREGANDO/PREPARACAO, mundo atual cidade e alvo neve/deserto. Usa **o mesmo slot** `world.modular`, carrega apenas atlas existente validado por SHA, recusa sobre-RSS, uso em corrida, classe incorreta ou outro módulo ocupando slot. Nenhum backend GPU, thread SDL, arquivo de arte ou cache de texturas novo.
- **Auto-preheat OFF:** o próximo bioma do jogo é sorteado somente na transição enquanto JOGANDO. Antecipar aleatoriedade alteraria a sequência do jogo; usar a API exige uma janela de carregamento onde o alvo já seja conhecido. Não foi alterado o sorteio, a física, saves nem o instante da transição.
- Testes/profiler usam a classe **PROD** para comparar carregamento frio real com cena pré-preparada, paridade RGBA e aumento de RSS temporário. O ato de preparar consome tempo fora da corrida; não é redução do custo total de geração.

## B. Buffer do 5º quadro — fundo REAL
- Novo `tests/test_qa_buffer_full_v327746.py` e `.github/scripts/qa_benchmark_preheat_buffer_v327746.py`: usa `ParallaxBackground` da cópia QA de produção, `profundidade_cinematografica`, `desenhar_profundidade_bioma` Fase B, `SistemaClima._desenhar_nuvens_clima`, `CenasMemoraveis`, chão e HUD sintético mutável.
- Compara **byte-a-byte RGBA**, 35 quadros por cidade/neve/deserto com noite/clima/scroll. Controle: render direto na tela + `CacheFundoUltraQA.guardar`; alternativa: composição em buffer offscreen e **um blit no display**. Ambas mantêm o mesmo frame do fundo e intervalo de 5.
- **Regressao detectada, alternativa ingênua reprovada:** com mundos independentes, a scratch que nao copiava o framebuffer anterior divergiu em `deserto`/noite=0.95/frame=15 no pixel (444,340). O renderizador de fundo nao garante repintura opaca em todos os pixels quando existem camadas transparentes.
- **Alternativa segura em teste:** antes de compor num buffer offscreen, copia `alt` (framebuffer do quadro anterior) para a scratch, preservando o underlay de todas as camadas. Isso adiciona uma transferencia completa alem da apresentacao; por isso nao declarar ganho de FPS sem medicao justa. O benchmark compara objetos de cena separados iniciados com RNG identico.
- **Alternativa OFF por padrão**; NÃO altera a política de cinco quadros. Só habilitar após evidência de ganho e validação de frame real Android.

## C. Tracker das 32 frentes
Arquivo `QA_TRACKER_32_v327746.md` com critério conservador: 12 concluídas na integração offline, 15 parciais e 5 pendentes, sem confundir implementação com homologação de FPS Android.

## Preservações e testes
Versão QA `v3.277.46-QA-ANDROID-RC`, Buildozer `3.277.46 / 327746`, nomes de relatórios QA `pixelrush_qa_v327746.json` / CSV. Modificações do jogo são **somente a versão**. Nenhuma mudança em aparência, sprites, Pygame gameplay, aleatoriedade, física, tela, qualidade, efeitos, pets, saves, main, DEV, assets ou workflows APK/AAB. Novo CI `qa-offline-v327746.yml` só executa Python/pygame-ce/Linux SDL e emite JSON. **Não compilar APK nem testar Android.**
