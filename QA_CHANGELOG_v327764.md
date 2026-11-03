# PIXEL RUSH — Changelog v3.277.64-QA

Integração na mesma branch qa/fechamento-32-v3.277.57, a partir da v3.277.63.

Melhoria #25 (ainda parcial): memória RSS alta agora permite desalocar caches derivados de cenas modulares inativas. A política é compartilhada entre limpeza parcelada e fallback. Neve: _maps/_composites; Deserto: _maps/_composites/_night_tiles. Não apagar _night_tiles pré-computadas de Neve, tiles fonte, poses nem buffers do bioma ativo. Bioma reavaliado no momento do pop para evitar corrida com troca de cenário.

Testes pygame-ce offline: novo conjunto cobre fallback RSS, mudança de bioma após agendamento, preservação de Neve e resultado RGBA do método real de Deserto antes/depois da evicção. Testes anteriores e preflight AST/SHA continuam no CI. Nenhum desempenho Android inferido antes dos logs.

Metadados sincronizados no arquivo de engine, VERSION e buildozer.spec; não compilar APK/AAB ou homologar Android. main, DEV, física, aparência, jogabilidade, recursos, pets, saves e workflow de produção preservados.