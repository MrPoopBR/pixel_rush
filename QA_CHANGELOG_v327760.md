# PIXEL RUSH — Changelog integrado QA v3.277.60

Branch única: qa/fechamento-32-v3.277.57. Base v3.277.59-QA.

## Código alterado

**#18 Cache de céu/nuvens/clima:** pixelrush_qa_scene_v327733.py agora usa o cache de textura de nuvem apenas quando o destino não é SRCALPHA e as três cores são opacas. A função original pygame.draw.rect permanece para alvos transparentes, cores parcialmente transparentes, escalas não suportadas e rollback PIXELRUSH_QA_SAFE_CLOUD_CACHE=0. Motivo: blit SRCALPHA pode zerar RGB oculto que o desenho original deixaria intacto. Não adicionar Surface de framebuffer ao cache; LRU de até 96 nuvens leves já existente. Mantido desenho original em casos de paridade incerta.

**Gates:** tests/test_qa_cloud_weather_v327760.py com provas byte RGBA em todas as combinações de flags, fundo alfa 0/255, cores RGB/RGBA opacas/parciais, posição, escala 1/2, comparação das 14 condições de clima da função real World._weather vs QA e benchmark local RGB. O workflow offline mantém 18 gates existentes. Resultado dos novos gates ainda pendente, sem presumir ganhos Android.

**Metadados:** engine somente string da versão, VERSAO_ATUAL, tracker, changelog, spec. Sem SDK Android, Buildozer, Gradle, APK, AAB, ADB ou homologação de driver. main, DEV, tutorial, física, gameplay, saves, pets, assets e shaders não alterados. Estado conservador de entrada: 15 concluídas offline, 17 parciais, 0 homologadas Android.
