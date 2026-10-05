from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from uart_upload import Peer, Parser, frame


class HostPeerTests(unittest.TestCase):
    def test_stream_corruption_and_split_frames(self):
        p=Parser(); good=frame(b'\x01'); bad=bytearray(good); bad[-1]^=1
        self.assertEqual(p.feed(b'noise'+bad+good[:3]),[])
        self.assertEqual(p.feed(good[3:]+frame(b'\x05')),[b'\x01',b'\x05'])
        self.assertEqual(p.feed(b'\xaa\x55\xff\xff'+good),[b'\x01'])

    def test_two_stages_repeated_reads_and_status(self):
        data=bytes(range(256))*4; peer=Peer(data,256000)
        self.assertEqual(peer.reply(b'\x01'),b'\x01'+struct.pack('<I',256000))
        request=b'\x02'+struct.pack('<II',10,512)
        self.assertEqual(peer.reply(request),request+data[10:522])
        self.assertEqual(peer.reply(request),request+data[10:522])
        self.assertEqual(peer.reply(b'\x03\x80'),b'\x03\x80')
        self.assertFalse(peer.complete); self.assertTrue(peer.loader_staged)
        peer.reply(b'\x01')
        self.assertEqual(peer.reply(b'\x05'),b'\x05')
        self.assertEqual(peer.reply(b'\x04'+struct.pack('<I',1000)),b'\x04')
        self.assertEqual(peer.reply(b'\x03\x00'),b'\x03\x00')
        self.assertTrue(peer.complete)

    def test_bounds_and_error(self):
        p=Peer(b'x'*1024,256000)
        with self.assertRaises(ValueError): p.reply(b'\x05')
        p.reply(b'\x01')
        for offset,count in [(0,0),(0,513),(1000,25),(0xffffffff,512)]:
            with self.assertRaises(ValueError): p.reply(b'\x02'+struct.pack('<II',offset,count))
        for data in (b'',b'\x02',b'\x01\x00',b'\x04',b'\x06'):
            with self.assertRaises(ValueError): p.reply(data)
        self.assertEqual(p.reply(b'\x03\x02'),b'\x03\x02')
        self.assertEqual(p.error,2); self.assertFalse(p.complete)

    def test_sdk_start_baud_confirmation(self):
        peer=Peer(b'x'*1024,256000)
        response=b'\x01'+struct.pack('<I',256000)
        self.assertEqual(peer.reply(b'\x01'),response)
        self.assertEqual(peer.reply(response),response)
        self.assertEqual(peer.reply(b'\x01'+struct.pack('<I',9600)),response)
        for baud in (0,9599,1000001,0xffffffff):
            with self.assertRaises(ValueError):
                peer.reply(b'\x01'+struct.pack('<I',baud))


if __name__=='__main__': unittest.main()
