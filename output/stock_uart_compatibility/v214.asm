; Original vendor disassembler output. Addresses are VMAs; file offset = VMA - 0x1e00120.
; Relative branch/call numbers are disassembler operands, not absolute addresses.
; tbb/tbh inline table bytes below are DATA despite objdump instruction rendering.

; region 0x1e11c20..0x1e11c38
 1e11c20:    c7 14             	r15 = 0
 1e11c22:    4c e0 9a 04       	r12 = 1178
 1e11c26:    c9 ff 40 73 00 00 	r9 = 29504
 1e11c2c:    46 e0 4e 02       	r6 = 590
 1e11c30:    45 21             	r5 = 1
 1e11c32:    6f 81             	r7 = r6 + 1
 1e11c34:    c0 14             	r8 = 0
 1e11c36:    34 8c             	goto 216

; region 0x1e11df4..0x1e11ec8
 1e11df4:    e0 e0 80 58       	r0 = r5 + 0x400000
 1e11df8:    80 35             	[sp+84] = r0
 1e11dfa:    37 48             	if (r7 == 0) goto 208
 1e11dfc:    bf ea 5f f8       	call -3906
 1e11e00:    41 e0 32 02       	r1 = 562
 1e11e04:    d8 ed 98 11       	r1 = h[r9+r1<<1] (u)
 1e11e08:    80 42             	if (r0 != 0) goto 4
 1e11e0a:    91 f8 5f fe       	if (r1 != 255) goto 190
 1e11e0e:    32 e1 60 1f       	r2 = r1 + -160
 1e11e12:    82 fc 34 48       	if (r2 <= 36) goto 104
 1e11e16:    32 e1 80 1f       	r2 = r1 + -128
 1e11e1a:    82 fc 64 06       	if (r2 <= 3) goto 200
 1e11e1e:    00 ff 00 10 0d 02 	if (r1 == 0) goto 1050
 1e11e24:    00 ff 01 10 2b 02 	if (r1 == 1) goto 1110
 1e11e2a:    00 ff 02 10 8f 02 	if (r1 == 2) goto 1310
 1e11e30:    00 ff 10 10 d4 02 	if (r1 == 16) goto 1448
 1e11e36:    00 ff 30 10 de 02 	if (r1 == 48) goto 1468
 1e11e3c:    00 ff 31 10 e9 02 	if (r1 == 49) goto 1490
 1e11e42:    00 ff 70 10 eb 02 	if (r1 == 112) goto 1494
 1e11e48:    00 ff 71 10 04 03 	if (r1 == 113) goto 1544
 1e11e4e:    00 ff 90 10 20 03 	if (r1 == 144) goto 1600
 1e11e54:    00 ff 91 10 27 03 	if (r1 == 145) goto 1614
 1e11e5a:    00 ff fe 10 2f 03 	if (r1 == 254) goto 1630
 1e11e60:    91 f8 34 fe       	if (r1 != 255) goto 104
 1e11e64:    52 ee 94 55       	b[r9+84] = r5
 1e11e68:    87 f9 2f 07       	if (r7 < 3) goto -418
 1e11e6c:    40 e0 33 02       	r0 = 563
 1e11e70:    d8 ed 98 00       	r0 = h[r9+r0<<1] (u)
 1e11e74:    50 ed 91 03       	h[r9+48] = r0
 1e11e78:    c8 94             	r0 = sp + 84
 1e11e7a:    41 22             	r1 = 2
 1e11e7c:    97 89             	goto -430
 1e11e7e:    20 a1             	r0 = r2 << 1
 1e11e80:    10 01             	tbh [r0]
 1e11e82:    27 00             	btbclr
 1e11e84:    3e 00             	ssync
 1e11e86:    46 01              <unknown instruction>
 1e11e88:    4c 01              <unknown instruction>
 1e11e8a:    52 01              <unknown instruction>
 1e11e8c:    62 00              <unknown instruction>
 1e11e8e:    25 00              <unknown instruction>
 1e11e90:    25 00              <unknown instruction>
 1e11e92:    25 00              <unknown instruction>
 1e11e94:    25 00              <unknown instruction>
 1e11e96:    6a 01              <unknown instruction>
 1e11e98:    25 00              <unknown instruction>
 1e11e9a:    9f 01              <unknown instruction>
 1e11e9c:    25 00              <unknown instruction>
 1e11e9e:    25 00              <unknown instruction>
 1e11ea0:    25 00              <unknown instruction>
 1e11ea2:    b4 01              <unknown instruction>
 1e11ea4:    80 00             	rts
 1e11ea6:    d9 01              <unknown instruction>
 1e11ea8:    25 00              <unknown instruction>
 1e11eaa:    25 00              <unknown instruction>
 1e11eac:    25 00              <unknown instruction>
 1e11eae:    25 00              <unknown instruction>
 1e11eb0:    25 00              <unknown instruction>
 1e11eb2:    25 00              <unknown instruction>
 1e11eb4:    25 00              <unknown instruction>
 1e11eb6:    25 00              <unknown instruction>
 1e11eb8:    25 00              <unknown instruction>
 1e11eba:    25 00              <unknown instruction>
 1e11ebc:    25 00              <unknown instruction>
 1e11ebe:    25 00              <unknown instruction>
 1e11ec0:    25 00              <unknown instruction>
 1e11ec2:    25 00              <unknown instruction>
 1e11ec4:    a2 00             	swi 2
 1e11ec6:    dd 00             	goto r13

