#!/usr/bin/env python3
"""Validacoes verificaveis do APK debug Android RC; nunca usa segredos de assinatura.

Subcomandos: preflight, apk. Este arquivo nao altera codigo do jogo.
"""
import argparse
import configparser
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import tarfile
import zipfile

EXPECTED_BLOBS = {
    'PixelRush_v3.277.11_PRODUCAO_ANDROID_RC.py': '48618ccfb0ac6268bac2a97c7ad8192763c9b90e',
    'main.py': '77b3fb47fb1123eb71bed711c9cdf6312cd0a008',
    'VERSAO_ATUAL.txt': 'f166d950d8d1f1577519d448a6fee2ce5d33e3ce',
    'p4a-recipes/python3/__init__.py': 'fc7a21423b3eae737422d2da2d5a985a247aca81',
    '.github/scripts/test_android_p4a_patches.py': '07ce9c357d37fa99d9189cf03afa703d61b93977',
    '.github/scripts/test_android_stdlib_bootstrap.py': '8361723053d4ecddbf2cbc88d28ab0b20856eaf6',
    '.github/scripts/test_android_stdlib_dt_needed.py': '3f47d6ebf543b90ff9e4e2939dfe92eb8401799f',
    'assets/atlas_prod_v32776/deserto.atlas': 'a35eb6e2cc2d1eb1069270e7ffb25c195201318d',
    'assets/buffers_prod_v32779/neve.pbuf': '2a9b535e25dc306f7adb24d8978cca8d7eefc2f4',
}
EXPECTED_CONFIG = {
    'version': '3.277.27',
    'android.numeric_version': '327727',
    'icon.filename': 'assets_android/icon_pixel_rush.png',
    'presplash.filename': 'assets_android/splash_01_vermelho.png',
    'android.api': '36',
    'android.minapi': '26',
    'android.ndk': '28c',
    'android.ndk_api': '26',
    'android.archs': 'arm64-v8a',
    'android.debug_artifact': 'apk',
    'p4a.bootstrap': 'sdl2',
    'p4a.local_recipes': 'p4a-recipes',
}
REQUIRED_EXTENSIONS = ('py', 'png', 'json', 'ttf', 'atlas', 'pbuf', 'tiles', 'rgbaz', 'pcmz')


ANDROID_VISUAL_ASSETS = {
    'assets_android/icon_pixel_rush.png': '5cc97d07346966734b0e16b080841d559078477009d3068932cb8f84c2ee1e76',
    'assets_android/splash_01_vermelho.png': '5ac990f52e9724eb27cbfe8fbdb506f81d0fbd02678ca3fc491276a3c71483ac',
    'assets_android/splash_02_laranja.png': '2429c4736f45ce7c9b5892d88d3310db7ce821a6f322a772c22a4bcdf0afd4e6',
    'assets_android/splash_03_amarelo.png': '9bc945ec7c1bce8342bd6617a77819b8bd6e79b3c958724e2fa97664d4eb50ab',
    'assets_android/splash_04_ciano.png': 'c1e778a439e660558f21da6d22d5fce090330427a9819071a33506f20c575322',
}

