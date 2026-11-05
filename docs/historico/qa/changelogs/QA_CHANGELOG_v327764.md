# PIXEL RUSH — Changelog v3.277.64-QA

Integração na mesma branch qa/fechamento-32-v3.277.57, a partir da v3.277.63.

Melhoria #25 (ainda parcial): memória RSS alta agora permite desalocar caches derivados de cenas modulares inativas. A política é compartilhada entre limpeza parcelada e fallback. Neve: _maps/_composites; Deserto: _maps/_composites/_night_tiles. Não apagar _night_tiles pré-computadas de Neve, tiles fonte, poses nem buffers do bioma ativo. Bioma reavaliado no momento do pop para evitar corrida com troca de cenário.

Testes pygame-ce offline: novo conjunto cobre fallback RSS, mudança de bioma após agendamento, preservação de Neve e resultado RGBA do método real de Deserto antes/depois da evicção. Testes anteriores e preflight AST/SHA continuam no CI. Nenhum desempenho Android inferido antes dos logs.

Metadados sincronizados no arquivo de engine, VERSION e buildozer.spec; não compilar APK/AAB ou homologar Android. main, DEV, física, aparência, jogabilidade, recursos, pets, saves e workflow de produção preservados.
## Evidência final e status v764

O CI offline #41721816822 foi aprovado: 33/33 testes automáticos pygame-ce 2.5.8 + preflight AST/SHA. Novos 4 testes de RAM modular passaram: Neve pré-gerada preservada, Deserto recomposto byte-RGBA, fila segura após troca de bioma, fallback RSS seguro. O status permanece 17/32 implementadas e validadas offline, 15/32 parciais, 0/32 homologadas Android. Não afirmar queda real de RSS ou aumento FPS no dispositivo; código final preserva todos os comportamentos de gameplay, física, visual, pets e saves, não há compilação APK/AAB nem alterações em main/DEV/workflows Android.
