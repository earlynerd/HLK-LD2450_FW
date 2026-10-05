"""Compile the firmware component for BR23; never link/download/flash a board."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from setup_sdk import ROOT, load_lock, verify_sdk
from generate_radar_config import generate

SOURCES = ["src/radar_wire.c", "src/radar_init.c", "src/app.c", "target/br23/peripherals.c"]


def default_toolchain():
    local = ROOT / ".cache/toolchain/extracted-2.5.2/C$/JL/pi32/bin"
    if os.name == "nt" and (local / "clang.exe").is_file():
        return local
    return Path("C:/JL/pi32/bin" if os.name == "nt" else "/opt/jieli/pi32v2/bin")


def toolchain_provenance(toolchain):
    toolchain = toolchain.resolve()
    lock = json.loads((ROOT / "toolchain.lock.json").read_text(encoding="utf-8-sig"))
    if toolchain != (ROOT / lock["local_bin"]).resolve():
        return {"bin": str(toolchain), "matches_project_lock": False}
    for name, expected in lock["tool_files_sha256"].items():
        actual = hashlib.sha256((toolchain.parent / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Local toolchain hash mismatch: {name}")
    return {"bin": str(toolchain), "matches_project_lock": True,
            "version": lock["version"], "installer_sha256": lock["installer_sha256"],
            "tool_files_sha256": lock["tool_files_sha256"]}


def commands(sdk, toolchain, out):
    makefile = (sdk / "Makefile").read_text(encoding="utf-8")
    includes_block = makefile.split("INCLUDES :=", 1)[1].split("\n#", 1)[0]
    includes = re.findall(r"-I([^\s\\]+)", includes_block)
    flags = ["-target", "pi32v2", "-mcpu=r3", "-integrated-as", "-std=gnu99",
             "-Oz", "-g", "-flto", "-fno-common", "-fms-extensions",
             "-fallow-pointer-null", "-fprefer-gnu-section", "-DSUPPORT_MS_EXTENSIONS",
             "-DCONFIG_CPU_BR23", "-DCONFIG_FREE_RTOS_ENABLE", "-D__GCC_PI32V2__"]
    # Stock Makefile lists several optional directories absent from this
    # release archive. GCC/Clang also ignore those nonexistent search paths.
    for path in [ROOT / "include", ROOT / "target/br23", out / "generated", *[sdk / p for p in includes if (sdk / p).is_dir()]]:
        if not path.is_dir():
            raise ValueError(f"Include directory absent: {path}")
        flags += ["-I", str(path)]
    sys_include = toolchain.parent / ("pi32v2-include" if os.name == "nt" else "include")
    flags += ["-isystem", str(sys_include)]
    compiler = toolchain / ("clang.exe" if os.name == "nt" else "clang")
    archiver = toolchain / ("llvm-ar.exe" if os.name == "nt" else "lto-ar")
    sources = [ROOT / source for source in SOURCES] + [out / "generated/radar_config_generated.c"]
    objects = [out / (source.stem + ".o") for source in sources]
    build = [[str(compiler), *flags, "-c", str(source), "-o", str(obj)]
             for source, obj in zip(sources, objects)]
    build.append([str(archiver), "rcs", str(out / "libld2450.a"), *map(str, objects)])
    return build, [compiler, archiver, sys_include]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", type=Path, default=ROOT / ".cache/sdk")
    parser.add_argument("--toolchain", type=Path, default=default_toolchain())
    parser.add_argument("--out", type=Path, default=ROOT / "build/br23")
    parser.add_argument("--radar-config", type=Path, default=ROOT / "config/radar_baseline_mode2.json",
                        help="Recovered baseline plus guarded, occurrence-specific overrides.")
    parser.add_argument("--plan", action="store_true", help="Validate SDK and save commands; do not claim a target build.")
    args = parser.parse_args()
    lock = load_lock()
    try:
        checked = verify_sdk(args.sdk, lock)
        radar_config = generate(args.radar_config, args.out / "generated")
        build, required = commands(args.sdk.resolve(), args.toolchain.resolve(), args.out.resolve())
        missing = [str(p) for p in required if not p.exists()]
        plan = {"sdk_commit": lock["commit"], "verified_vendor_files": checked,
                "radar_config": radar_config,
                "target_built": False, "image_linked": False, "device_flashed": False,
                "commands": build, "missing_toolchain_paths": missing,
                "toolchain": toolchain_provenance(args.toolchain),
                "source_sha256": {str(ROOT / p): hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                                  for p in SOURCES}}
        if missing and not args.plan:
            raise ValueError("JieLi target toolchain unavailable: " + ", ".join(missing))
        args.out.mkdir(parents=True, exist_ok=True)
        if args.plan:
            (args.out / "build-plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
            print(f"SDK/API checks passed ({checked} pinned files); target build not performed.")
            if missing:
                print("Missing JieLi toolchain: " + ", ".join(missing))
            print(f"Compile/archive commands saved in {args.out / 'build-plan.json'}")
            return
        env = {k.upper(): v for k, v in os.environ.items()} if os.name == "nt" else dict(os.environ)
        for command in build:
            subprocess.run(command, check=True, env=env, cwd=ROOT)
        plan["target_built"] = True
        archive = args.out / "libld2450.a"
        plan["component_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
        plan["component_size_bytes"] = archive.stat().st_size
        (args.out / "build-result.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        print(f"BR23 component built: {args.out / 'libld2450.a'} (no device download)")
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"BR23 component build failed: {error}\n")


if __name__ == "__main__":
    main()