def check_preflight():
    conf = configparser.ConfigParser(interpolation=None)
    if not conf.read('buildozer.spec', encoding='utf-8'):
        raise AssertionError('buildozer.spec ausente')
    spec = conf['app']
    for key, wanted in EXPECTED_CONFIG.items():
        value = spec.get(key, '').strip()
        if value != wanted:
            raise AssertionError(f'buildozer.spec {key}: {value!r}, esperado {wanted!r}')
    req = {s.strip() for s in spec['requirements'].split(',')}
    required = {'python3==3.12.12', 'hostpython3==3.12.12', 'numpy', 'pygame-ce'}
    if not required <= req:
        raise AssertionError(f'requisitos obrigatorios ausentes: {required - req}')
    exts = {s.strip() for s in spec['source.include_exts'].split(',')}
    if not set(REQUIRED_EXTENSIONS) <= exts:
        raise AssertionError(f'extensoes ausentes: {set(REQUIRED_EXTENSIONS)-exts}')
    recipe = Path('p4a-recipes/pygame-ce/__init__.py').read_text(encoding='utf-8')
    if not re.search(r'(?m)^\s*version\s*=\s*[\"\']2\.5\.8[\"\']', recipe):
        raise AssertionError('receita pygame-ce nao fixa 2.5.8')
    if 'system src_c/system.c' not in recipe:
        raise AssertionError('receita sem modulo nativo pygame.system para saves')
    for filename, sha in EXPECTED_BLOBS.items():
        raw = Path(filename).read_bytes()
        blob_hash = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        if blob_hash != sha:
            raise AssertionError(f'fonte/asset RC diferente do original: {filename}')
    for filename, wanted in ANDROID_VISUAL_ASSETS.items():
        raw = Path(filename).read_bytes()
        if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
            raise AssertionError(f'PNG visual Android invalido: {filename}')
        if hashlib.sha256(raw).hexdigest() != wanted:
            raise AssertionError(f'Asset visual Android alterado: {filename}')
    if 'v3.277.27' not in Path('VERSAO_ATUAL.txt').read_text(encoding='utf-8'):
        raise AssertionError('arquivo de versao divergente')
    summary = {'resultado': 'APROVADO', 'pygame_ce_recipe': '2.5.8', 'numpy': 'p4a recipe', 'android_api': 36,
               'android_ndk': '28c', 'ndk_api': 26, 'abi': 'arm64-v8a', 'assets_amostrados': len(EXPECTED_BLOBS), 'assets_visuais_android': len(ANDROID_VISUAL_ASSETS)}
    return summary


def elf_segments(raw, name):
    if raw[:4] != b'\x7fELF':
        raise AssertionError(f'{name}: nao e ELF')
    if raw[4] != 2 or raw[5] != 1:
        raise AssertionError(f'{name}: nao e ELF64 little endian')
    if len(raw) < 64 or struct.unpack_from('<H', raw, 18)[0] != 183:
        raise AssertionError(f'{name}: arquitetura nao e AArch64')
    phoff = struct.unpack_from('<Q', raw, 32)[0]
    phentsize, phnum = struct.unpack_from('<HH', raw, 54)
    if phnum == 0 or phentsize < 56:
        raise AssertionError(f'{name}: tabela PHDR ausente/invalida')
    if phoff + phentsize * phnum > len(raw):
        raise AssertionError(f'{name}: PHDR extrapola o ELF')
    loads = []
    for i in range(phnum):
        off = phoff + i * phentsize
        if struct.unpack_from('<I', raw, off)[0] != 1:
            continue
        segment_offset = struct.unpack_from('<Q', raw, off + 8)[0]
        vaddr = struct.unpack_from('<Q', raw, off + 16)[0]
        align = struct.unpack_from('<Q', raw, off + 48)[0]
        if align < 16384 or (vaddr - segment_offset) % 16384:
            raise AssertionError(f'{name}: PT_LOAD desalinhado 16 KiB (align={align:#x})')
        loads.append(align)
    if not loads:
        raise AssertionError(f'{name}: sem segmentos PT_LOAD')
    return loads


def find_bin(name):
    found = shutil.which(name)
    if found:
        return found
    candidates = []
    for sdk in (os.environ.get('ANDROID_HOME'), os.environ.get('ANDROID_SDK_ROOT'),
                str(Path.home() / '.buildozer/android/platform/android-sdk')):
        if sdk:
            candidates.extend(Path(sdk).glob('build-tools/*/' + name))
    return str(sorted(candidates)[-1]) if candidates else None


