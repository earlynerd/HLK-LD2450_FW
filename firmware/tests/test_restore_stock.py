from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from package_ufw import container
import restore_stock as rs


class RestoreStockTests(unittest.TestCase):
    def test_restore_image_is_stock_with_only_the_loader_changed(self):
        with tempfile.TemporaryDirectory() as d:
            data=rs.build(Path(d))
        stock=rs.STOCK.read_bytes()
        _,items=container(stock); _,restored=container(data)
        changed=[a['name'] for a,b in zip(items,restored)
                 if stock[a['offset']:a['offset']+a['size']]!=data[b['offset']:b['offset']+b['size']]]
        self.assertEqual(changed,['ota.bin'])

    def test_bench_report_frame_and_version_reply(self):
        # Captured from stock V2.14 after the 2026-10-08 restore, at 9600 baud.
        frame=bytes.fromhex('aaff03007500bd8100006801'+'00'*16+'55cc')
        self.assertEqual(rs.report_frames(b'\x00'+frame+frame[:10]),
                         [[dict(x_mm=-117,y_mm=445,speed_cms=0,resolution_mm=360)]])
        ack=rs.CMD_HEAD+bytes.fromhex('0c00a00100000001140212241125')+rs.CMD_TAIL
        self.assertEqual(rs.version(b'junk'+ack),'V2.14.25112412')
        self.assertIsNone(rs.version(ack[:-1]))
        self.assertEqual(rs.command(0xff,b'\x01\x00').hex(),'fdfcfbfa0400ff00010004030201')


if __name__=='__main__': unittest.main()
