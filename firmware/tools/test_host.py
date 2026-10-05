"""Build and run the C tests without invoking any vendor download tools."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generator", default="Visual Studio 17 2022" if os.name == "nt" else "Unix Makefiles")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build/host")
    parser.add_argument("--radar-config", type=Path, default=ROOT / "config/radar_baseline_mode2.json")
    args = parser.parse_args()
    cmake, ctest = shutil.which("cmake"), shutil.which("ctest")
    if not cmake or not ctest:
        raise SystemExit("CMake and CTest must be installed for host validation.")
    # Some Windows parent processes supply both PATH and Path. .NET/MSBuild
    # rejects that environment; normalize names only for these child builds.
    env = {k.upper(): v for k, v in os.environ.items()} if os.name == "nt" else dict(os.environ)
    configure = [cmake, "-S", str(ROOT), "-B", str(args.build_dir), "-G", args.generator]
    configure += [f"-DLD2450_RADAR_CONFIG={args.radar_config.resolve()}",
                  f"-DPython3_EXECUTABLE={sys.executable}"]
    if args.generator.startswith("Visual Studio"):
        configure += ["-A", "x64"]
    commands = [configure, [cmake, "--build", str(args.build_dir), "--config", "Debug"],
                [ctest, "--test-dir", str(args.build_dir), "-C", "Debug", "--output-on-failure"],
                [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", "test_tools.py", "-v"]]
    for command in commands:
        subprocess.run(command, env=env, check=True)


if __name__ == "__main__":
    main()
