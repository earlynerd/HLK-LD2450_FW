; Original vendor disassembler output. Addresses are VMAs; file offset = VMA - 0x1e00120.
; Relative branch/call numbers are disassembler operands, not absolute addresses.
; tbb/tbh inline table bytes below are DATA despite objdump instruction rendering.

; region 0x1e11618..0x1e116c2
 1e11618:    e0 e0 80 e8       	r0 = r14 + 0x400000
 1e1161c:    80 33             	[sp+76] = r0
 1e1161e:    0f f8 50 00       	if (r15 == 0) goto 160
 1e11622:    bf ea 14 fc       	call -2008
 1e11626:    41 e0 2e 02       	r1 = 558
 1e1162a:    d8 ed 78 11       	r1 = h[r7+r1<<1] (u)
 1e1162e:    80 42             	if (r0 != 0) goto 4
 1e11630:    91 f8 47 fe       	if (r1 != 255) goto 142
 1e11634:    32 e1 60 1f       	r2 = r1 + -160
 1e11638:    82 fc 2f 22       	if (r2 <= 17) goto 94
 1e1163c:    32 e1 80 1f       	r2 = r1 + -128
 1e11640:    82 fc 4f 06       	if (r2 <= 3) goto 158
 1e11644:    00 ff 00 10 c7 01 	if (r1 == 0) goto 910
 1e1164a:    00 ff 01 10 2b 01 	if (r1 == 1) goto 598
 1e11650:    00 ff 02 10 e2 01 	if (r1 == 2) goto 964
 1e11656:    00 ff 10 10 20 02 	if (r1 == 16) goto 1088
 1e1165c:    00 ff 90 10 28 02 	if (r1 == 144) goto 1104
 1e11662:    00 ff 91 10 2e 02 	if (r1 == 145) goto 1116
 1e11668:    42 20             	r2 = 0
 1e1166a:    00 ff c1 10 78 01 	if (r1 == 193) goto 752
 1e11670:    00 ff c2 10 31 02 	if (r1 == 194) goto 1122
 1e11676:    00 ff fe 10 a7 01 	if (r1 == 254) goto 846
 1e1167c:    91 f8 21 fe       	if (r1 != 255) goto 66
 1e11680:    52 ee 70 e5       	b[r7+80] = r14
 1e11684:    8f f9 30 07       	if (r15 < 3) goto -416
 1e11688:    40 e0 2f 02       	r0 = 559
 1e1168c:    d8 ed 78 00       	r0 = h[r7+r0<<1] (u)
 1e11690:    50 ed 71 03       	h[r7+48] = r0
 1e11694:    c8 8c             	r0 = sp + 76
 1e11696:    41 22             	r1 = 2
 1e11698:    97 8a             	goto -428
 1e1169a:    20 a1             	r0 = r2 << 1
 1e1169c:    10 01             	tbh [r0]
 1e1169e:    18 00              <unknown instruction>
 1e116a0:    2f 00             	btbclr
 1e116a2:    51 00              <unknown instruction>
 1e116a4:    71 00              <unknown instruction>
 1e116a6:    77 00              <unknown instruction>
 1e116a8:    8f 00              <unknown instruction>
 1e116aa:    12 00              <unknown instruction>
 1e116ac:    12 00              <unknown instruction>
 1e116ae:    12 00              <unknown instruction>
 1e116b0:    12 00              <unknown instruction>
 1e116b2:    12 00              <unknown instruction>
 1e116b4:    12 00              <unknown instruction>
 1e116b6:    aa 00             	swi 2
 1e116b8:    12 00              <unknown instruction>
 1e116ba:    12 00              <unknown instruction>
 1e116bc:    12 00              <unknown instruction>
 1e116be:    bf 00             	testset b[r15]
 1e116c0:    e1 00             	cli r1
