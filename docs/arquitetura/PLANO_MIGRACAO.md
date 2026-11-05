# Plano seguro para modularizar o motor PIXEL RUSH

1. **QA788: bases e histórico** — mover código de tres aceleradores da Cidade
   para `src/pixelrush/performance/city` mantendo compatibilidade, arquivar
   somente notas antigas comprovadamente não referenciadas pelos testes/CI,
   documentar imports e validar benchmarks. Esta etapa não acaba a migração.
2. **Mundo e render** — extrair um sistema de cada vez (câmera, Cidade, clima,
   sprites urbanos) mantendo wrappers e preservando os 260 buffers RGBA.
3. **Entidades e sistemas** — separar player, inimigos, pets, física, input,
   tutorial, saves e áudio usando adaptadores temporários e fixtures reais.
4. **Motor principal** — extrair o loop de 16.120 linhas somente após os
   subsistemas terem interfaces estáveis; preservar `main.py` e a assinatura
   de APK/AAB, verificar carregamento de assets e saves antigos.
5. **Limpeza definitiva** — remover adaptadores/arquivos antigos apenas quando
   todos os imports + CI de Python + testes em Android real passarem. Arquivos
   históricos que sustentam testes antigos ficam guardados e versionados.

**Não remover em massa:** arquivos Python por parecerem antigos, notas citadas
pelos gates antigos, receitas `p4a-recipes`, world art, bibliotecas C, saves ou
workflows. Uma chamada de limpeza indiscriminada pode corromper APK/AAB.

### Segunda etapa QA789

25 módulos reais de Cidade/biomas/mundo/render foram movidos e as importações legadas preservadas. O motor de 16 mil linhas, módulos Python com hashes de preflight, entidades, pets, física, save e câmera ainda dependem de testes adicionais antes da migração completa. Três documentos foram arquivados com blobs iguais e as notas exigidas por CI foram retidas.
