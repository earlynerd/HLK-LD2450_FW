"""Exercise source-integrity and extraction boundaries without network access."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from setup_sdk import archive_members, setup, verify_sdk
from generate_radar_config import customize, generate, load_profiles, table_bytes


class SourceIntegrityTests(unittest.TestCase):
    def test_archive_paths_and_symlinks_are_rejected(self):
        for name in ["sdk/../escape.c", "/escape.c", "C:/escape.c", "sdk\\escape.c"]:
            with self.subTest(name=name):
                raw = io.BytesIO()
                with zipfile.ZipFile(raw, "w") as archive:
                    archive.writestr(name, b"data")
                with zipfile.ZipFile(raw) as archive:
                    # ZipInfo normalizes backslashes on Windows. Also exercise
                    # the validator directly with the unnormalized spelling.
                    archive.infolist()[0].filename = name
                    with self.assertRaises(ValueError):
                        archive_members(archive)
        raw = io.BytesIO()
        with zipfile.ZipFile(raw, "w") as archive:
            info = zipfile.ZipInfo("sdk/link")
            info.external_attr = 0o120777 << 16
            archive.writestr(info, "../escape")
        with zipfile.ZipFile(raw) as archive, self.assertRaises(ValueError):
            archive_members(archive)

    def test_verified_setup_preserves_a_changed_checkout(self):
        base = ROOT / "build/tool-tests"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            root = Path(directory)
            source, sdk = root / "source.zip", root / "sdk"
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("vendor-root/api.h", b"pinned API")
            lock = {"commit": "fixture", "archive_size_bytes": source.stat().st_size,
                    "archive_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    "verified_api_sha256": {"api.h": hashlib.sha256(b"pinned API").hexdigest()}}
            self.assertEqual(setup(source, sdk, lock), 1)
            self.assertEqual(verify_sdk(sdk, lock), 1)
            (sdk / "api.h").write_bytes(b"local changes")
            with self.assertRaises(ValueError):
                setup(source, sdk, lock)
            self.assertEqual((sdk / "api.h").read_bytes(), b"local changes")
            with self.assertRaises(ValueError):
                verify_sdk(sdk, lock)
            fresh = root / "must-not-be-created"
            lock["archive_sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                setup(source, fresh, lock)
            self.assertFalse(fresh.exists())

    def test_captured_fixture_hashes(self):
        fixtures = ROOT / "tests/fixtures"
        manifest = json.loads((fixtures / "manifest.json").read_text())
        for entry in manifest["files"]:
            raw = (fixtures / entry["file"]).read_bytes()
            self.assertEqual(len(raw), entry["bytes"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])


class RadarConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles, cls.provenance = load_profiles()

    def test_baselines_match_recovered_binary_tables(self):
        for name, profile in self.profiles.items():
            original = ROOT.parent / "output/radar_init" / (name + ".bin")
            self.assertEqual(table_bytes(profile), original.read_bytes())
        config = json.loads((ROOT / "config/radar_baseline_mode2.json").read_text())
        writes, changes = customize(config, self.profiles)
        self.assertEqual(writes, self.profiles["mode_2_ram_initial"])
        self.assertFalse(changes)

    def test_occurrence_override_preserves_earlier_write(self):
        config = json.loads((ROOT / "config/radar_no_idle_powerdown.json").read_text())
        writes, changes = customize(config, self.profiles)
        baseline = self.profiles["mode_2_ram_initial"]
        self.assertEqual(writes[1]["value"], 0x0004)
        self.assertEqual(writes[78]["value"], 0xc854)
        self.assertEqual([i + 1 for i, (a, b) in enumerate(zip(baseline, writes)) if a != b], [79])
        self.assertEqual(changes[0]["old"], "0xC844")
        self.assertEqual(changes[0]["stage"], "post_spi")
        self.assertEqual(self.profiles["mode_2_ram_initial"][78]["value"], 0xc844)

    def test_guards_and_bad_configs(self):
        import copy
        original = json.loads((ROOT / "config/radar_no_idle_powerdown.json").read_text())
        changes = [("sequence", 0), ("sequence", 81), ("register", "0x40"),
                   ("expected", "0x0004"), ("value", "0x10000"),
                   ("value", True), ("value", "0xC844"), ("reason", "")]
        for field, value in changes:
            with self.subTest(field=field, value=value):
                config = copy.deepcopy(original)
                config["overrides"][0][field] = value
                with self.assertRaises(ValueError):
                    customize(config, self.profiles)
        config = copy.deepcopy(original)
        config["overrides"].append(dict(config["overrides"][0]))
        with self.assertRaises(ValueError):
            customize(config, self.profiles)
        for field, value in [("name", 'bad"name'), ("base_profile", "unknown"), ("overrides", {})]:
            config = copy.deepcopy(original); config[field] = value
            with self.assertRaises(ValueError):
                customize(config, self.profiles)

    def test_generated_bytes_and_provenance(self):
        base = ROOT / "build/tool-tests"
        base.mkdir(parents=True, exist_ok=True)
        config_path = ROOT / "config/radar_no_idle_powerdown.json"
        with tempfile.TemporaryDirectory(dir=base) as directory:
            out = Path(directory)
            info = generate(config_path, out)
            records = (out / "radar_config_records.bin").read_bytes()
            wire = (out / "radar_config_wire_inferred.bin").read_bytes()
            self.assertEqual(len(records), 320)
            self.assertEqual(len(wire), 320)
            self.assertEqual(wire[78 * 4:79 * 4], bytes.fromhex("40 41 c8 54"))
            self.assertEqual(hashlib.sha256(records).hexdigest(), info["table_sha256"])
            self.assertEqual(info["config_sha256"], hashlib.sha256(config_path.read_bytes()).hexdigest())
            self.assertFalse(info["target_built"])
            self.assertFalse(info["device_tested"])
            self.assertEqual(len(info["sources"]), 2)
            self.assertIn('"mode2-no-idle-powerdown-candidate"',
                          (out / "radar_config_generated.c").read_text())


if __name__ == "__main__":
    unittest.main()
