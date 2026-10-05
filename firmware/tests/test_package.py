"""Stock identity roundtrips and all-variant replacement, without a compiler."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from package_ufw import package, container, flash_view, FLASH_TYPES


class PackageTests(unittest.TestCase):
    def test_stock_identity_and_replacement(self):
        for stem in ('5o09fdkye1jo8', 'oncstzcza54pd'):
            with self.subTest(template=stem), tempfile.TemporaryDirectory() as tmp:
                tmp = Path(tmp)
                template = ROOT.parent / (stem + '.ufw')
                stock = ROOT.parent / f'output/ufw_analysis/{stem}/flash_images/flash.bin/files/app.bin'
                original = template.read_bytes()
                result = tmp / 'update.ufw'
                package(template, stock, result)
                self.assertEqual(original, result.read_bytes(), 'No-op must be byte identical')
                app = tmp / 'app.bin'; app.write_bytes(bytes(range(256)) * 5)
                package(template, app, result)
                changed = result.read_bytes()
                _, before = container(original); _, after = container(changed)
                seen = 0
                for old, new in zip(before, after):
                    off, n = new['offset'], new['size']
                    if new['type'] in FLASH_TYPES:
                        seen += 1
                        base, area, _, (_, entry) = flash_view(changed[off:off+n])
                        self.assertEqual(changed[off:off+base], original[off:off+base])
                        got = area[entry['offset']:entry['offset']+entry['size']]
                        self.assertEqual(got[:1280], app.read_bytes())
                        self.assertEqual(got[1280:], b'\xff' * (len(got)-1280))
                    else:
                        self.assertEqual(old, new)
                        self.assertEqual(changed[off:off+n], original[off:off+n])
                self.assertEqual(seen, 4)

    def test_reject_unpinned_oversize_empty_and_input_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp); app = tmp/'app'; out = tmp/'out'
            template = ROOT.parent/'5o09fdkye1jo8.ufw'
            for content in (b'', b'x'*182761):
                app.write_bytes(content)
                with self.assertRaises(ValueError): package(template, app, out)
                self.assertFalse(out.exists())
            app.write_bytes(b'valid small application')
            with self.assertRaises(ValueError): package(template, app, template)
            with self.assertRaises(ValueError): package(template, app, app)
            corrupt = tmp/'corrupt'; bad = bytearray(template.read_bytes()); bad[-1] ^= 1
            corrupt.write_bytes(bad)
            with self.assertRaises(ValueError): package(corrupt, app, out)


if __name__ == '__main__': unittest.main()