def check_apk(apk):
    apk = Path(apk)
    if not apk.is_file() or apk.suffix != '.apk':
        raise AssertionError(f'APK debug nao encontrado: {apk}')
    libraries = []
    zip_stored_checked = 0
    stdlib_check = {}

    def collect_tar(label, payload, mode='r:*'):
        # O bootstrap p4a grava os modulos Python num TAR gzip chamado
        # libpybundle.so. O nome .so nao significa que o conteudo seja ELF.
        try:
            with tarfile.open(fileobj=io.BytesIO(payload), mode=mode) as archive:
                for member in archive:
                    if member.isfile() and member.name.endswith('/stdlib.zip'):
                        if stdlib_check:
                            raise AssertionError('varios stdlib.zip encontrados em bundles')
                        stream = archive.extractfile(member)
                        if stream is None:
                            raise AssertionError('bundle Python sem leitura de stdlib.zip')
                        with zipfile.ZipFile(io.BytesIO(stream.read())) as lib:
                            infos = lib.infolist()
                            if not infos or any(i.compress_type != zipfile.ZIP_STORED for i in infos):
                                raise AssertionError('stdlib.zip deve usar ZIP_STORED; DEFLATE depende de zlib no boot')
                            missing = {'encodings/__init__.pyc', 'encodings/utf_8.pyc',
                                       'codecs.pyc'} - set(lib.namelist())
                            if missing:
                                raise AssertionError(f'stdlib.zip sem codecs: {sorted(missing)}')
                            for boot_name in ('encodings/__init__.pyc',
                                              'encodings/utf_8.pyc', 'codecs.pyc'):
                                if lib.read(boot_name)[:4] != b'\xcb\r\r\n':
                                    raise AssertionError(f'magic Python 3.12 invalido: {boot_name}')
                            bad = lib.testzip()
                            if bad:
                                raise AssertionError('stdlib.zip CRC invalido: ' + bad)
                            stdlib_check.update({'arquivos': len(infos),
                                                 'compressao': 'ZIP_STORED',
                                                 'codecs': 'presentes'})
                    if member.isfile() and member.name.endswith('.so'):
                        f = archive.extractfile(member)
                        if f:
                            libraries.append((label + '!' + member.name, f.read()))
        except (tarfile.TarError, OSError) as exc:
            raise AssertionError(f'{label}: TAR Python invalido: {exc}') from exc

    with zipfile.ZipFile(apk, 'r') as z, apk.open('rb') as apk_source:
        entries = z.namelist()
        if not any(x.endswith('.so') and x.startswith('lib/arm64-v8a/') for x in entries):
            raise AssertionError('APK sem bibliotecas Android lib/arm64-v8a/')
        for item in z.infolist():
            # Em ZIP/APK, apenas entradas STORED necessitam alinhamento de
            # deslocamento. Libraries ELF STORED exigem 16 KiB; outras, 4 B.
            # Entradas DEFLATED nao sao carregadas diretamente do APK.
            if item.compress_type == zipfile.ZIP_STORED:
                apk_source.seek(item.header_offset)
                header = apk_source.read(30)
                if len(header) != 30 or header[:4] != b'PK\x03\x04':
                    raise AssertionError(f'{item.filename}: cabecalho ZIP local invalido')
                name_len, extra_len = struct.unpack_from('<HH', header, 26)
                data_offset = item.header_offset + 30 + name_len + extra_len
                alignment = 16384 if (item.filename.startswith('lib/') and
                                      item.filename.endswith('.so')) else 4
                if data_offset % alignment:
                    raise AssertionError(
                        f'{item.filename}: ZIP STORED desalinhado '
                        f'(offset={data_offset}, exigido={alignment})'
                    )
                zip_stored_checked += 1

            if item.filename == 'lib/arm64-v8a/libpybundle.so':
                bundle = z.read(item)
                if not bundle.startswith(b'\x1f\x8b'):
                    raise AssertionError('libpybundle.so: esperado TAR gzip do python-for-android')
                collect_tar(item.filename, bundle, mode='r:gz')
            elif item.filename.endswith('.so'):
                libraries.append((item.filename, z.read(item)))
            elif item.filename.endswith(('.tar', '.tar.gz', '.tgz')):
                collect_tar(item.filename, z.read(item))
    if not libraries:
        raise AssertionError('nenhuma biblioteca compartilhada encontrada')
    if not stdlib_check:
        raise AssertionError('bundle Python sem stdlib.zip validado')
    if not any('/modules/zlib.cpython-312.so' in label for label, _ in libraries):
        raise AssertionError('bundle Python sem extensao nativa zlib 3.12')
    if not zip_stored_checked:
        raise AssertionError('APK sem entradas ZIP STORED para auditar')
    aligned = []
    for name, payload in libraries:
        loads = elf_segments(payload, name)
        aligned.append({'nome': name, 'load_alignments': loads})
    # Prova DT_NEEDED nas extensoes CPython empacotadas.
    cpython_modules = [(label, binary) for label, binary in libraries
                       if re.search(r'/modules/[^/]+\.cpython-312\.so$', label)]
    required_modules = {'math', 'zlib', '_ctypes', '_ssl'}
    module_names = {Path(label).name.split('.cpython-312.so')[0]
                    for label, _ in cpython_modules}
    if required_modules - module_names or len(cpython_modules) < 50:
        raise AssertionError('extensoes nativas CPython incompletas: '
                             + repr(sorted(required_modules - module_names)))
    readelf = shutil.which('readelf')
    if not readelf:
        raise AssertionError('readelf ausente: gate DT_NEEDED sem evidencia')
    with tempfile.TemporaryDirectory(prefix='px-cpython-needed-') as temp:
        for i, (label, binary) in enumerate(cpython_modules):
            file = Path(temp) / f'modulo_{i}.so'
            file.write_bytes(binary)
            result = subprocess.run([readelf, '-d', str(file)],
                                    text=True, capture_output=True)
            if result.returncode:
                raise AssertionError(f'{label}: readelf falhou: {result.stderr[-300:]}')
            occurrences = re.findall(
                r'\(NEEDED\).*?Shared library: \[libpython3\.12\.so\]',
                result.stdout)
            if len(occurrences) != 1:
                raise AssertionError(f'{label}: DT_NEEDED libpython3.12.so ausente ou duplicado')
    names = [item[0].lower() for item in libraries]
    # A prova de pygame e numpy requer detectar as extensoes nativas, nao apenas SDL/libpython.
    pygame_native = [name for name in names if '/pygame/' in name or 'pygame' in Path(name).name]
    numpy_native = [name for name in names if '/numpy/' in name or 'numpy' in Path(name).name or '_multiarray_umath' in name]
    if not pygame_native:
        raise AssertionError('nao foi encontrada extensao nativa do pygame-ce no APK')
    if not numpy_native:
        raise AssertionError('nao foi encontrada extensao nativa NumPy no APK')
    if any(x.endswith('.aab') for x in entries):
        raise AssertionError('AAB indevidamente empacotado no APK debug')
    zipalign = find_bin('zipalign')
    if not zipalign:
        raise AssertionError('zipalign ausente: instalar SDK Build-Tools >=35')
    check = subprocess.run([zipalign, '-c', '-P', '16', '-v', '4', str(apk)],
                           text=True, capture_output=True)
    if check.returncode:
        raise AssertionError('zipalign -P 16 reprovou APK: ' + (check.stderr or check.stdout)[-2500:])
    aapt = find_bin('aapt')
    if not aapt:
        raise AssertionError('aapt ausente: sem como checar manifest API 36 e min26')
    result = subprocess.run([aapt, 'dump', 'badging', str(apk)], text=True, capture_output=True)
    if result.returncode:
        raise AssertionError('aapt dump badging falhou: ' + result.stderr[-1200:])
    manifest = result.stdout
    for label, rx in [('targetSdkVersion 36', r"targetSdkVersion:'36'"),
                      ('sdkVersion 26', r"sdkVersion:'26'")]:
        if not re.search(rx, manifest):
            raise AssertionError(f'Manifest APK nao confirma {label}')
    if "native-code: 'arm64-v8a'" not in manifest:
        raise AssertionError('manifest nao confirma ABI exclusiva ARM64')
    return {'resultado': 'APROVADO', 'apk': str(apk), 'bibliotecas_so': len(libraries),
            'bibliotecas_pygame': len(pygame_native), 'bibliotecas_numpy': len(numpy_native),
            'alinhamento_elf_minimo': min(min(x['load_alignments']) for x in aligned),
            'zipalign_16k': 'aprovado', 'cp312_modulos_dt_needed': len(cpython_modules), 'zip_stored_verificados': zip_stored_checked, 'target_api': 36, 'min_api': 26,
            'arquitetura': 'arm64-v8a', 'stdlib_python': stdlib_check,
            'bibliotecas': aligned}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('etapa', choices=('preflight', 'apk'))
    ap.add_argument('--apk')
    ap.add_argument('--report', default='debug-apk-validation.json')
    args = ap.parse_args()
    try:
        if args.etapa == 'preflight':
            result = check_preflight()
        else:
            if not args.apk:
                raise AssertionError('informe --apk')
            result = check_apk(args.apk)
    except Exception as ex:
        result = {'resultado': 'REPROVADO', 'etapa': args.etapa, 'motivo': str(ex)}
        Path(args.report).write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
    Path(args.report).write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'bibliotecas'}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
