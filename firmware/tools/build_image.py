"""Compile and link the minimal BR23 application; never invoke a downloader."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import struct
from build_br23 import commands, default_toolchain, toolchain_provenance
from setup_sdk import ROOT, load_lock, verify_sdk
from generate_radar_config import generate
from package_ufw import package
from audit_image import audit_startup
from audit_runtime import audit_runtime


def application_bytes(elf):
    raw=elf.read_bytes()
    if raw[:6] != b'\x7fELF\x01\x01': raise ValueError('Expected little-endian ELF32')
    if struct.unpack_from('<I',raw,24)[0] != 0x1e00120: raise ValueError('Wrong entry address')
    off=struct.unpack_from('<I',raw,32)[0]
    entsize,count,names_index=struct.unpack_from('<HHH',raw,46)
    sections=[struct.unpack_from('<IIIIIIIIII',raw,off+i*entsize) for i in range(count)]
    ns=sections[names_index]; names=raw[ns[4]:ns[4]+ns[5]]
    by_name={names[s[0]:].split(b'\0',1)[0].decode():s for s in sections}
    order=['.text','.data','.data_code','.overlay_aec','.overlay_wav','.overlay_ape',
           '.overlay_flac','.overlay_m4a','.overlay_amr','.overlay_dts','.overlay_fm',
           '.overlay_mp3','.overlay_wma']
    result=bytearray()
    for name,s in by_name.items():
        # SDK startup populates these RAM reservations; download.bat omits them.
        if s[2] & 2 and s[1] != 8 and s[5] and name not in order + ['.irq_stack','.mmu_tlb']:
            raise ValueError(f'Unpackaged allocated section: {name}')
    for name in order:
        if name not in by_name: continue
        s=by_name[name]
        if name.startswith('.overlay') and s[5] > 4:
            raise ValueError('Unexpected populated audio overlay in minimal application')
        if s[1]==8: raise ValueError('Cannot put BSS in application image')
        result.extend(raw[s[4]:s[4]+s[5]])
    return bytes(result)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sdk', type=Path, default=ROOT / '.cache/sdk')
    ap.add_argument('--toolchain', type=Path, default=default_toolchain())
    ap.add_argument('--out', type=Path)
    ap.add_argument('--application', choices=['radar', 'hello'], default='radar')
    ap.add_argument('--radar-config', type=Path, default=ROOT / 'config/radar_baseline_mode2.json')
    ap.add_argument('--template',type=Path,default=ROOT.parent/'5o09fdkye1jo8.ufw')
    a = ap.parse_args(); sdk=a.sdk.resolve(); tc=a.toolchain.resolve()
    out=(a.out or ROOT / ('build/hello' if a.application == 'hello' else 'build/image')).resolve()
    out.mkdir(parents=True,exist_ok=True)
    verify_sdk(sdk,load_lock()); provenance=toolchain_provenance(tc)
    if a.application == 'hello':
        (out/'generated').mkdir(exist_ok=True)
        profile={'name': 'hello-world-with-uart-updater'}
    else:
        profile=generate(a.radar_config,out/'generated')
    build,_=commands(sdk,tc,out)
    flags=build[0][1:-4]
    flags=['-I',str(ROOT/'target/br23/image'),*flags,'-DLD2450_EARLY_CONSOLE',
           '-DUSE_SDFILE_NEW=1','-DVFS_ENABLE=1','-DSDFILE_STORAGE=1',
           '-DVFS_FILE_POOL_NUM_CONFIG=4','-DFS_VERSION=0x020001',
           '-DSDFILE_VERSION=0x020000','-DVM_MAX_SIZE_CONFIG=65536',
           '-DVM_ITEM_MAX_NUM=256','-DCONFIG_ITEM_FORMAT_VM',
           '-DCONFIG_UPDATA_ENABLE','-DCONFIG_OTA_UPDATA_ENABLE',
           '-DEVENT_HANDLER_NUM_CONFIG=2','-DEVENT_POOL_SIZE_CONFIG=256',
           '-DTIMER_POOL_NUM_CONFIG=15','-DAPP_ASYNC_POOL_NUM_CONFIG=0']
    if a.application == 'hello': flags += ['-DLD2450_HELLO_WORLD']
    env={k.upper():v for k,v in os.environ.items()}
    log=[]
    def run(cmd):
        log.append(list(map(str,cmd)))
        (out/'commands.json').write_text(json.dumps(log,indent=2)+'\n')
        subprocess.run(cmd,cwd=out,env=env,check=True)
    sources=[ROOT/p for p in ['src/uart_update_protocol.c',
        'target/br23/peripherals.c','target/br23/image/main.c',
        'target/br23/image/config.c','target/br23/image/uart_loader.c',
        'target/br23/image/bringup.c','target/br23/image/console.c','target/br23/image/board.c']]
    if a.application == 'radar':
        sources += [ROOT/p for p in ['src/radar_wire.c','src/radar_init.c','src/app.c']]
        sources += [out/'generated/radar_config_generated.c']
    sources += [sdk/p for p in ['cpu/br23/setup.c','cpu/br23/uart_dev.c',
        'cpu/br23/charge.c','cpu/br23/pwm_led.c',
        'apps/soundbox/log_config/lib_system_config.c','apps/soundbox/log_config/lib_driver_config.c',
        'apps/soundbox/log_config/lib_update_config.c']]
    objects=[]
    for i,src in enumerate(sources):
        obj=out/f'{i}_{src.stem}.o';objects.append(obj)
        # Keep the pinned SDK untouched; project setup_arch applies clock
        # constraints before invoking its complete bring-up sequence.
        source_flags = ['-Dsetup_arch=ld2450_sdk_setup_arch'] if src == sdk/'cpu/br23/setup.c' else []
        run([tc/'clang.exe',*flags,*source_flags,'-c',src,'-o',obj])
    run([tc/'clang.exe',*flags,'-D__LD__','-E','-P','-x','c',sdk/'cpu/br23/sdk_ld.c','-o',out/'sdk.ld'])
    ld=(out/'sdk.ld').read_text()
    if 'ORIGIN = 0x1E00100' not in ld: raise ValueError('Unexpected SDK linker layout')
    (out/'sdk.ld').write_text(ld.replace('ORIGIN = 0x1E00100','ORIGIN = 0x1E00120'))
    (out/'sdk_used_list.used').write_text('sdfile_vfs_ops\n' +
        ('ld2450_build_radar_profile\n' if a.application == 'radar' else ''))
    libs=[sdk/f'include_lib/liba/br23/{x}.a' for x in ['cpu','system','update']]
    syslibs=tc.parent/'pi32v2-lib/r3'
    link=[tc/'pi32v2-lto-wrapper.exe','-o',out/'sdk.elf',*objects,
          '--start-group',*libs,syslibs/'libc.a',syslibs/'libm.a',syslibs/'libcompiler-rt.a','--end-group',
          '-T',out/'sdk.ld','-L',sdk/'cpu/br23','-M='+str(out/'sdk.map'),
          '--plugin-opt=mcpu=r3','--plugin-opt=-mattr=+fprev1',
          '--plugin-opt=-used-symbol-file='+str(out/'sdk_used_list.used'),
          '--gc-sections','--dont-complain-call-overflow']
    run(link)
    app=out/'app.bin'; app.write_bytes(application_bytes(out/'sdk.elf'))
    startup_audit = audit_startup(out/'sdk.elf', app.read_bytes())
    disassemble = [str(tc/'llvm-objdump.exe'), '-d', str(out/'sdk.elf')]
    log.append(disassemble)
    (out/'commands.json').write_text(json.dumps(log,indent=2)+'\n')
    disassembly = subprocess.run(disassemble, cwd=out, env=env, check=True,
                                 capture_output=True, text=True).stdout
    (out/'sdk-disasm.txt').write_text(disassembly)
    runtime_audit = audit_runtime(out/'sdk.elf', disassembly)
    if a.application == 'radar':
        table=(out/'generated/radar_config_records.bin').read_bytes()
        if table not in app.read_bytes(): raise ValueError('Configured radar table was removed during link')
    packaged=package(a.template.resolve(),app,out/'update.ufw')
    inputs = set(sources + libs + list(syslibs.glob('*.a')))
    inputs.update(ROOT.glob('include/*.h'))
    inputs.update((ROOT/'target/br23').rglob('*.h'))
    inputs.update([sdk/'Makefile', sdk/'cpu/br23/sdk_ld.c', sdk/'cpu/br23/maskrom_stubs.ld',
                   sdk/'cpu/br23/sdk_used_list.c', ROOT/'sdk.lock.json', ROOT/'toolchain.lock.json',
                   Path(__file__), ROOT/'tools/build_br23.py', ROOT/'tools/package_ufw.py',
                   ROOT/'tools/audit_image.py',
                   ROOT/'tools/audit_runtime.py', tc/'llvm-objdump.exe',
                   ROOT/'tools/generate_radar_config.py',a.radar_config.resolve()])
    (out/'build-result.json').write_text(json.dumps({'image_linked':True,'device_flashed':False,
        'toolchain':provenance,'profile':profile,'package':packaged,
        'sdk_commit':load_lock()['commit'], 'application':a.application,
        'startup_audit': startup_audit,
        'runtime_audit': runtime_audit,
        'radar_table_retained':a.application == 'radar',
        'source_and_link_inputs_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)},
        'elf_sha256':hashlib.sha256((out/'sdk.elf').read_bytes()).hexdigest()},indent=2)+'\n')
    print(f'Linked {len(app.read_bytes())} application bytes; packaged {out / "update.ufw"}')
    print('All four flash variants verified; no device operation performed.')

if __name__=='__main__': main()
