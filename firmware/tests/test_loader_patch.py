from pathlib import Path
import sys
import struct
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'firmware/tools'))
from patch_stock_uart_loader import patch_loader, unpack_loader, patch_image, PATCHES
from package_ufw import container, crc


class LoaderPatchTests(unittest.TestCase):
    def test_only_selected_instructions_change(self):
        raw=(ROOT/'output/ufw_analysis/5o09fdkye1jo8/ota_loaders/uart_user.bin').read_bytes()
        original=unpack_loader(raw)
        patched,code=patch_loader(raw)
        expected=bytearray(original)
        for offset,before,after in PATCHES:
            self.assertEqual(original[offset:offset+len(before)],before)
            expected[offset:offset+len(before)]=after
        self.assertEqual(expected,code)
        self.assertEqual(unpack_loader(patched),code)
        with self.assertRaisesRegex(ValueError,'Unrecognized'):
            patch_loader(raw[:-1]+bytes([raw[-1]^1]))

    def test_package_preserves_every_other_component(self):
        source=ROOT/'5o09fdkye1jo8.ufw'
        before=source.read_bytes();_,original=container(before)
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'patched.ufw'
            patch_image(source,target)
            after=target.read_bytes();_,items=container(after)
            self.assertEqual(len(before),len(after))
            for old,new in zip(original,items):
                offset,size=new['offset'],new['size']
                payload=after[offset:offset+size]
                if new['name']!='ota.bin':
                    self.assertEqual(old['header'],new['header'])
                    self.assertEqual(before[offset:offset+size],payload)
                else:
                    self.assertEqual(crc(payload),new['crc'])
                    for pos in range(0,struct.unpack_from('<I',payload,4)[0],32):
                        self.assertEqual(crc(payload[pos+2:pos+32]),struct.unpack_from('<H',payload,pos)[0])
                        loc,n=struct.unpack_from('<II',payload,pos+4)
                        self.assertEqual(crc(payload[loc:loc+n]),struct.unpack_from('<H',payload,pos+2)[0])
            with self.assertRaisesRegex(ValueError,'overwrite'):
                patch_image(source,source)


if __name__=='__main__': unittest.main()
