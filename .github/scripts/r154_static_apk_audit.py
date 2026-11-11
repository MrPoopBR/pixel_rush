#!/usr/bin/env python3
"""R154: auditoria estatica ARM64/16KiB, sem testes no aparelho."""
import gzip
import hashlib
import io
import json
import re
import struct
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

APK_SHA256 = "0f12e59327b5284fca0df0e009d7d856b997f84c324a5bfcc7c656cda9306b44"
CRITICOS = {
    "_ssl.cpython-312.so": {"libpython3.12.so", "libssl.so", "libcrypto.so"},
    "_hashlib.cpython-312.so": {"libpython3.12.so", "libcrypto.so"},
    "_ctypes.cpython-312.so": {"libpython3.12.so", "libffi.so"},
    "math.cpython-312.so": {"libpython3.12.so"},
    "zlib.cpython-312.so": {"libpython3.12.so"},
}

def check_elf(nome, data):
    if (len(data) < 64 or data[:5] != b"\x7fELF\x02" or data[5] != 1
            or struct.unpack_from("<H", data, 18)[0] != 183):
        raise ValueError("ELF nao ARM64: " + nome)
    off = struct.unpack_from("<Q", data, 32)[0]
    es = struct.unpack_from("<H", data, 54)[0]
    n = struct.unpack_from("<H", data, 56)[0]
    if es < 56 or n < 1 or off + es * n > len(data):
        raise ValueError("Tabela ELF invalida: " + nome)
    count = 0
    for i in range(n):
        pos = off + es * i
        if struct.unpack_from("<I", data, pos)[0] != 1:
            continue
        foff, vaddr, align = (struct.unpack_from("<Q", data, pos + j)[0] for j in (8, 16, 48))
        if align < 16384 or (foff-vaddr)%16384:
            raise ValueError("PT_LOAD sem 16KiB: " + nome)
        count += 1
    if not count:
        raise ValueError("ELF sem PT_LOAD: " + nome)
    return count

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python r154_static_apk_audit.py APK")
    apkpath = Path(sys.argv[1])
    body = apkpath.read_bytes()
    sha = hashlib.sha256(body).hexdigest()
    if sha != APK_SHA256:
        raise ValueError("APK diferente do original R154 #2: "+sha)
    so = {}
    with zipfile.ZipFile(io.BytesIO(body)) as apk:
        if apk.testzip():
            raise ValueError("CRC invalido no APK")
        for name in apk.namelist():
            if not name.startswith("lib/") or not name.endswith(".so"):
                continue
            if not name.startswith("lib/arm64-v8a/"):
                raise ValueError("ABI inesperada: "+name)
            so[name] = apk.read(name)
        # libpybundle.so e um tar.gz com sufixo .so (formato p4a), NAO ELF.
        packed = so.pop("lib/arm64-v8a/libpybundle.so", None)
        if not packed or not packed.startswith(b"\x1f\x8b"):
            raise ValueError("libpybundle.so nao contem gzip valido")
        with tarfile.open(fileobj=io.BytesIO(gzip.decompress(packed)), mode="r:") as tar:
            for m in tar.getmembers():
                if m.isfile() and m.name.endswith(".so"):
                    if not m.name.startswith("_python_bundle/") or "x86_64" in m.name or "linux-gnu" in m.name:
                        raise ValueError("Extensao Python inesperada: "+m.name)
                    so[m.name] = tar.extractfile(m).read()
        with tarfile.open(fileobj=io.BytesIO(apk.read("assets/private.tar")), mode="r:*") as private:
            files = set(private.getnames())
            pcm = [n for n in files if n.startswith("assets/audio/prebaked_r154/") and n.endswith(".pcm")]
            if len(pcm) != 6 or not ({"main.py", "main.pyc"} & files):
                raise ValueError("Entrada Python ou 6 trilhas PCM ausentes")
    stats = Counter()
    for name, binary in so.items():
        stats["pt_load_16k"] += check_elf(name, binary)
        stats["bundle" if name.startswith("_python_bundle/") else "external"] += 1
    if stats["external"] != 15 or stats["bundle"] != 114:
        raise ValueError("Quantidade ELF nao corresponde ao APK R154: "+str(stats))
    with tempfile.TemporaryDirectory() as temp:
        for basename, expected in CRITICOS.items():
            key = "_python_bundle/modules/"+basename
            if key not in so:
                raise ValueError("Modulo CPython ausente: "+basename)
            obj = Path(temp)/basename
            obj.write_bytes(so[key])
            res = subprocess.run(["readelf", "-dW", str(obj)], capture_output=True, text=True, check=True)
            needed = set(re.findall(r"\(NEEDED\).*?\[([^]]+)\]",res.stdout))
            if expected-needed:
                raise ValueError("DT_NEEDED faltando em "+basename+": "+str(sorted(expected-needed)))
    report = {
        "resultado":"APROVADO_ESTATICAMENTE_SEM_HOMOLOGACAO_ANDROID",
        "apk_sha256":sha,
        "apk_bytes":len(body),
        "elf_arm64_total":stats["external"]+stats["bundle"],
        "elf_externos":stats["external"],
        "elf_bundle_python":stats["bundle"],
        "pt_load_16k":stats["pt_load_16k"],
        "pcm":len(pcm),
        "package_esperado":"com.bigheadmobile_pixelrush",
        "version_code_esperado":"327906",
    }
    Path("R154_AUDITORIA_APK.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=="__main__":
    try:
        main()
    except Exception as error:
        print("FALHA NA AUDITORIA: "+str(error),file=sys.stderr)
        sys.exit(1)