; region 0x1e12226..0x1e1223e
 1e12226:    40 e0 32 02       	r0 = 562
 1e1222a:    d8 ed 98 20       	r2 = h[r9+r0<<1] (u)
 1e1222e:    80 14             	r1_r0 = 0
 1e12230:    43 21             	r3 = 1
 1e12232:    86 88             	goto -1520
 1e12234:    52 ee 90 55       	b[r9+80] = r5
 1e12238:    80 14             	r1_r0 = 0
 1e1223a:    6a 32             	r2 = 178
 1e1223c:    86 82             	goto -1532

; region 0x1e15602..0x1e15724
 1e15602:    50 ee 60 15       	r1 = b[r6+80] (u)
 1e15606:    01 f8 8a 00       	if (r1 == 0) goto 276
 1e1560a:    47 20             	r7 = 0
 1e1560c:    4a e0 e4 11       	r10 = 4580
 1e15610:    c5 ff cc 6e 00 00 	r5 = 28364
 1e15616:    4b e0 aa 00       	r11 = 170
 1e1561a:    4c e0 d4 20       	r12 = 8404
 1e1561e:    4d e0 02 21       	r13 = 8450
 1e15622:    44 20             	r4 = 0
 1e15624:    34 99             	goto 242
 1e15626:    b4 e0 90 04       	r0 = r9 + r4
 1e1562a:    60 18             	r0 += r6
 1e1562c:    d8 ee 00 0a       	r0 = b[r0+r10] (u)
 1e15630:    04 82             	goto 4
 1e15632:    50 ed 69 73       	h[r6+56] = r7
 1e15636:    50 ed 68 13       	r1 = h[r6+56] (u)
 1e1563a:    01 4e             	if (r1 == 0) goto 28
 1e1563c:    50 ed 68 23       	r2 = h[r6+56] (u)
 1e15640:    50 ed 68 13       	r1 = h[r6+56] (u)
 1e15644:    82 f8 12 02       	if (r2 != 1) goto 36
 1e15648:    1a 81             	r2 = r1 + 1
 1e1564a:    50 ed 69 23       	h[r6+56] = r2
 1e1564e:    d8 ee 11 05       	b[r1+r5] = r0
 1e15652:    80 f8 ee ab       	if (r0 != 85) goto -36
 1e15656:    24 9f             	goto 190
 1e15658:    90 f8 5d 54       	if (r0 != 170) goto 186
 1e1565c:    50 ed 68 03       	r0 = h[r6+56] (u)
 1e15660:    09 81             	r1 = r0 + 1
 1e15662:    50 ed 69 13       	h[r6+56] = r1
 1e15666:    d8 ee 01 b5       	b[r0+r5] = r11
 1e1566a:    24 95             	goto 170
 1e1566c:    50 ed 68 23       	r2 = h[r6+56] (u)
 1e15670:    2b 81             	r3 = r2 + 1
 1e15672:    50 ed 69 33       	h[r6+56] = r3
 1e15676:    d8 ee 21 05       	b[r2+r5] = r0
 1e1567a:    81 f9 4c 08       	if (r1 < 4) goto 152
 1e1567e:    50 ed 68 13       	r1 = h[r6+56] (u)
 1e15682:    58 61             	r0 = h[r5+2] (u)
 1e15684:    0a 86             	r2 = r0 + 6
 1e15686:    82 e8 46 10       	if (r1 != r2) goto 140
 1e1568a:    50 ed 69 73       	h[r6+56] = r7
 1e1568e:    09 84             	r1 = r0 + 4
 1e15690:    50 16             	r0 = r5
 1e15692:    bf ea 52 ff       	call -348
 1e15696:    59 61             	r1 = h[r5+2] (u)
 1e15698:    51 18             	r1 += r5
 1e1569a:    1a 45             	r2 = b[r1+5] (u)
 1e1569c:    19 44             	r1 = b[r1+4] (u)
 1e1569e:    a1 e1 20 24       	r1 <= insert(r2, p:8, l:8)
 1e156a2:    80 e8 0f 10       	if (r1 != r0) goto 30
 1e156a6:    58 44             	r0 = b[r5+4] (u)
 1e156a8:    f8 3f             	r0 += -1
 1e156aa:    00 fc 0e 0a       	if (r0 > 5) goto 28
 1e156ae:    00 01             	tbb [r0]
 1e156b0:    03 10             	r3 = b[r0++=r8] (u)
 1e156b2:    1b 1e             	r3 = r1 - r1
 1e156b4:    24 2b             	r4 = [sp+172]
 1e156b6:    b4 e0 80 2c       	r2 = r8 + r12
 1e156ba:    40 22             	r0 = 2
 1e156bc:    bf ea d4 b7       	call -36952
 1e156c0:    42 23             	r2 = 3
 1e156c2:    14 87             	goto 78
 1e156c4:    50 ed 69 73       	h[r6+56] = r7
 1e156c8:    14 86             	goto 76
 1e156ca:    12 e1 bc 86       	r2 = r8 + 5820
 1e156ce:    04 90             	goto 32
 1e156d0:    12 e1 0d 8f       	r2 = r8 + 7949
 1e156d4:    40 22             	r0 = 2
 1e156d6:    bf ea c7 b7       	call -36978
 1e156da:    d0 ec 64 1b       	r1 = [r6+180]
 1e156de:    01 5b             	if (r1 == 0) goto 54
 1e156e0:    40 20             	r0 = 0
 1e156e2:    c1 00             	call r1
 1e156e4:    04 98             	goto 48
 1e156e6:    12 e1 d8 8d       	r2 = r8 + 7640
 1e156ea:    04 82             	goto 4
 1e156ec:    12 e1 04 8e       	r2 = r8 + 7684
 1e156f0:    40 22             	r0 = 2
 1e156f2:    bf ea b9 b7       	call -37006
 1e156f6:    04 8f             	goto 30
 1e156f8:    12 e1 30 8e       	r2 = r8 + 7728
 1e156fc:    40 22             	r0 = 2
 1e156fe:    bf ea b3 b7       	call -37018
 1e15702:    42 25             	r2 = 5
 1e15704:    04 86             	goto 12
 1e15706:    b4 e0 80 2d       	r2 = r8 + r13
 1e1570a:    40 22             	r0 = 2
 1e1570c:    bf ea ac b7       	call -37032
 1e15710:    42 21             	r2 = 1
 1e15712:    8f ea de 6a       	call 2020796
 1e15716:    c4 21             	r4 += 1
 1e15718:    8e e8 85 41       	if (r4 != r14) goto -246
 1e1571c:    04 83             	goto 6
 1e1571e:    e1 16             	r1 = r14
 1e15720:    bf ea 6d e2       	call -15142

