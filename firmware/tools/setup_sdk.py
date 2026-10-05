"""Fetch/verify the pinned vendor source; never execute SDK binaries."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load_lock():
    return json.loads((ROOT / "sdk.lock.json").read_text(encoding="utf-8"))


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_sdk(sdk, lock):
    for relative, expected in lock["verified_api_sha256"].items():
        path = sdk / relative
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"Pinned vendor file missing or changed: {relative}")
    return len(lock["verified_api_sha256"])


def archive_members(archive):
    """Strip the GitLab archive's common root; reject escapes and symlinks."""
    result, roots = [], set()
    for info in archive.infolist():
        name = info.filename
        parts = PurePosixPath(name).parts
        if "\\" in name or ":" in name or name.startswith("/") or ".." in parts:
            raise ValueError(f"Unsafe archive path: {name}")
        if not parts:
            continue
        roots.add(parts[0])
        if (info.external_attr >> 16) & 0o170000 == 0o120000:
            raise ValueError(f"Archive symlink rejected: {name}")
        if len(parts) > 1 and not info.is_dir():
            result.append((info, Path(*parts[1:])))
    if len(roots) != 1 or not result:
        raise ValueError("Expected one GitLab archive root with source files.")
    return result


def setup(archive_path, sdk, lock):
    if archive_path.stat().st_size != lock["archive_size_bytes"] or sha256(archive_path) != lock["archive_sha256"]:
        raise ValueError("Vendor archive size/SHA-256 does not match sdk.lock.json.")
    sdk.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        members = archive_members(archive)
        if sdk.exists():
            # Preserve existing contents. Never silently replace an SDK checkout.
            for info, relative in members:
                local = sdk / relative
                expected = hashlib.sha256(archive.read(info)).hexdigest()
                if not local.is_file() or sha256(local) != expected:
                    raise ValueError(f"Existing SDK differs at {relative}; use a fresh destination.")
        else:
            with tempfile.TemporaryDirectory(prefix="sdk-extract-", dir=sdk.parent) as temporary:
                staging = Path(temporary) / "source"
                staging.mkdir()
                for info, relative in members:
                    dest = staging / relative
                    if not dest.resolve().is_relative_to(staging.resolve()):
                        raise ValueError("Archive destination escapes staging directory.")
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info) as source, dest.open("wb") as target:
                        shutil.copyfileobj(source, target)
                verify_sdk(staging, lock)
                staging.rename(sdk)
    verify_sdk(sdk, lock)
    (sdk / ".ld2450-pinned-source.json").write_text(
        json.dumps({"commit": lock["commit"], "archive_sha256": lock["archive_sha256"]}, indent=2) + "\n",
        encoding="utf-8")
    return len(members)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ROOT / ".cache/sdk-source.zip")
    parser.add_argument("--sdk", type=Path, default=ROOT / ".cache/sdk")
    parser.add_argument("--download", action="store_true", help="Download the pinned public archive if missing.")
    args = parser.parse_args()
    lock = load_lock()
    try:
        if not args.archive.exists():
            if not args.download:
                raise ValueError("SDK archive absent; pass --download or --archive PATH.")
            args.archive.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(prefix="sdk-download-", dir=args.archive.parent, delete=False) as stream:
                temporary = Path(stream.name)
                try:
                    with urllib.request.urlopen(lock["archive_url"], timeout=60) as response:
                        shutil.copyfileobj(response, stream)
                except BaseException:
                    stream.close()
                    temporary.unlink()
                    raise
            try:
                if temporary.stat().st_size != lock["archive_size_bytes"] or sha256(temporary) != lock["archive_sha256"]:
                    raise ValueError("Downloaded archive hash differs from the pinned source.")
                temporary.rename(args.archive)
            finally:
                if temporary.exists():
                    temporary.unlink()
        count = setup(args.archive.resolve(), args.sdk.resolve(), lock)
        print(f"Verified {count} vendor files at commit {lock['commit']}: {args.sdk}")
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        parser.exit(1, f"SDK setup failed: {error}\n")


if __name__ == "__main__":
    main()
