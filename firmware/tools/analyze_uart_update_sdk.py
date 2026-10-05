"""Inspect the pinned BR23 updater and compile its ABI contract; never flash."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from build_br23 import commands, default_toolchain, toolchain_provenance
from setup_sdk import ROOT, load_lock, verify_sdk


def main():
    sdk = ROOT / ".cache/sdk"
    out = ROOT / "build/uart-investigation"
    evidence = ROOT.parent / "output/uart_update_analysis"
    out.mkdir(parents=True, exist_ok=True)
    (out / "generated").mkdir(exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    lock = load_lock()
    verified = verify_sdk(sdk, lock)
    toolchain = default_toolchain().resolve()
    provenance = toolchain_provenance(toolchain)
    suffix = ".exe" if os.name == "nt" else ""
    env = {k.upper(): v for k, v in os.environ.items()} if os.name == "nt" else dict(os.environ)
    executed = []

    def run(command):
        executed.append(list(map(str, command)))
        return subprocess.run(command, cwd=out, env=env, check=True,
                              capture_output=True, text=True).stdout

    archive = sdk / "include_lib/liba/br23/update.a"
    members = ["uart_update_driver.c.o", "download_loop.c.o", "update_main.c.o"]
    run([toolchain / ("llvm-ar" + suffix), "x", archive, *members])
    for member in members:
        run([toolchain / ("opt" + suffix), "-S", out / member,
             "-o", out / member.replace(".c.o", ".ll")])
    symbols = run([toolchain / ("llvm-nm" + suffix), "-A", archive])
    (evidence / "update_symbols.txt").write_text(symbols, encoding="utf-8")
    driver = (out / "uart_update_driver.ll").read_text()
    download = (out / "download_loop.ll").read_text()
    selected = [line for line in download.splitlines()
                if line.startswith("@update_loader_match_tab =")]
    if len(selected) != 1 or 'i16 23044, [16 x i8] c"uart_user.bin' not in selected[0]:
        raise ValueError("Unexpected UART loader mapping; inspect the SDK manually")
    if "store volatile i32 9600, i32* @baudrate" not in driver:
        raise ValueError("Unexpected UART initial baud")
    if "inttoptr (i32 1974528 to i32*)" not in driver:
        raise ValueError("Unexpected UART register base")
    excerpts = selected + [line for line in driver.splitlines() if any(
        token in line for token in ["store volatile i32 9600", "@request_irq(i8",
                                   "@gpio_uart_rx_input(i32 %"]) ]
    (evidence / "library_excerpts.txt").write_text("\n".join(excerpts) + "\n", encoding="utf-8")

    # Compile only. This file contains ABI assertions, not an update receiver.
    probe = out / "uart_update_abi.c"
    probe.write_text('''#define USE_SDFILE_NEW 1
#include "update.h"
#include "update_loader_download.h"
#include "uart_update.h"
#include "asm/br23.h"
_Static_assert(UART_UPDATA == 0x5a04, "update type");
_Static_assert(sizeof(UPDATA_UART) == 16, "UART handoff size");
_Static_assert(sizeof(UPDATA_PARM) == 80, "handoff header size");
_Static_assert(sizeof(update_mode_info_t) == 16, "library mode ABI");
_Static_assert(sizeof(update_op_api_t) == 28, "library callbacks ABI");
_Static_assert(sizeof(uart_update_cfg) == 6, "UART driver ABI");
_Static_assert(JL_UART1_BASE == 1974528, "library uses UART1");
int (*const checked_update_entry)(update_mode_info_t *) = app_active_update_task_init;
void (*const checked_handoff)(UPDATA_TYPE, void (*)(UPDATA_PARM *), void (*)(int)) = update_mode_api_v2;
''', encoding="utf-8")
    build, _ = commands(sdk, toolchain, out)
    run(build[0][:-4] + ["-Werror", "-c", str(probe), "-o", str(out / "uart_update_abi.o")])
    sources = [archive, sdk / "apps/common/update/uart_update.c",
               sdk / "apps/common/update/uart_update_master.c",
               sdk / "apps/common/update/update.c", sdk / "include_lib/update/update.h",
               sdk / "include_lib/update/uart_update.h",
               sdk / "include_lib/update/update_loader_download.h"]
    sources += list((sdk / "doc/功能模块说明文档/串口升级相关说明文档").glob("*.pdf"))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    report = {
        "sdk_commit": lock["commit"], "verified_sdk_api_files": verified,
        "toolchain": provenance,
        "inspection_tools_sha256": {name: sha(toolchain / (name + suffix))
                                    for name in ["opt", "llvm-nm"]},
        "source_sha256": {str(p.relative_to(ROOT.parent)): sha(p) for p in sources},
        "script_sha256": sha(Path(__file__)), "commands": executed,
        "uart_update_type": "0x5a04", "selected_loader": "uart_user.bin",
        "vendor_driver_uart": 1, "vendor_driver_initial_baud": 9600,
        "sava_uart_update_param_in_update_archive": "sava_uart_update_param" in symbols,
        "abi_probe_compiled": True, "updater_implemented": False,
        "application_linked": False, "device_flashed": False,
    }
    (evidence / "manifest.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Confirmed UART_UPDATA -> uart_user.bin; UART1 at 9600 initial baud.")
    print("BR23 ABI probe compiled. No application link or device operation.")
    print(evidence / "manifest.json")


if __name__ == "__main__":
    main()
