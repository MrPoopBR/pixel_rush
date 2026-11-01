"""Pixel Rush v3.211 — auditoria/compilacao OFFLINE de arte.

Este arquivo NAO e importado pelo jogo. Apenas lê imagens de produção e escreve
relatórios em qa211. Atlas legado 3.114 é auditado, nunca recriado ou duplicado.
Compatível com Python >= 3.9, Pygame-ce e Pillow.

Uso: python pixelrush_assets_v3211.py [--saida qa211] [--medir]
"""
import argparse
from collections import defaultdict
import hashlib
from io import BytesIO
import json
from pathlib import Path
import statistics
import time
import sys

BASE = Path(__file__).resolve().parent
PRODUCAO = ('world_art_v3106', 'world_parallax_v3112')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def arquivos_producao(base=BASE):
    # Restrito aos recursos utilizados pelos sistemas de arte externos atuais:
    # nunca confundir screenshots de QA com assets usados na partida.
    return sorted(f for pasta in PRODUCAO for f in (base / pasta).glob('*.png'))


def auditar_png(base=BASE):
    from PIL import Image
    entradas, exatos, pixels = [], defaultdict(list), defaultdict(list)
    for f in arquivos_producao(base):
        bruto = f.read_bytes()
        with Image.open(f) as imagem:
            imagem.load()
            dims = list(imagem.size)
            modo = imagem.mode
            rgba = imagem.convert('RGBA')
            assinatura = sha(rgba.tobytes() + f'{dims[0]}x{dims[1]}'.encode())
            # Não interpretar alocacao virtual de 4 bytes/pixel como memoria
            # residente efetiva no Android: nao inclui sobreposicoes/caches.
            decodificado = imagem.width * imagem.height * 4
            meta = list(imagem.info.keys())
        rel = f.relative_to(base).as_posix()
        entradas.append(dict(arquivo=rel, bytes_png=len(bruto), largura=dims[0],
                            altura=dims[1], modo=modo, estimativa_rgba_bytes=decodificado,
                            sha256=sha(bruto), sha_rgba=assinatura,
                            metadados_png=meta))
        exatos[sha(bruto)].append(rel)
        pixels[assinatura].append(rel)
    return {
        'arquivos': entradas,
        'total_png': len(entradas),
        'tamanho_png_bytes': sum(i['bytes_png'] for i in entradas),
        'limite_superior_rgba_bytes': sum(i['estimativa_rgba_bytes'] for i in entradas),
        'duplicados_binarios': [x for x in exatos.values() if len(x)>1],
        'duplicados_rgba': [x for x in pixels.values() if len(x)>1],
        'aviso_memoria': 'Soma teorica de superficies RGBA se TODAS forem residentes; nao e uso real nem VRAM medido.'
    }


