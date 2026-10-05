"""Extract the hash-pinned Windows compiler locally without running its installer."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from setup_sdk import ROOT, sha256
from build_br23 import toolchain_provenance


def fetch(path, url, expected, download):
    if not path.exists():
        if not download: raise ValueError(f'Missing {path}; supply it or pass --download')
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
            temporary=Path(f.name)
            try:
                with urllib.request.urlopen(url, timeout=60) as r: shutil.copyfileobj(r,f)
            except BaseException:
                f.close(); temporary.unlink(); raise
        try:
            if sha256(temporary)!=expected: raise ValueError(f'Download hash mismatch: {url}')
            temporary.rename(path)
        finally:
            if temporary.exists(): temporary.unlink()
    if sha256(path)!=expected: raise ValueError(f'Hash mismatch: {path}')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    cache=ROOT/'.cache/toolchain'
    p.add_argument('--installer',type=Path,default=cache/'JL_toolchain_2.5.2.exe')
    p.add_argument('--extractor-archive',type=Path,default=cache/'innoextract-1.9-windows.zip')
    p.add_argument('--out',type=Path,default=cache/'extracted-2.5.2')
    p.add_argument('--download',action='store_true'); a=p.parse_args()
    if os.name!='nt': p.error('This pinned toolchain is for Windows.')
    lock=json.loads((ROOT/'toolchain.lock.json').read_text())
    fetch(a.installer,lock['installer_url'],lock['installer_sha256'],a.download)
    fetch(a.extractor_archive,lock['extraction_tool_url'],lock['extraction_archive_sha256'],a.download)
    out=a.out.resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    tc=out/'C$/JL/pi32/bin'
    if not out.exists():
        with tempfile.TemporaryDirectory(prefix='toolchain-',dir=out.parent) as directory:
            staging=Path(directory); exe=staging/'innoextract.exe'
            with zipfile.ZipFile(a.extractor_archive) as z:
                entries=[n for n in z.namelist() if n.endswith('/innoextract.exe') or n=='innoextract.exe']
                if len(entries)!=1: raise ValueError('Expected exactly one extractor executable')
                exe.write_bytes(z.read(entries[0]))
            extracted=staging/'extracted'
            # Match the pi32 directory, including its target headers and libraries.
            subprocess.run([str(exe),'--silent','--include','pi32','--output-dir',str(extracted),
                            str(a.installer.resolve())],check=True)
            toolchain_provenance(extracted/'C$/JL/pi32/bin')
            extracted.rename(out)
    report=toolchain_provenance(tc)
    (out/'provenance.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Verified compiler at {tc}; installer not executed; no global PATH changes.')


if __name__=='__main__': main()
