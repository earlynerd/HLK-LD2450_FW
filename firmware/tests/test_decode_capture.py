from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from decode_capture import records, decode

class CaptureDecoderTests(unittest.TestCase):
    def test_real_fixture_and_corruption(self):
        raw=(Path(__file__).parent/'fixtures/steady-chirp0.bin').read_bytes()
        found=records(b'junk'+raw+b'junk')
        self.assertEqual([(x['offset'],x['pairs'],x['rx'],x['checksum']) for x in found],[(4,512,1,'07e6')])
        bad=bytearray(raw);bad[5]^=1
        self.assertEqual(records(bad),[])
        self.assertEqual(records(raw[:-1]),[])
    def test_missing_line_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'Missing/reordered'):
                decode('CAPTURE BEGIN lane=0 size=8192 complete=1\nDATA 0 0020 '+'00'*32,Path(d))
    def test_two_complete_serial_dumps(self):
        for size in (8192,32896):
            self.check_dump_size(size)
    def check_dump_size(self,size):
        lines=[]
        for lane in range(2):
            lines.append(f'CAPTURE BEGIN lane={lane} size={size} complete=0')
            lines.extend(f'DATA {lane} {offset:04x} '+('a5'*32) for offset in range(0,size,32))
            lines.append(f'CAPTURE END lane={lane}')
        with tempfile.TemporaryDirectory() as d:
            r=decode('\n'.join(lines),Path(d))
            self.assertTrue(r['lanes_identical'])
            self.assertFalse(r['lanes'][0]['dma_complete'])
            self.assertEqual(r['lanes'][0]['valid_records'],[])