def validar_atlas_existente(base=BASE):
    """Confronta atlas já integrado 3.114 com originais, sem modificar quadros."""
    from PIL import Image, ImageChops
    pasta = base / 'world_parallax_v3112'
    manifesto = json.loads((pasta/'atlas_manifest.json').read_text(encoding='utf-8'))
    paginas = manifesto['atlases']
    inspecionados, erros, repetidos, ocupados = [], [], set(), defaultdict(list)
    with_images = []
    try:
        for arquivo in paginas:
            path = pasta / arquivo
            with Image.open(path) as a:
                with_images.append(a.convert('RGBA'))
        for item in manifesto['sprites']:
            origem = pasta / item['source_file']
            pagina = int(item['atlas_page'])
            x,y,w,h = map(int,item['atlas_rect'])
            chave = (item['biome'],int(item['sprite_index']))
            erro = []
            if chave in repetidos: erro.append('referencia_repetida')
            repetidos.add(chave)
            if origem.name != item['source_file']: erro.append('caminho_fora_pasta')
            if not origem.is_file(): erro.append('arquivo_ausente')
            if pagina < 0 or pagina >= len(with_images): erro.append('pagina_invalida')
            if w<1 or h<1 or x<0 or y<0:erro.append('retangulo_invalido')
            if not erro:
                try:
                    atlas = with_images[pagina]
                    if x+w>atlas.width or y+h>atlas.height:erro.append('fora_atlas')
                    if sha(origem.read_bytes())!=item['source_sha256']:erro.append('hash_origem')
                    with Image.open(origem) as original:
                        fonte=original.convert('RGBA')
                    if fonte.size!=(w,h):erro.append('dimensoes_origem')
                    elif atlas.crop((x,y,x+w,y+h)).tobytes()!=fonte.tobytes():erro.append('pixels_diferentes')
                    for ox,oy,ow,oh in ocupados[pagina]:
                        if x<ox+ow and ox<x+w and y<oy+oh and oy<y+h:erro.append('sobreposicao')
                    ocupados[pagina].append((x,y,w,h))
                except Exception as exc:
                    erro.append(type(exc).__name__)
            inspecionados.append({'sprite':str(chave), 'arquivo':origem.name,'problemas':erro})
            erros.extend(f'{chave}: {e}' for e in erro)
    finally:
        for img in with_images:img.close()
    return {'atlas_preexistente':'world_parallax_v3112/atlas_manifest.json',
            'paginas':len(paginas), 'sprites':len(inspecionados),
            'erros':erros, 'detalhes':inspecionados, 'aprovado':not erros,
            'decisao':'Reutilizar atlas existente, nao acrescentar novo atlas ao runtime.'}


def prospectar_compactacao(base=BASE):
    """Testa PNG recompactado em memoria sem tocar no arquivo fonte.

    Não inclui candidatas com metadados funcionais ou ganho < 2%,
    pois esses arquivos ja vieram compactados adequadamente.
    """
    from PIL import Image
    resultados=[]
    for f in arquivos_producao(base):
        data=f.read_bytes()
        with Image.open(BytesIO(data)) as a:
            a.load()
            original_modo=a.mode
            original_bytes=a.tobytes()
            info_keys=list(a.info.keys())
            buffer=BytesIO()
            a.save(buffer,format='PNG',compress_level=9,optimize=True)
        novo=buffer.getvalue()
        if len(novo)<len(data):
            with Image.open(BytesIO(novo)) as b:
                b.load()
                if b.mode!=original_modo or b.tobytes()!=original_bytes:
                    raise AssertionError('recodificacao mudou pixels: '+f.name)
        savings=len(data)-len(novo)
        if savings>0:
            resultados.append({'arquivo':f.relative_to(base).as_posix(),
                               'economia_bytes':savings,'percentual':round(100*savings/len(data),3),
                               'metadados':info_keys,'recomendar_aplicacao':not info_keys and savings/len(data)>=.02})
    return {'candidatos':resultados,'economia_teorica_bytes':sum(max(0,r['economia_bytes']) for r in resultados),
            'aplicar_nesta_versao':False,
            'criterio':'Somente origens com ganho >=2%, zero mudanca RGBA/modo e sem metadados relevantes; nenhuma e aplicada automaticamente.'}


def medir_io(base=BASE):
    """Mede somente leitura/decodificacao no host atual; nao simula FPS mobile."""
    import pygame
    pygame.init()
    pygame.display.set_mode((32,32))
    duracoes=[]
    for f in arquivos_producao(base):
        t0=time.perf_counter_ns()
        pixels=f.read_bytes()
        t1=time.perf_counter_ns()
        img=pygame.image.load(BytesIO(pixels), f.name)
        img=img.convert_alpha() if img.get_masks()[3] else img.convert()
        t2=time.perf_counter_ns()
        duracoes.append({'arquivo':f.relative_to(base).as_posix(),
                         'leitura_ms':round((t1-t0)/1e6,4),
                         'decodificacao_conversao_ms':round((t2-t1)/1e6,4),
                         'tamanho_superficie':list(img.get_size())})
    pygame.quit()
    ordered=sorted([x['decodificacao_conversao_ms'] for x in duracoes]);n=len(ordered)
    return {'ambiente':f'{sys.version.split()[0]} / Pygame SDL dummy',
            'arquivos_medidos':len(duracoes),'mediana_decode_ms':statistics.median(ordered) if ordered else None,
            'p95_decode_ms':ordered[min(n-1,int(n*.95))] if n else None,
            'maiores':sorted(duracoes,key=lambda v:v['decodificacao_conversao_ms'],reverse=True)[:12],
            'aviso':'Medição pontual e aquecida no PC/SDL dummy; nao representa Android nativo, RAM alocada ou FPS.'}