; region 0x1e19532..0x1e19566
 1e19532:    10 04             	[--sp] = rets
 1e19534:    e2 9f             	sp += -4
 1e19536:    de e9 03 00       	b[sp+3] = r0
 1e1953a:    89 83             	r1 = sp + 3
 1e1953c:    40 23             	r0 = 3
 1e1953e:    42 21             	r2 = 1
 1e19540:    71 89             	call -46
 1e19542:    c0 ff f0 42 00 00 	r0 = 17136
 1e19548:    41 ea 16 0d       	[r0+4] = 0x2580
 1e1954c:    40 20             	r0 = 0
 1e1954e:    02 81             	sp += 4
 1e19550:    00 04             	pc = [sp++]
 1e19552:    c1 ff f0 42 00 00 	r1 = 17136
 1e19558:    11 61             	r1 = [r1+4] 
 1e1955a:    42 20             	r2 = 0
 1e1955c:    82 6a             	[r0+40] = r2
 1e1955e:    82 6b             	[r0+44] = r2
 1e19560:    81 6c             	[r0+48] = r1
 1e19562:    82 6d             	[r0+52] = r2
 1e19564:    80 00             	rts

; region 0x1e195e8..0x1e1965c
 1e195e8:    78 44             	r0 = b[r7+4] (u)
 1e195ea:    80 f8 e2 03       	if (r0 != 1) goto -60
 1e195ee:    79 48             	r1 = b[r7+8] (u)
 1e195f0:    7a 47             	r2 = b[r7+7] (u)
 1e195f2:    a2 f1 20 14       	r2 <= insert(r1, p:8, l:8)  #
 1e195f6:    7b 46             		 r3 = b[r7+6] (u)
 1e195f8:    78 45             	r0 = b[r7+5] (u)
 1e195fa:    d0 ec a4 40       	r4 = [r10+4]
 1e195fe:    a0 e1 20 34       	r0 <= insert(r3, p:8, l:8)
 1e19602:    a0 e1 40 28       	r0 <= insert(r2, p:16, l:16)
 1e19606:    80 e8 1f 40       	if (r4 != r0) goto 62
 1e1960a:    00 e1 4c 65       	r0 = r6 + 1356
 1e1960e:    50 ec 08 20       	r3_r2 = d[r0+8]
 1e19612:    50 ec 00 00       	r1_r0 = d[r0+0]
 1e19616:    d0 e9 29 20       	d[sp+40] = r3_r2
 1e1961a:    d0 e9 21 00       	d[sp+32] = r1_r0
 1e1961e:    a8 80             	r0 = sp + 32
 1e19620:    80 ea d2 6d       	call 56228
 1e19624:    e7 86             	goto -116
 1e19626:    b4 e0 60 2b       	r2 = r6 + r11
 1e1962a:    40 22             	r0 = 2
 1e1962c:    bf ea 1c 98       	call -53192
 1e19630:    e7 80             	goto -128
 1e19632:    b4 e0 60 2c       	r2 = r6 + r12
 1e19636:    40 22             	r0 = 2
 1e19638:    bf ea 16 98       	call -53204
 1e1963c:    40 25             	r0 = 5
 1e1963e:    41 20             	r1 = 0
 1e19640:    42 20             	r2 = 0
 1e19642:    bf ea 67 ff       	call -306
 1e19646:    d7 95             	goto -150
 1e19648:    a4 16             	r4 = r10
 1e1964a:    d0 ec 47 00       	[++r4=4] = r0
 1e1964e:    41 94             	call -216
 1e19650:    40 21             	r0 = 1
 1e19652:    42 24             	r2 = 4
 1e19654:    41 16             	r1 = r4
 1e19656:    bf ea 5d ff       	call -326
 1e1965a:    d7 8b             	goto -170