def salvar_relatorios(destino,base=BASE,medir=True):
    destino=Path(destino);destino.mkdir(parents=True,exist_ok=True)
    inv=auditar_png(base)
    atlas=validar_atlas_existente(base)
    poss=prospectar_compactacao(base)
    io=medir_io(base) if medir else {'nao_executado':True}
    rel={'versao_ferramenta':'v3.211.0', 'escopo':'somente assets externos de produção, QA excluído',
         'inventario':inv,'atlas':atlas,'compactacao':poss,'carregamento':io,
         'politica':'sem alterar pixel arts, sem deduplicar arquivos referenciados, sem carga adicional no runtime'}
    (destino/'inventario_assets_v3211.json').write_text(json.dumps(rel,ensure_ascii=False,indent=2),encoding='utf-8')
    linhas=[
        '# Relatório de assets — v3.211.0', '',
        f"- PNGs externos de produção: **{inv['total_png']}**.",
        f"- Tamanho PNG total: **{inv['tamanho_png_bytes']:,} bytes**.",
        f"- Soma hipotética RGBA: **{inv['limite_superior_rgba_bytes']/2**20:.2f} MiB** (não é RAM real).",
        f"- Duplicados byte a byte: **{len(inv['duplicados_binarios'])} grupos**.",
        f"- Duplicados RGBA: **{len(inv['duplicados_rgba'])} grupos**.",
        f"- Atlas já existente: **{atlas['sprites']} sprites**, **{atlas['paginas']} página(s)**, **{len(atlas['erros'])} alertas**.",
        f"- Economia potencial de recodificação PNG sem alterar pixels: **{poss['economia_teorica_bytes']:,} bytes**, sem aplicar por não justificar risco/manutenção.",
        f"- Tempo mediano decodificação + conversão no host: **{io.get('mediana_decode_ms','não medido')} ms**.",
        '', '## Limites', '',
        '- Não contabiliza sprites gerados proceduralmente, skins embutidas em código nem pico real de RAM.',
        '- Não é medição nativa em Galaxy A54, MEmu ou APK/AAB.',
        '- Não remove ou renomeia arquivos existentes nem substitui os atlases integrados.',
        '- Nenhum ganho de FPS em partida foi reivindicado.',
    ]
    if atlas['erros']:linhas += ['','### Alertas do atlas'] + ['- '+e for e in atlas['erros']]
    (destino/'RELATORIO_ASSETS_v3.211.0.md').write_text('\n'.join(linhas)+'\n',encoding='utf-8')
    return rel


def main():
    parser=argparse.ArgumentParser(description='Auditor de assets offline Pixel Rush v3.211')
    parser.add_argument('--saida',type=Path,default=BASE/'qa211')
    parser.add_argument('--sem-benchmark',action='store_true')
    args=parser.parse_args()
    rel=salvar_relatorios(args.saida,medir=not args.sem_benchmark)
    print('QA ASSETS',rel['inventario']['total_png'],'PNGs;',rel['atlas']['sprites'],'sprites atlas;',
          'alertas',len(rel['atlas']['erros']))
    return 0 if not rel['atlas']['erros'] else 2

if __name__=='__main__':
    sys.exit(main())
